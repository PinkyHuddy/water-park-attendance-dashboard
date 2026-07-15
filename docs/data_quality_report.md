# Data Quality Report

## Scope

This audit covers the immutable raw inputs `data/cash_receipts.csv` and `data/weather.csv`. The resulting analysis table contains 416 observed operating dates from May 19, 2018 through July 26, 2025. Ticket counts are estimates derived from admission revenue and historical prices; they are not direct turnstile attendance counts.

## Issue Register

| Issue | Affected rows | Handling | Rationale |
|---|---:|---|---|
| Voided receipt rows | 413 raw rows | Excluded all rows belonging to a receipt ID with a void flag | Voided transactions do not represent completed sales. |
| Refund indicator has no variation | 41,312 rows are marked non-refund | Retained and documented | The source provides no positive refund examples; refund completeness cannot be independently verified. |
| Zero-amount receipt rows | 410 raw rows | Retained unless removed by an existing void/admin rule | A zero amount can reflect a valid record; it is not silently treated as an error. |
| Administrative records | Rows attributed to a designated administrative account or described as `Journal Entry` | Excluded using the established source-processing rule | These records are not treated as customer admission activity. The account name is private and supplied locally through configuration. |
| Admission counts are inferred | All 416 daily rows | Labeled and documented as estimated ticket sales | Revenue is divided by date-dependent admission prices; the source lacks direct ticket quantities. |
| Zero-ticket operating dates | 3 daily rows | Retained and flagged for review | The source does not establish whether these are closures, partial days, or valid low-activity records. |
| High attendance outliers | 12 daily rows above the 1.5-IQR upper bound of 763 tickets | Retained | Holiday and weekend peaks may be legitimate. Removing them would distort descriptive analysis. |
| Duplicate raw weather timestamps | 509 repeated timestamps | Aggregated to one local date/hour row using numeric summaries and the modal condition | This preserves supported measurements without arbitrarily deleting an observation. |
| Missing daily weather match | 2 daily rows | Retained with null weather fields | Attendance information remains valid; weather is not invented. |
| Missing `wind_gust` | 34,982 raw weather rows | Not included in the main daily dataset | Missingness is too extensive for a reliable dashboard measure. |
| Entirely missing weather fields | `sea_level`, `grnd_level`, `rain_3h`, `snow_1h`, and `snow_3h` | Excluded | These fields contain no usable observations. |
| Missing `rain_1h` | 59,467 raw weather rows | Interpreted as no reported rain when aggregating precipitation; `precipitation_reported` preserves whether rain was explicitly present | OpenWeather commonly omits the rain object when no rain is reported. This convention is documented rather than hidden. |
| Daily weather condition is categorical | 13 raw labels | Uses the modal operating-hour label | A mode is more representative than selecting the first hourly label, but it still simplifies within-day changes. |
| Closed and missing days are indistinguishable | Unknown | Dataset includes only dates with qualifying receipt activity | No operating calendar or closure log exists. No closed-day rows are manufactured. |
| Partial days and special events | Unknown | No indicators created | The source does not reliably support these fields. |
| Exact duplicate source rows | 0 in each raw CSV | Generic duplicate removal remains in the script | Defensive validation without changing current data. |
| Invalid receipt dates | 0 | Parser fails rows to null, then excludes invalid required records | Required timestamps must be valid for daily aggregation. |
| Negative ticket estimates | 0 | Build fails if any are produced | Negative attendance is invalid. |

## Attendance Outlier Context

Daily estimated ticket sales range from 0 to 1,152. The median is 226 and the mean is 275.2, indicating a right-skewed distribution. The 1.5-IQR review threshold is 763 tickets. Twelve rows exceed that threshold, including July 4 and Memorial Day observations. These values remain in the analysis because calendar context suggests that at least some are plausible high-demand days.

## Category Definitions

Attendance categories are quantile-based and contain 104 observations each:

- **Low:** estimated tickets ranked in the lowest quartile (observed range 0–126).
- **Typical:** second quartile (127–225).
- **High:** third quartile (227–381).
- **Very High:** highest quartile (382–1,152).

Ranking with deterministic tie handling is used so all four groups remain equal in size. Categories describe this dataset only and are not universal operating thresholds.

Temperature bands use documented dashboard thresholds:

- Below 75°F
- 75°F to 84.99°F
- 85°F to 94.99°F
- 95°F and above

## Unsupported Fields

The source does not reliably support closure reasons, special-event indicators, staffing, promotions, school calendars, verified attendance, or partial-day status. These fields are not invented.

## Reproducibility

Run `python3 scripts/build_analysis_dataset.py` to rebuild all processed CSVs. The script validates required columns, date parsing, chronological order, unique operating dates, and nonnegative ticket estimates. Additional checks are in `tests/test_analysis_dataset.py` and `sql/quality_checks.sql`.
