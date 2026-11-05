-- Business question: How does mature 90-day NGR per user compare with CAC for the same signup cohorts?
-- Metric contract: Only campaigns with complete 90-day follow-up: every attributed signup has 90 dates of follow-up. Ratio is a proxy, not ROAS forecast.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
WITH eligible_campaigns AS (
 SELECT * FROM analytics.marketing_campaigns WHERE campaign_end_date+89<=DATE '2025-12-31'
), user_value AS (
 SELECT a.campaign_id,u.user_id,COALESCE(SUM(r.ggr-r.bonus),0) AS ngr_90d
 FROM analytics.campaign_attribution a JOIN eligible_campaigns c USING(campaign_id)
 JOIN analytics.users u USING(user_id)
 LEFT JOIN analytics.revenue_ledger r ON r.user_id=u.user_id
 AND r.day>=u.registration_date AND r.day<u.registration_date+90
 GROUP BY a.campaign_id,u.user_id
), campaign_values AS (
 SELECT campaign_id,COUNT(*) AS acquired_users,SUM(ngr_90d) AS ngr_90d FROM user_value GROUP BY 1
)
SELECT c.channel,SUM(c.campaign_cost_krw) AS spend_krw,SUM(COALESCE(v.acquired_users,0)) AS acquired_users,
 ROUND(SUM(v.ngr_90d)/NULLIF(SUM(v.acquired_users),0),2) AS observed_90d_ltv_krw,
 ROUND(SUM(c.campaign_cost_krw)::numeric/NULLIF(SUM(v.acquired_users),0),2) AS cac_krw,
 ROUND(SUM(v.ngr_90d)/NULLIF(SUM(c.campaign_cost_krw),0),2) AS ltv_cac_ratio
FROM eligible_campaigns c LEFT JOIN campaign_values v USING(campaign_id) GROUP BY c.channel ORDER BY c.channel;
