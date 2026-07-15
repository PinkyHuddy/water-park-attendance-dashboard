"""Build the Tableau-ready daily water park attendance analysis datasets."""

from __future__ import annotations

import os
from pathlib import Path

import holidays
import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RECEIPTS_PATH = PROJECT_ROOT / "data" / "cash_receipts.csv"
WEATHER_PATH = PROJECT_ROOT / "data" / "weather.csv"
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
PRIVATE_EXCLUDED_USER_PATH = PROJECT_ROOT / "data" / "private" / "excluded_receipt_user.txt"
DAILY_OUTPUT = OUTPUT_DIR / "water_park_daily_analysis.csv"
SUMMARY_OUTPUT = OUTPUT_DIR / "water_park_summary_metrics.csv"
GROUPED_OUTPUT = OUTPUT_DIR / "water_park_grouped_analysis.csv"

RECEIPT_COLUMNS = {
    "Receipt ID", "Date", "Time", "User", "Description", "Amount", "Is Refund", "Is Voided"
}
WEATHER_COLUMNS = {
    "dt_iso", "temp", "temp_min", "temp_max", "humidity", "wind_speed",
    "rain_1h", "weather_description",
}


def require_columns(frame: pd.DataFrame, required: set[str], source_name: str) -> None:
    """Raise a helpful error when a source does not contain required fields."""
    missing = sorted(required.difference(frame.columns))
    if missing:
        raise ValueError(f"{source_name} is missing required columns: {', '.join(missing)}")


def calculate_estimated_tickets(date_value: pd.Timestamp, amount: float, is_weekday: int) -> int:
    """Convert admission revenue to estimated tickets using documented historical prices."""
    if is_weekday == 1:
        return int(amount // 6.00)
    if date_value < pd.Timestamp("2019-07-05"):
        best_remainder = float("inf")
        best_count = 0
        for nine_dollar_tickets in range(int(amount // 9) + 2):
            remainder_after_nines = amount - nine_dollar_tickets * 9
            if remainder_after_nines < 0:
                continue
            eight_dollar_tickets = int(remainder_after_nines // 8)
            remainder = remainder_after_nines % 8
            if remainder < best_remainder:
                best_remainder = remainder
                best_count = eight_dollar_tickets + nine_dollar_tickets
        return best_count
    price = 9.00 if date_value < pd.Timestamp("2025-07-01") else 9.25
    return int(amount // price)


def prepare_receipts(path: Path = RECEIPTS_PATH) -> pd.DataFrame:
    """Clean receipt rows and aggregate estimated ticket sales by operating date."""
    receipts = pd.read_csv(path)
    require_columns(receipts, RECEIPT_COLUMNS, path.name)
    receipts = receipts.drop_duplicates().copy()
    receipts["date"] = pd.to_datetime(receipts["Date"], format="%b %d, %y", errors="coerce")
    receipts["hour"] = pd.to_datetime(receipts["Time"], format="%I:%M %p", errors="coerce").dt.hour
    receipts["amount"] = pd.to_numeric(receipts["Amount"], errors="coerce")
    receipts = receipts.dropna(subset=["Receipt ID", "date", "hour", "amount"])

    valid_receipt_ids = receipts.groupby("Receipt ID").filter(
        lambda group: group["Is Voided"].sum() == 0 and group["Is Refund"].sum() == 0
    )["Receipt ID"].unique()
    receipts = receipts[receipts["Receipt ID"].isin(valid_receipt_ids)].copy()
    excluded_user = os.getenv("WATER_PARK_EXCLUDED_RECEIPT_USER")
    if not excluded_user and PRIVATE_EXCLUDED_USER_PATH.exists():
        excluded_user = PRIVATE_EXCLUDED_USER_PATH.read_text(encoding="utf-8").strip()
    if excluded_user:
        receipts = receipts[receipts["User"].ne(excluded_user)].copy()
    receipts = receipts[receipts["Description"].ne("Journal Entry")].copy()

    receipts["is_weekday"] = (receipts["date"].dt.weekday < 5).astype(int)
    us_holidays = pd.DatetimeIndex(
        pd.to_datetime(list(holidays.UnitedStates(years=range(2018, 2027)).keys()))
    )
    receipts["is_holiday"] = receipts["date"].isin(us_holidays)
    weekend_or_holiday = (~receipts["is_weekday"].astype(bool) | receipts["is_holiday"]) & receipts["hour"].between(12, 17)
    weekday = receipts["is_weekday"].astype(bool) & receipts["hour"].between(14, 17)
    receipts = receipts[weekend_or_holiday | weekday].copy()
    in_season = (
        ((receipts["date"].dt.month == 5) & (receipts["date"].dt.day > 15))
        | receipts["date"].dt.month.isin([6, 7, 8])
    )
    receipts = receipts[in_season].copy()

    daily = receipts.groupby("date", as_index=False).agg(
        admission_revenue=("amount", "sum"),
        is_weekday=("is_weekday", "first"),
        is_holiday=("is_holiday", "first"),
        receipt_rows=("Receipt ID", "size"),
        distinct_receipts=("Receipt ID", "nunique"),
        first_receipt_hour=("hour", "min"),
        last_receipt_hour=("hour", "max"),
    )
    daily["actual_tickets"] = daily.apply(
        lambda row: calculate_estimated_tickets(row["date"], row["admission_revenue"], row["is_weekday"]),
        axis=1,
    )
    return daily


def _mode_or_missing(values: pd.Series) -> str | pd.NA:
    modes = values.dropna().mode()
    return modes.iloc[0] if not modes.empty else pd.NA


def prepare_weather(path: Path = WEATHER_PATH) -> pd.DataFrame:
    """Parse hourly weather and aggregate supported measures by local operating date."""
    weather = pd.read_csv(path)
    require_columns(weather, WEATHER_COLUMNS, path.name)
    weather = weather.drop_duplicates().copy()
    weather["timestamp"] = pd.to_datetime(
        weather["dt_iso"], format="%Y-%m-%d %H:%M:%S %z UTC", errors="coerce"
    )
    weather = weather.dropna(subset=["timestamp"])
    weather["timestamp"] = weather["timestamp"].dt.tz_convert("America/Los_Angeles")
    weather["date"] = weather["timestamp"].dt.tz_localize(None).dt.normalize()
    weather["hour"] = weather["timestamp"].dt.hour
    weather = weather[weather["hour"].between(11, 19)].copy()
    numeric_columns = ["temp", "temp_min", "temp_max", "humidity", "wind_speed", "rain_1h"]
    for column in numeric_columns:
        weather[column] = pd.to_numeric(weather[column], errors="coerce")

    # OpenWeather omits rain_1h when no rain object is reported; retain a flag documenting this convention.
    weather["rain_1h_reported"] = weather["rain_1h"].notna()
    weather["rain_1h_for_sum"] = weather["rain_1h"].fillna(0)
    hourly = weather.groupby(["date", "hour"], as_index=False).agg(
        temperature=("temp", "mean"),
        temperature_low=("temp_min", "min"),
        temperature_high=("temp_max", "max"),
        humidity=("humidity", "mean"),
        wind_speed=("wind_speed", "max"),
        precipitation=("rain_1h_for_sum", "mean"),
        precipitation_reported=("rain_1h_reported", "max"),
        weather_condition=("weather_description", _mode_or_missing),
    )
    return hourly.groupby("date", as_index=False).agg(
        temperature_high=("temperature_high", "max"),
        temperature_low=("temperature_low", "min"),
        average_temperature=("temperature", "mean"),
        precipitation=("precipitation", "sum"),
        precipitation_reported=("precipitation_reported", "max"),
        weather_condition=("weather_condition", _mode_or_missing),
        wind_speed=("wind_speed", "max"),
        humidity=("humidity", "mean"),
        weather_hour_count=("hour", "nunique"),
    )


def add_analysis_fields(daily: pd.DataFrame) -> pd.DataFrame:
    """Create calendar, attendance, rolling, and interpretable grouping fields."""
    analysis = daily.sort_values("date").reset_index(drop=True).copy()
    analysis["year"] = analysis["date"].dt.year
    analysis["month_number"] = analysis["date"].dt.month
    analysis["month_name"] = analysis["date"].dt.month_name()
    analysis["week_of_year"] = analysis["date"].dt.isocalendar().week.astype(int)
    analysis["day_of_month"] = analysis["date"].dt.day
    analysis["day_of_week"] = analysis["date"].dt.day_name()
    analysis["day_of_week_number"] = analysis["date"].dt.weekday + 1
    analysis["is_weekend"] = analysis["day_of_week_number"].isin([6, 7])
    analysis["season"] = np.select(
        [analysis["month_number"].isin([5, 6]), analysis["month_number"].eq(7)],
        ["Early season", "Peak season"],
        default="Late season",
    )
    season_open = pd.to_datetime(analysis["year"].astype(str) + "-05-16")
    season_close = pd.to_datetime(analysis["year"].astype(str) + "-08-31")
    analysis["days_since_season_open"] = (analysis["date"] - season_open).dt.days
    analysis["days_until_season_close"] = (season_close - analysis["date"]).dt.days
    analysis["precipitation_indicator"] = analysis["precipitation"].fillna(0).gt(0)
    analysis["temperature_band"] = pd.cut(
        analysis["temperature_high"],
        bins=[-np.inf, 75, 85, 95, np.inf],
        labels=["Below 75", "75 to 84", "85 to 94", "95 and above"],
        right=False,
    )
    analysis["temperature_band"] = analysis["temperature_band"].cat.add_categories(
        ["Missing"]
    ).fillna("Missing")
    analysis["seven_day_rolling_average"] = analysis["actual_tickets"].rolling(7, min_periods=1).mean()
    analysis["prior_operating_day_attendance"] = analysis["actual_tickets"].shift(1)
    analysis["attendance_change_from_prior_day"] = analysis["actual_tickets"].diff()
    analysis["attendance_percent_change_from_prior_day"] = (
        analysis["actual_tickets"].pct_change(fill_method=None).replace([np.inf, -np.inf], np.nan) * 100
    )
    ranked = analysis["actual_tickets"].rank(method="first")
    analysis["attendance_category"] = pd.qcut(
        ranked, q=4, labels=["Low", "Typical", "High", "Very High"]
    )
    analysis["operating_status"] = "Observed operating date"
    return analysis


def build_daily_dataset() -> pd.DataFrame:
    """Build and validate one analysis row per observed operating date."""
    receipts = prepare_receipts()
    weather = prepare_weather()
    daily = receipts.merge(weather, on="date", how="left", validate="one_to_one")
    analysis = add_analysis_fields(daily)
    if analysis["date"].duplicated().any():
        raise ValueError("Final daily dataset contains duplicate operating dates.")
    if analysis["actual_tickets"].lt(0).any():
        raise ValueError("Final daily dataset contains negative ticket estimates.")
    if not analysis["date"].is_monotonic_increasing:
        raise ValueError("Final daily dataset is not chronologically sorted.")
    return analysis


def build_summary_metrics(daily: pd.DataFrame) -> pd.DataFrame:
    """Create dashboard-level metrics in a simple long format."""
    weekday = daily.loc[~daily["is_weekend"], "actual_tickets"]
    weekend = daily.loc[daily["is_weekend"], "actual_tickets"]
    hot = daily.loc[daily["temperature_high"] >= 90, "actual_tickets"]
    cool = daily.loc[daily["temperature_high"] < 90, "actual_tickets"]
    rainy = daily.loc[daily["precipitation_indicator"], "actual_tickets"]
    dry = daily.loc[~daily["precipitation_indicator"], "actual_tickets"]
    busiest = daily.loc[daily["actual_tickets"].idxmax()]
    slowest = daily.loc[daily["actual_tickets"].idxmin()]
    metrics = {
        "total_operating_days": len(daily),
        "total_tickets": daily["actual_tickets"].sum(),
        "average_daily_tickets": daily["actual_tickets"].mean(),
        "median_daily_tickets": daily["actual_tickets"].median(),
        "minimum_daily_tickets": daily["actual_tickets"].min(),
        "maximum_daily_tickets": daily["actual_tickets"].max(),
        "busiest_date": busiest["date"].date().isoformat(),
        "slowest_date": slowest["date"].date().isoformat(),
        "average_weekday_attendance": weekday.mean(),
        "average_weekend_attendance": weekend.mean(),
        "weekend_attendance_difference": weekend.mean() - weekday.mean(),
        "average_hot_day_attendance": hot.mean(),
        "average_cool_day_attendance": cool.mean(),
        "average_rainy_day_attendance": rainy.mean(),
        "average_dry_day_attendance": dry.mean(),
        "number_of_missing_weather_days": daily["temperature_high"].isna().sum(),
    }
    return pd.DataFrame([{"metric": key, "value": value} for key, value in metrics.items()])


def build_grouped_analysis(daily: pd.DataFrame) -> pd.DataFrame:
    """Summarize dashboard dimensions with observation counts and descriptive statistics."""
    dimensions = {
        "day_of_week": "day_of_week",
        "month": "month_name",
        "weekend_status": "is_weekend",
        "holiday_status": "is_holiday",
        "temperature_range": "temperature_band",
        "precipitation_status": "precipitation_indicator",
        "attendance_category": "attendance_category",
    }
    frames = []
    for dimension_name, column in dimensions.items():
        grouped = daily.groupby(column, observed=True)["actual_tickets"].agg(
            observation_count="count", average_attendance="mean", median_attendance="median",
            minimum_attendance="min", maximum_attendance="max", standard_deviation="std",
        ).reset_index().rename(columns={column: "group_name"})
        grouped.insert(0, "group_dimension", dimension_name)
        grouped["small_sample_flag"] = grouped["observation_count"] < 5
        frames.append(grouped)
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    """Build all analytics outputs and print a concise processing summary."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    daily = build_daily_dataset()
    summary = build_summary_metrics(daily)
    grouped = build_grouped_analysis(daily)
    daily.to_csv(DAILY_OUTPUT, index=False, date_format="%Y-%m-%d")
    summary.to_csv(SUMMARY_OUTPUT, index=False)
    grouped.to_csv(GROUPED_OUTPUT, index=False)
    print(f"Built {len(daily):,} daily rows from {daily['date'].min().date()} through {daily['date'].max().date()}.")
    print(f"Weather missing for {daily['temperature_high'].isna().sum():,} daily rows.")
    print(f"Wrote: {DAILY_OUTPUT.relative_to(PROJECT_ROOT)}")
    print(f"Wrote: {SUMMARY_OUTPUT.relative_to(PROJECT_ROOT)}")
    print(f"Wrote: {GROUPED_OUTPUT.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
