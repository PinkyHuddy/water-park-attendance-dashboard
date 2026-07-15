# Tableau Dashboard Guide

## Setup

Connect Tableau to `data/processed/water_park_daily_analysis.csv`. Confirm that `date` is a Date, attendance and weather fields are numeric, and Boolean fields are dimensions. Use **Water Park Attendance and Operations Dashboard** as the title and a fixed desktop size near 1,300 × 850 pixels.

This dataset contains estimated ticket sales, not verified turnstile attendance. Add that statement to the dashboard subtitle.

## 1. KPI Cards

Create separate text worksheets and place them in a horizontal container.

| KPI | Field and aggregation | Format | Tooltip |
|---|---|---|---|
| Operating Days | `COUNTD(date)` | Whole number | “Number of observed operating dates in the current filters.” |
| Total Attendance | `SUM(actual_tickets)` | Whole number with separators | “Total estimated ticket sales across selected dates.” |
| Average Daily Attendance | `AVG(actual_tickets)` | One decimal | “Average estimated ticket sales per observed date.” |
| Median Daily Attendance | `MEDIAN(actual_tickets)` | Whole number | “Median estimated ticket sales per observed date.” |
| Busiest Date | Put `date` on Text after filtering to the maximum | `MMM d, yyyy` | Include date and maximum tickets. |
| Highest Attendance | `MAX(actual_tickets)` | Whole number | “Highest observed daily estimate.” |
| Weekend Difference | Calculated field below | One decimal | “Weekend average minus weekday average in the current filters.” |

Weekend difference calculated field:

```text
{ FIXED : AVG(IF [is_weekend] THEN [actual_tickets] END) }
-
{ FIXED : AVG(IF NOT [is_weekend] THEN [actual_tickets] END) }
```

If filters should affect this fixed calculation, add them to Context.

## 2. Attendance Over Time

1. Drag continuous `date` to Columns.
2. Drag `actual_tickets` to Rows and use SUM because each date is unique.
3. Drag `seven_day_rolling_average` to Rows and use AVG.
4. Select Dual Axis, synchronize the axes, and hide the second header.
5. Use a muted blue daily line and a thicker orange rolling-average line.

Tooltip: `Date: <date>`, `Estimated tickets: <actual_tickets>`, `7-operating-day average: <seven_day_rolling_average>`, `Weekday: <day_of_week>`, `High temperature: <temperature_high>°F`.

The provided rolling value covers seven observed operating dates, not seven consecutive calendar days.

## 3. Attendance by Weekday

1. Drag `day_of_week` to Columns and `AVG(actual_tickets)` to Rows.
2. Sort using `day_of_week_number`, ascending.
3. Put `COUNTD(date)` on Detail and in the tooltip.
4. Label bars with the average; keep counts in the tooltip to avoid clutter.

Tooltip: `Day`, `Average estimated tickets`, `Median estimated tickets`, and `Observed dates`. Note that sample sizes differ by weekday.

## 4. Weekend Versus Weekday

A boxplot is preferable because it shows the distribution and outliers, not only two means.

1. Drag `is_weekend` to Columns and rename aliases to Weekday/Weekend.
2. Drag `actual_tickets` to Rows.
3. Use Show Me → Box-and-Whisker Plot.
4. Add `AVG(actual_tickets)`, `MEDIAN(actual_tickets)`, and `COUNTD(date)` to the tooltip.

## 5. Attendance Versus Temperature

1. Put `temperature_high` on Columns and `actual_tickets` on Rows.
2. Place `date` on Detail, `is_weekend` on Color, and optionally `attendance_category` on Shape.
3. Add a linear trend line through the Analytics pane.
4. State in the caption that the trend is descriptive and not causal.

Tooltip: date, estimated tickets, high/average temperature, weather condition, precipitation, weekend status, and holiday status.

## 6. Temperature-Band Analysis

Use the existing `temperature_band` field and manually sort it:

1. Below 75
2. 75 to 84
3. 85 to 94
4. 95 and above

Place the band on Columns and `AVG(actual_tickets)` on Rows. Add `COUNTD(date)` to Detail and tooltip. The Below 75°F group has only 11 observations, so display its count prominently.

## 7. Precipitation Analysis

1. Put `precipitation_indicator` on Columns and alias values as Dry and Rain Reported.
2. Put `AVG(actual_tickets)` on Rows.
3. Add `COUNTD(date)` to labels or tooltip.

Tooltip: precipitation status, average and median tickets, observed dates, and average precipitation. Add a visible note that only 11 dates report rain.

## 8. Holiday Analysis

Use a bar chart with `is_holiday` on Columns and `AVG(actual_tickets)` on Rows. Add `COUNTD(date)` and `MEDIAN(actual_tickets)` to the tooltip. Label the holiday count because only 16 holiday observations are available.

## 9. Attendance Distribution

Create `Attendance Bin` from `actual_tickets` with a bin size of 50. Put the bin on Columns and `COUNTD(date)` on Rows. Add a reference line at the median of 226. Use the chart to discuss skew and high-demand dates, not to define universal capacity thresholds.

## 10. Highest and Lowest Days

Create two ranked tables or a parameter-controlled table containing:

- `date`
- `actual_tickets`
- `day_of_week`
- `temperature_high`
- `precipitation`
- `is_holiday`
- `attendance_category`

Use a Top 10 filter by `SUM(actual_tickets)` for the busiest table and Bottom 10 for the slowest table. Tooltip: “Estimated ticket sales are revenue-derived; investigate closure and event context before acting on an individual date.”

## Dashboard Filters

Add these filters and apply them to all worksheets using the daily source:

- Date range
- Month name, sorted by month number
- Day of week, sorted by day number
- Weekend status
- Holiday status
- Temperature band
- Precipitation status
- Attendance category

Use Context filters when they must affect fixed KPI calculations.

## Recommended Layout

- Top: title, subtitle, and KPI cards.
- Second row: full-width attendance-over-time chart.
- Third row: weekday bars and temperature scatterplot.
- Fourth row: weekend distribution, precipitation bars, and holiday bars.
- Bottom: highest/lowest dates and a limitations note.

Use one blue sequential palette plus an orange highlight. Avoid pie charts, 3D effects, decorative graphics, excessive labels, and red-green-only encodings.

## Publishing Checklist

- Verify all worksheet counts against `water_park_summary_metrics.csv` and `water_park_grouped_analysis.csv`.
- Keep “estimated ticket sales” in titles or subtitles.
- Include sample counts in every grouped tooltip.
- Add the data-limitations note from `docs/analysis_findings.md`.
- Export a dashboard screenshot to `reports/` after construction.
- Add the Tableau Public URL to the README only after it is actually published.
