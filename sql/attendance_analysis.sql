-- Overall distribution and average attendance by weekday.
SELECT day_of_week, day_of_week_number, COUNT(*) AS observations,
       ROUND(AVG(actual_tickets), 1) AS average_attendance,
       MIN(actual_tickets) AS minimum_attendance,
       MAX(actual_tickets) AS maximum_attendance
FROM water_park_daily_analysis
GROUP BY day_of_week, day_of_week_number
ORDER BY day_of_week_number;

-- Weekend versus weekday attendance.
SELECT CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS weekend_status,
       COUNT(*) AS observations, ROUND(AVG(actual_tickets), 1) AS average_attendance
FROM water_park_daily_analysis
GROUP BY is_weekend;

-- Top and bottom ten observed days using window-function ranking.
WITH ranked AS (
    SELECT date, day_of_week, actual_tickets, temperature_high, precipitation,
           RANK() OVER (ORDER BY actual_tickets DESC) AS busiest_rank,
           RANK() OVER (ORDER BY actual_tickets ASC) AS slowest_rank
    FROM water_park_daily_analysis
)
SELECT * FROM ranked
WHERE busiest_rank <= 10 OR slowest_rank <= 10
ORDER BY actual_tickets DESC;

-- Seven-observation rolling average and operating-day change.
SELECT date, actual_tickets,
       ROUND(AVG(actual_tickets) OVER (
           ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
       ), 1) AS seven_operating_day_average,
       actual_tickets - LAG(actual_tickets) OVER (ORDER BY date) AS change_from_prior_operating_day
FROM water_park_daily_analysis
ORDER BY date;
