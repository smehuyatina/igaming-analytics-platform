-- Business question: What is observed 90-day NGR per acquired user?
-- Metric contract: LTV proxy, not a lifetime forecast: first 90 dates [signup, signup+90); only fully mature users. No discount/tax/opex.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
WITH mature AS (
 SELECT * FROM analytics.users WHERE registration_date+89<=DATE '2025-12-31'
), per_user AS (
 SELECT u.user_id,u.acquisition_channel,COALESCE(SUM(r.ggr-r.bonus),0) AS ngr_90d
 FROM mature u LEFT JOIN analytics.revenue_ledger r ON r.user_id=u.user_id
 AND r.day>=u.registration_date AND r.day<u.registration_date+90
 GROUP BY u.user_id,u.acquisition_channel
)
SELECT acquisition_channel,COUNT(*) AS mature_users,ROUND(AVG(ngr_90d),2) AS observed_90d_ltv_krw
FROM per_user GROUP BY 1 ORDER BY 3 DESC;
