"""Generate descriptive attendance-analysis figures from the processed daily dataset."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "processed" / "water_park_daily_analysis.csv"
FIGURE_DIR = PROJECT_ROOT / "reports" / "figures"
COLOR = "#2F6690"
ACCENT = "#D98E04"


def save_figure(fig: plt.Figure, filename: str) -> None:
    """Apply consistent spacing, save a figure, and close it."""
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / filename, dpi=160, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    """Create the reproducible chart set used by the analysis and Tableau guide."""
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    data = pd.read_csv(DATA_PATH, parse_dates=["date"])
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(data["date"], data["actual_tickets"], color=COLOR, alpha=0.45, label="Daily estimated tickets")
    ax.plot(data["date"], data["seven_day_rolling_average"], color=ACCENT, linewidth=2, label="7-operating-day average")
    ax.set(title=f"Estimated Ticket Sales Over Time (n={len(data)})", xlabel="Operating date", ylabel="Estimated tickets")
    ax.legend()
    save_figure(fig, "attendance_over_time.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(data["actual_tickets"], bins=20, color=COLOR, edgecolor="white")
    ax.axvline(data["actual_tickets"].median(), color=ACCENT, linestyle="--", label=f"Median: {data['actual_tickets'].median():.0f}")
    ax.set(title=f"Distribution of Daily Estimated Ticket Sales (n={len(data)})", xlabel="Estimated tickets", ylabel="Operating days")
    ax.legend()
    save_figure(fig, "attendance_distribution.png")

    weekday = data.groupby("day_of_week")["actual_tickets"].agg(["mean", "count"]).reindex(weekday_order)
    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(weekday.index, weekday["mean"], color=COLOR)
    for bar, count in zip(bars, weekday["count"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"n={count}", ha="center", va="bottom", fontsize=8)
    ax.set(title="Average Estimated Ticket Sales by Weekday", xlabel="Day of week", ylabel="Average estimated tickets")
    ax.tick_params(axis="x", rotation=25)
    save_figure(fig, "attendance_by_weekday.png")

    weekend = data.groupby("is_weekend")["actual_tickets"].agg(["mean", "median", "count"])
    fig, ax = plt.subplots(figsize=(7, 5))
    labels = ["Weekday", "Weekend"]
    bars = ax.bar(labels, weekend.reindex([False, True])["mean"], color=[COLOR, ACCENT])
    for bar, count in zip(bars, weekend.reindex([False, True])["count"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"n={count}", ha="center", va="bottom")
    ax.set(title="Weekend Versus Weekday Attendance", ylabel="Average estimated tickets")
    save_figure(fig, "weekend_comparison.png")

    weather_data = data.dropna(subset=["temperature_high"])
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = weather_data["is_weekend"].map({False: COLOR, True: ACCENT})
    ax.scatter(weather_data["temperature_high"], weather_data["actual_tickets"], c=colors, alpha=0.65)
    ax.set(title=f"Attendance and Daily High Temperature (n={len(weather_data)})", xlabel="High temperature (°F)", ylabel="Estimated tickets")
    save_figure(fig, "attendance_vs_temperature.png")

    temperature = data.groupby("temperature_band", observed=True)["actual_tickets"].agg(["mean", "count"])
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(temperature.index.astype(str), temperature["mean"], color=COLOR)
    for bar, count in zip(bars, temperature["count"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"n={count}", ha="center", va="bottom")
    ax.set(title="Average Attendance by Temperature Band", xlabel="Daily high temperature band (°F)", ylabel="Average estimated tickets")
    save_figure(fig, "attendance_by_temperature_band.png")

    precipitation = data.groupby("precipitation_indicator")["actual_tickets"].agg(["mean", "count"]).reindex([False, True])
    fig, ax = plt.subplots(figsize=(7, 5))
    bars = ax.bar(["Dry", "Rain reported"], precipitation["mean"], color=[COLOR, ACCENT])
    for bar, count in zip(bars, precipitation["count"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"n={count}", ha="center", va="bottom")
    ax.set(title="Attendance by Precipitation Status", ylabel="Average estimated tickets")
    save_figure(fig, "attendance_by_precipitation.png")

    month = data.groupby(["month_number", "month_name"])["actual_tickets"].agg(["mean", "count"]).reset_index().sort_values("month_number")
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(month["month_name"], month["mean"], color=COLOR)
    for bar, count in zip(bars, month["count"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(), f"n={count}", ha="center", va="bottom")
    ax.set(title="Average Attendance Through the Operating Season", xlabel="Month", ylabel="Average estimated tickets")
    save_figure(fig, "attendance_by_month.png")

    fig, ax = plt.subplots(figsize=(10, 5))
    values = [data.loc[data["day_of_week"] == day, "actual_tickets"] for day in weekday_order]
    ax.boxplot(values, tick_labels=weekday_order, showfliers=True)
    ax.set(title="Attendance Variation by Weekday", xlabel="Day of week", ylabel="Estimated tickets")
    ax.tick_params(axis="x", rotation=25)
    save_figure(fig, "attendance_weekday_boxplot.png")

    ranked = pd.concat([data.nsmallest(10, "actual_tickets"), data.nlargest(10, "actual_tickets")]).sort_values("actual_tickets")
    fig, ax = plt.subplots(figsize=(9, 7))
    labels = ranked["date"].dt.strftime("%Y-%m-%d")
    ax.barh(labels, ranked["actual_tickets"], color=[COLOR] * 10 + [ACCENT] * 10)
    ax.set(title="Ten Lowest and Ten Highest Attendance Dates", xlabel="Estimated tickets", ylabel="Operating date")
    save_figure(fig, "highest_and_lowest_days.png")

    print(f"Generated 10 figures in {FIGURE_DIR.relative_to(PROJECT_ROOT)}.")


if __name__ == "__main__":
    main()
