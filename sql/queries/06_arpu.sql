-- Business question: What is monthly revenue per gameplay-active user?
-- Metric contract: GGR / distinct monthly gameplay users. GGR ARPU; not per all registered accounts.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
WITH active AS (
 SELECT date_trunc('month',day)::date AS month,COUNT(DISTINCT user_id) AS mau
 FROM analytics.activity GROUP BY 1
)
SELECT r.month,COALESCE(a.mau,0) AS mau,r.ggr_krw,
 ROUND(r.ggr_krw/NULLIF(a.mau,0),2) AS arpu_krw
FROM analytics.monthly_revenue r LEFT JOIN active a USING(month) ORDER BY r.month;
