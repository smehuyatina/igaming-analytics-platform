-- Business question: What is gross gaming revenue and realized hold?
-- Metric contract: All settled simulated sessions; stakes minus payouts. Negative GGR is allowed.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
SELECT SUM(bet_amount_krw) AS bets_krw,SUM(win_amount_krw) AS wins_krw,
 SUM(bet_amount_krw-win_amount_krw) AS ggr_krw,
 ROUND(100.0*SUM(bet_amount_krw-win_amount_krw)/NULLIF(SUM(bet_amount_krw),0),2) AS hold_pct
FROM analytics.game_sessions;
