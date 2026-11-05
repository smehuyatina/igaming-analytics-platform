-- Business question: How do successful deposits compare with successful withdrawals?
-- Metric contract: Amount ratio and cash movement, not revenue, margin, or wallet balance. Independent monthly aggregates avoid fanout.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
WITH d AS (
 SELECT date_trunc('month',transaction_date)::date AS month,SUM(amount_krw) AS deposits_krw
 FROM analytics.deposits WHERE payment_status='success' GROUP BY 1
), w AS (
 SELECT date_trunc('month',transaction_date)::date AS month,SUM(amount_krw) AS withdrawals_krw
 FROM analytics.withdrawals WHERE payment_status='success' GROUP BY 1
)
SELECT r.month,COALESCE(d.deposits_krw,0) AS deposits_krw,COALESCE(w.withdrawals_krw,0) AS withdrawals_krw,
 ROUND(d.deposits_krw::numeric/NULLIF(w.withdrawals_krw,0),3) AS deposit_withdrawal_ratio,
 COALESCE(d.deposits_krw,0)-COALESCE(w.withdrawals_krw,0) AS net_cash_movement_krw
FROM analytics.monthly_revenue r LEFT JOIN d USING(month) LEFT JOIN w USING(month) ORDER BY r.month;
