-- Attendance by documented temperature bands.
SELECT temperature_band, COUNT(*) AS observations,
       ROUND(AVG(actual_tickets), 1) AS average_attendance,
       MIN(actual_tickets) AS minimum_attendance,
       MAX(actual_tickets) AS maximum_attendance
FROM water_park_daily_analysis
WHERE temperature_high IS NOT NULL
GROUP BY temperature_band
ORDER BY CASE temperature_band
    WHEN 'Below 75' THEN 1 WHEN '75 to 84' THEN 2
    WHEN '85 to 94' THEN 3 WHEN '95 and above' THEN 4 END;

-- Rainy versus dry attendance; counts expose the small rainy-day sample.
SELECT CASE WHEN precipitation_indicator = 1 THEN 'Rain reported' ELSE 'Dry' END AS precipitation_status,
       COUNT(*) AS observations, ROUND(AVG(actual_tickets), 1) AS average_attendance
FROM water_park_daily_analysis
GROUP BY precipitation_indicator;

-- Weather/calendar combinations with at least five observations.
WITH combinations AS (
    SELECT temperature_band,
           CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS weekend_status,
           precipitation_indicator,
           COUNT(*) AS observations,
           AVG(actual_tickets) AS average_attendance
    FROM water_park_daily_analysis
    GROUP BY temperature_band, is_weekend, precipitation_indicator
)
SELECT *, ROUND(average_attendance, 1) AS rounded_average_attendance
FROM combinations
WHERE observations >= 5
ORDER BY average_attendance DESC;
