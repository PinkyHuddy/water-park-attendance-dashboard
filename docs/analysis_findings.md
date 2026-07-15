# Attendance Analysis Findings

## Executive Summary

The analysis contains 416 observed operating dates from May 19, 2018 through July 26, 2025. Daily estimated ticket sales averaged 275.2 and had a median of 226. Weekend dates, hotter days, holidays, and the middle of the operating season corresponded with higher attendance in this dataset. These are descriptive associations, not causal results.

## Main Attendance Patterns

- Total estimated tickets across observed dates: **114,463**.
- Average per observed date: **275.2**; median: **226**.
- Daily values ranged from **0 to 1,152**.
- The distribution is right-skewed: a small number of high-volume dates raise the mean above the median.
- The median absolute change between consecutive observed operating dates was **129 tickets**, showing substantial day-to-day volatility.

## Calendar Patterns

Weekend attendance averaged **397.7 tickets across 170 dates**, compared with **190.5 across 246 weekdays**. The observed weekend difference was **207.2 tickets**, or approximately **108.7% above the weekday average**.

Sunday had the highest weekday-level average at **401.3 tickets across 83 dates**, followed by Saturday at **394.2 across 87 dates**. Tuesday had the lowest average at **156.5 across 53 dates**.

Holiday dates averaged **549.4 tickets across only 16 observations**, compared with **264.2 across 400 non-holidays**. The holiday sample is small and includes high-demand dates such as July 4 and Memorial Day, so it should be interpreted cautiously.

## Seasonal Patterns

- June: **312.1 average tickets**, 143 dates.
- July: **284.2 average tickets**, 164 dates.
- May: **229.9 average tickets**, 42 dates.
- August: **202.5 average tickets**, 67 dates.

June had the highest observed monthly average. Differences may reflect the operating calendar, weekday mix, holidays, weather, and unrecorded events—not month alone.

## Weather-Related Patterns

Daily high temperature had a modest positive correlation of **0.262** with estimated tickets. Correlation does not establish causation and may partly reflect seasonal and weekend patterns.

Temperature-band results were:

| High-temperature band | Dates | Average tickets |
|---|---:|---:|
| Below 75°F | 11 | 92.7 |
| 75–84°F | 83 | 224.7 |
| 85–94°F | 179 | 260.5 |
| 95°F and above | 141 | 338.8 |

Rain was reported on only **11 dates**, which averaged **122.3 tickets**. The remaining 405 dates averaged **279.3**. The rainy-day sample is too small for a strong general conclusion, but the observed difference is operationally worth monitoring as more data is collected.

## High- and Low-Demand Dates

The busiest observed date was **July 4, 2024**, with an estimated **1,152 tickets**. Other high dates included Memorial Day 2018 and several June or July weekends and holidays.

Three dates had zero estimated tickets: May 20, 2019; August 15, 2022; and August 22, 2024. Without closure or partial-day records, these values cannot be classified confidently and remain flagged for review.

## Operational Implications

- Review staffing coverage for weekends, especially Saturdays and Sundays, which had materially higher historical attendance than weekdays.
- Treat holidays as potential high-demand dates while recognizing the sample contains only 16 observations.
- Use temperature and precipitation as contextual planning inputs rather than deterministic staffing rules.
- Monitor June closely; it had the highest average attendance among observed months.
- Maintain flexibility because operating-day attendance changes were volatile and unrecorded events may explain individual peaks.
- Do not automate staffing decisions from this dataset alone.

## Data Limitations

- Ticket counts are inferred from revenue rather than measured directly.
- Only 416 observed dates across six seasons are available; the effective sample for many groups is much smaller.
- There are no 2020 or 2021 observations.
- Closure, partial-day, promotion, special-event, staffing, and school-calendar information is unavailable.
- Two daily attendance rows lack matched weather.
- Rain and holiday samples are small.
- Observed dates may omit closed or missing-record days.
- Relationships are descriptive and may not generalize to future seasons.
- The dataset is intended for descriptive operational analysis rather than precise future-demand estimates.

## Suggested Future Data Collection

Collect direct turnstile attendance, operating and closure status, staffing by role and shift, hourly attendance, revenue by product, promotions, special events, school calendars, capacity constraints, and consistently measured precipitation. Use the additional data to strengthen future operational comparisons.
