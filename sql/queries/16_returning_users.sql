-- Business question: How many monthly players returned after at least 30 days without gameplay?
-- Metric contract: Return = gap >=31 days between distinct active dates; first-ever gameplay excluded. Not proof of marketing impact.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
WITH gaps AS (
 SELECT user_id,day,day-LAG(day) OVER (PARTITION BY user_id ORDER BY day) AS days_since_previous
 FROM analytics.activity
), returns AS (
 SELECT date_trunc('month',day)::date AS month,COUNT(DISTINCT user_id) AS returning_users
 FROM gaps WHERE days_since_previous>=31 GROUP BY 1
)
SELECT r.month,COALESCE(t.returning_users,0) AS returning_users
FROM analytics.monthly_revenue r LEFT JOIN returns t USING(month) ORDER BY r.month;
