"""Validation tests for the Tableau-ready daily analysis outputs."""

from __future__ import annotations

import unittest

import numpy as np
import pandas as pd

from scripts.build_analysis_dataset import (
    DAILY_OUTPUT,
    GROUPED_OUTPUT,
    RECEIPTS_PATH,
    SUMMARY_OUTPUT,
    WEATHER_PATH,
    build_daily_dataset,
)


class AnalysisDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.saved = pd.read_csv(DAILY_OUTPUT, parse_dates=["date"])
        cls.can_rebuild = RECEIPTS_PATH.exists() and WEATHER_PATH.exists()
        cls.data = build_daily_dataset() if cls.can_rebuild else cls.saved.copy()
        cls.summary = pd.read_csv(SUMMARY_OUTPUT)
        cls.grouped = pd.read_csv(GROUPED_OUTPUT)

    def test_required_columns(self) -> None:
        required = {
            "date", "actual_tickets", "day_of_week", "day_of_week_number", "is_weekend",
            "is_holiday", "attendance_category", "seven_day_rolling_average",
            "temperature_high", "precipitation_indicator",
        }
        self.assertTrue(required.issubset(self.data.columns))

    def test_one_row_per_operating_date(self) -> None:
        self.assertEqual(len(self.data), self.data["date"].nunique())

    def test_chronological_order_and_valid_dates(self) -> None:
        self.assertFalse(self.data["date"].isna().any())
        self.assertTrue(self.data["date"].is_monotonic_increasing)

    def test_no_exact_duplicates_or_negative_tickets(self) -> None:
        self.assertEqual(int(self.data.duplicated().sum()), 0)
        self.assertTrue(self.data["actual_tickets"].ge(0).all())

    def test_weekend_indicators(self) -> None:
        expected = self.data["date"].dt.weekday.ge(5)
        pd.testing.assert_series_equal(
            self.data["is_weekend"].reset_index(drop=True), expected.reset_index(drop=True),
            check_names=False,
        )

    def test_rolling_average(self) -> None:
        expected = self.data["actual_tickets"].rolling(7, min_periods=1).mean()
        np.testing.assert_allclose(self.data["seven_day_rolling_average"], expected)

    def test_attendance_categories(self) -> None:
        self.assertFalse(self.data["attendance_category"].isna().any())
        self.assertEqual(
            set(self.data["attendance_category"].astype(str)),
            {"Low", "Typical", "High", "Very High"},
        )

    def test_no_infinite_numeric_values(self) -> None:
        numeric = self.data.select_dtypes(include="number")
        self.assertFalse(np.isinf(numeric.to_numpy()).any())

    def test_saved_output_matches_rebuild(self) -> None:
        if not self.can_rebuild:
            self.skipTest("Private raw sources are not available in the public repository.")
        self.assertEqual(len(self.saved), len(self.data))
        self.assertEqual(int(self.saved["actual_tickets"].sum()), int(self.data["actual_tickets"].sum()))

    def test_summary_metrics_match_daily_data(self) -> None:
        metrics = self.summary.set_index("metric")["value"]
        self.assertEqual(int(float(metrics["total_operating_days"])), len(self.saved))
        self.assertEqual(int(float(metrics["total_tickets"])), int(self.saved["actual_tickets"].sum()))
        self.assertAlmostEqual(float(metrics["average_daily_tickets"]), self.saved["actual_tickets"].mean())

    def test_group_counts_match_daily_observations(self) -> None:
        for dimension in self.grouped["group_dimension"].unique():
            subset = self.grouped[self.grouped["group_dimension"] == dimension]
            self.assertEqual(int(subset["observation_count"].sum()), len(self.saved))


if __name__ == "__main__":
    unittest.main()
