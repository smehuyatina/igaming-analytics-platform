-- Business question: What did each paid channel spend per attributed registration?
-- Metric contract: Single-touch signup attribution. Aggregate cost at campaign grain before joining users; organic CAC is undefined.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
WITH signups AS (
 SELECT campaign_id,COUNT(*) AS acquired_users FROM analytics.campaign_attribution GROUP BY 1
)
SELECT c.channel,SUM(c.campaign_cost_krw) AS spend_krw,SUM(COALESCE(s.acquired_users,0)) AS acquired_users,
 ROUND(SUM(c.campaign_cost_krw)::numeric/NULLIF(SUM(s.acquired_users),0),2) AS cac_krw
FROM analytics.marketing_campaigns c LEFT JOIN signups s USING(campaign_id)
GROUP BY c.channel ORDER BY cac_krw;
