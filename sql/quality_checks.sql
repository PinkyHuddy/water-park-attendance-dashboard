-- Expected result: zero duplicate dates.
SELECT date, COUNT(*) AS row_count
FROM water_park_daily_analysis
GROUP BY date
HAVING COUNT(*) > 1;

-- Missing-value counts for essential and weather fields.
SELECT COUNT(*) AS total_rows,
       SUM(CASE WHEN date IS NULL THEN 1 ELSE 0 END) AS missing_dates,
       SUM(CASE WHEN actual_tickets IS NULL THEN 1 ELSE 0 END) AS missing_attendance,
       SUM(CASE WHEN temperature_high IS NULL THEN 1 ELSE 0 END) AS missing_temperature,
       SUM(CASE WHEN weather_condition IS NULL THEN 1 ELSE 0 END) AS missing_weather_condition
FROM water_park_daily_analysis;

-- Invalid or questionable attendance observations for review, not automatic deletion.
SELECT date, actual_tickets, day_of_week, operating_status
FROM water_park_daily_analysis
WHERE actual_tickets <= 0 OR actual_tickets > 763
ORDER BY actual_tickets;

-- Validate calendar flags and category values.
SELECT * FROM water_park_daily_analysis
WHERE is_weekend NOT IN (0, 1)
   OR is_holiday NOT IN (0, 1)
   OR attendance_category NOT IN ('Low', 'Typical', 'High', 'Very High')
   OR actual_tickets < 0;
