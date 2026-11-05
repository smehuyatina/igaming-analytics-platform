-- Business question: How do game categories differ in volume and realized hold?
-- Metric contract: GGR only: deposit bonuses cannot be allocated to games without an additional allocation assumption.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
SELECT game_type,COUNT(*) AS sessions,COUNT(DISTINCT user_id) AS players,
 SUM(bet_amount_krw) AS bets_krw,SUM(bet_amount_krw-win_amount_krw) AS ggr_krw,
 ROUND(100.0*SUM(bet_amount_krw-win_amount_krw)/NULLIF(SUM(bet_amount_krw),0),2) AS hold_pct
FROM analytics.game_sessions GROUP BY game_type ORDER BY ggr_krw DESC;
