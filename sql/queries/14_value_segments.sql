-- Business question: How concentrated is observed revenue?
-- Metric contract: Historical descriptive segments, not a targeting recommendation. NTILE among players only; inactive separate.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
WITH player_value AS (
 SELECT user_id,SUM(bet_amount_krw-win_amount_krw) AS ggr,COUNT(*) AS sessions
 FROM analytics.game_sessions GROUP BY user_id
), ranked AS (
 SELECT *,NTILE(10) OVER (ORDER BY ggr DESC,user_id) AS value_decile FROM player_value
), segments AS (
 SELECT u.user_id,COALESCE(r.ggr,0) AS ggr,
 CASE WHEN r.user_id IS NULL THEN 'no_gameplay'
      WHEN r.ggr<=0 THEN 'nonpositive_ggr'
      WHEN r.value_decile=1 THEN 'top_ggr_decile' ELSE 'other_players' END AS segment
 FROM analytics.users u LEFT JOIN ranked r USING(user_id)
)
SELECT segment,COUNT(*) AS users,SUM(ggr) AS ggr_krw,ROUND(AVG(ggr),2) AS ggr_per_registered_user_krw
FROM segments GROUP BY segment ORDER BY ggr_krw DESC;
