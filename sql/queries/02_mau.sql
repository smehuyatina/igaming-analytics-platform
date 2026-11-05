-- Business question: How many unique users played each month?
-- Metric contract: Unique gameplay users in each calendar month; do not sum DAU.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
SELECT date_trunc('month',c.day)::date AS month, COUNT(DISTINCT a.user_id) AS mau
FROM analytics.calendar c LEFT JOIN analytics.activity a USING(day)
GROUP BY 1 ORDER BY 1;
