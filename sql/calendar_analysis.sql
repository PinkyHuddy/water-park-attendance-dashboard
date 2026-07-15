-- Monthly attendance with sample sizes.
SELECT month_number, month_name, COUNT(*) AS observations,
       ROUND(AVG(actual_tickets), 1) AS average_attendance
FROM water_park_daily_analysis
GROUP BY month_number, month_name
ORDER BY month_number;

-- Holiday comparison; interpret cautiously because the holiday sample is small.
SELECT CASE WHEN is_holiday = 1 THEN 'Holiday' ELSE 'Non-holiday' END AS holiday_status,
       COUNT(*) AS observations, ROUND(AVG(actual_tickets), 1) AS average_attendance
FROM water_park_daily_analysis
GROUP BY is_holiday;

-- Season phase and weekend conditional aggregation.
SELECT season, COUNT(*) AS observations,
       ROUND(AVG(actual_tickets), 1) AS average_attendance,
       ROUND(AVG(CASE WHEN is_weekend = 1 THEN actual_tickets END), 1) AS weekend_average,
       ROUND(AVG(CASE WHEN is_weekend = 0 THEN actual_tickets END), 1) AS weekday_average
FROM water_park_daily_analysis
GROUP BY season
ORDER BY MIN(days_since_season_open);
