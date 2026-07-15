# Water Park Attendance Analysis

## Overview

This project examines how weather, calendar conditions, and seasonal timing relate to daily water park demand. It converts transaction-level receipt records and hourly weather observations into a documented daily analysis dataset, then uses Python and SQL to identify operational patterns and prepare an interactive Tableau dashboard.

The attendance measure is estimated ticket sales derived from admission revenue and historical prices. It is a practical demand indicator, not a verified turnstile count. The project is intentionally focused on descriptive analytics and operational communication.

## Business Questions

- How is estimated attendance distributed across observed operating dates?
- Which weekdays and season periods correspond with higher or lower attendance?
- How do weekends compare with weekdays?
- How are temperature and reported precipitation associated with attendance?
- What patterns appear on holidays?
- Which dates were unusually busy or slow?
- How can these patterns inform cautious staffing and operating discussions?

## Dataset

The private inputs used locally are:

- `data/cash_receipts.csv`: 41,312 transaction rows across 516 source dates.
- `data/weather.csv`: 64,397 hourly weather rows.

These source files are intentionally excluded from the public repository because they contain private operational data. The receipt source includes transaction identifiers and internal user information. Reproducing the analysis requires authorized access to equivalent files matching the documented schemas.

The processing workflow filters voided and administrative receipt activity, applies the documented operating-hour and season rules, estimates ticket sales from revenue, aggregates weather to the operating date, and creates one row per observed operating date.

The final Tableau-ready dataset contains **416 dates from May 19, 2018 through July 26, 2025**. It includes six observed seasons; 2020 and 2021 are absent. Two attendance dates lack matched daily weather.

No PDF is stored in this repository, so the project does not currently claim independently verifiable extraction from a 2,600-page PDF. If that source is later added, its provenance can be documented here.

## Tools

- Python and pandas for extraction, cleaning, validation, and descriptive analysis
- Matplotlib for reproducible exploratory figures
- SQLite-compatible SQL for grouped analysis and quality checks
- Tableau for the interactive dashboard build

## Workflow

```text
Receipt records + hourly weather
        ↓
Validation and cleaning
        ↓
Daily ticket estimation and weather aggregation
        ↓
Calendar, rolling, and category fields
        ↓
Python and SQL descriptive analysis
        ↓
Tableau-ready CSVs and dashboard design
        ↓
Operational findings with documented limitations
```

## Analysis Outputs

- `water_park_daily_analysis.csv`: one row per observed operating date.
- `water_park_summary_metrics.csv`: dashboard KPI validation values.
- `water_park_grouped_analysis.csv`: grouped weekday, month, weekend, holiday, temperature, precipitation, and category summaries.
- `reports/figures/`: ten reproducible exploratory charts.
- `docs/analysis_findings.md`: calculated findings and cautious operational implications.
- `docs/data_quality_report.md`: issue counts, handling decisions, and limitations.

## Key Findings

- Average daily estimated ticket sales were **275.2**, with a median of **226**, across 416 observed dates.
- Weekends averaged **397.7 tickets across 170 dates**, compared with **190.5 across 246 weekdays**.
- Sunday had the highest weekday-level average at **401.3 tickets across 83 dates**; Tuesday had the lowest at **156.5 across 53 dates**.
- June had the highest monthly average at **312.1 tickets across 143 dates**.
- Dates with highs of at least 95°F averaged **338.8 tickets across 141 observations**. Daily high temperature had a modest correlation of **0.262** with attendance.
- Only 11 dates reported rain; they averaged **122.3 tickets**, compared with **279.3** across 405 dates without reported precipitation. The rainy-day sample is too small for a strong conclusion.
- Holidays averaged **549.4 tickets**, but only 16 holiday observations are available.

These values describe associations observed in this dataset. They do not establish causation or guarantee future attendance.

## Dashboard

**Water Park Attendance and Operations Dashboard**

The completed Tableau dashboard combines KPI cards with attendance trends, weekday and weekend comparisons, temperature analysis, precipitation context, and holiday patterns. The views are designed for descriptive operational analysis rather than causal or predictive claims.

**[Open the interactive dashboard on Tableau Public](https://public.tableau.com/app/profile/hudson.smith7339/viz/work_17840796637640/Dashboard1)**

The complete beginner-friendly build instructions are in [docs/tableau_dashboard_guide.md](docs/tableau_dashboard_guide.md).

## Operational Implications

- Historical weekend demand was substantially higher than weekday demand, suggesting that weekend staffing coverage and contingency plans deserve closer review.
- Holidays corresponded with higher attendance, but the dataset contains only 16 holiday observations. Managers could use this pattern as one input when reviewing voluntary availability, backup coverage, and callout contingencies rather than as an automatic staffing rule.
- Hotter days also corresponded with higher attendance. Staffing reviews for these dates should consider both potential demand and employee heat-safety needs, including adequate rotations, breaks, hydration, and backup coverage.
- The absence of observations for 2020 and 2021 prevents this dataset from measuring the operational effects of COVID-19. The gap instead highlights the value of business-continuity planning and consistent data collection during future disruptions.

These findings are descriptive and should be combined with capacity requirements, labor policies, employee availability, weather forecasts, and managerial judgment before staffing decisions are made.

## Limitations

- Ticket sales are inferred from revenue rather than measured directly.
- The daily dataset contains 416 observations, and many comparison groups are much smaller.
- No closure, partial-day, staffing, promotion, special-event, or school-calendar fields are available.
- Rain and holiday samples are limited.
- Two dates lack matched weather.
- Observed dates may omit closed or missing-record days.
- Descriptive relationships are not causal and may not generalize to future seasons.
- The available data supports descriptive analysis but not precise future-demand estimates.

## Repository Structure

```text
data/
├── cash_receipts.csv                    # immutable raw receipt source
├── weather.csv                          # immutable raw weather source
└── processed/                           # generated Tableau-ready outputs
docs/
├── analysis_findings.md
├── data_quality_report.md
└── tableau_dashboard_guide.md
reports/figures/                         # generated descriptive charts
scripts/
├── build_analysis_dataset.py
└── run_exploratory_analysis.py
sql/                                     # analysis and quality-check queries
tests/test_analysis_dataset.py
```

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Place authorized source files at `data/cash_receipts.csv` and `data/weather.csv`. If an administrative receipt account must be excluded, provide its name only in the local environment:

```bash
export WATER_PARK_EXCLUDED_RECEIPT_USER="private account name"
```

Build the processed datasets:

```bash
python3 scripts/build_analysis_dataset.py
```

Generate exploratory figures:

```bash
MPLBACKEND=Agg python3 scripts/run_exploratory_analysis.py
```

Run validation tests:

```bash
python3 -m unittest discover -s tests -v
```

The SQL files are SQLite-compatible. After importing the daily CSV into the `water_park_daily_analysis` table, run the queries under `sql/` in numerical or topic order.

## Future Improvements

Continue collecting direct turnstile attendance, additional seasons, staffing levels, hourly attendance, revenue by product, special events, promotions, school-calendar information, closures, and consistent precipitation measurements. These additions would make future operational comparisons more reliable and actionable.

## Authorship Note

This project was designed and implemented by Hudson, with AI-assisted support used selectively for documentation, validation, and development acceleration.
