-- Business question: How many unique users played each business day?
-- Metric contract: One row per calendar day; active = at least one gameplay session; zero days included.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
SELECT c.day, COUNT(DISTINCT a.user_id) AS dau
FROM analytics.calendar c LEFT JOIN analytics.activity a USING(day)
GROUP BY c.day ORDER BY c.day;
