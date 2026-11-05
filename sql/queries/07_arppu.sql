-- Business question: What is monthly gaming revenue attributable to depositors per depositor?
-- Metric contract: Payer = >=1 successful deposit that month; numerator includes only their GGR in the same month, including zero.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
WITH payers AS (
 SELECT DISTINCT user_id,date_trunc('month',transaction_date)::date AS month
 FROM analytics.deposits WHERE payment_status='success'
), revenue AS (
 SELECT user_id,date_trunc('month',session_date)::date AS month,SUM(bet_amount_krw-win_amount_krw) AS ggr
 FROM analytics.game_sessions GROUP BY 1,2
), metric AS (
 SELECT p.month,COUNT(*) AS paying_users,SUM(COALESCE(r.ggr,0)) AS payer_ggr_krw
 FROM payers p LEFT JOIN revenue r USING(user_id,month) GROUP BY p.month
)
SELECT m.month,COALESCE(t.paying_users,0) AS paying_users,COALESCE(t.payer_ggr_krw,0) AS payer_ggr_krw,
 ROUND(t.payer_ggr_krw/NULLIF(t.paying_users,0),2) AS arppu_krw
FROM analytics.monthly_revenue m LEFT JOIN metric t USING(month) ORDER BY m.month;
