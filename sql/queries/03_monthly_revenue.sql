-- Business question: How does monthly revenue change?
-- Metric contract: GGR and NGR in KRW. MoM uses previous calendar month; first month is NULL.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
SELECT *, ROUND(100.0*(ngr_krw-LAG(ngr_krw) OVER (ORDER BY month)) /
 NULLIF(ABS(LAG(ngr_krw) OVER (ORDER BY month)),0),2) AS ngr_mom_pct
FROM analytics.monthly_revenue ORDER BY month;
