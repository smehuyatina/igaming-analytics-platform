-- Business question: What fraction play exactly 1, 7, or 30 days after signup?
-- Metric contract: Registration-based exact-day retention; excludes registrations without complete follow-up for each horizon.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
WITH horizons AS (SELECT unnest(ARRAY[1,7,30]) AS horizon_days)
SELECT h.horizon_days,COUNT(*) AS eligible_users,
 COUNT(a.user_id) AS retained_users,ROUND(100.0*COUNT(a.user_id)/NULLIF(COUNT(*),0),2) AS retention_pct
FROM horizons h JOIN analytics.users u ON u.registration_date+h.horizon_days<=DATE '2025-12-31'
LEFT JOIN analytics.activity a ON a.user_id=u.user_id AND a.day=u.registration_date+h.horizon_days
GROUP BY h.horizon_days ORDER BY h.horizon_days;
