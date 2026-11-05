-- Business question: Does payment completion vary by month and transaction type?
-- Metric contract: Snapshot success rates: pending and failed remain in denominator; not eventual settlement conversion.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
WITH payments AS (
 SELECT 'deposit' AS type,transaction_date,payment_status FROM analytics.deposits
 UNION ALL SELECT 'withdrawal',transaction_date,payment_status FROM analytics.withdrawals
)
SELECT type,date_trunc('month',transaction_date)::date AS month,COUNT(*) AS attempts,
 COUNT(*) FILTER (WHERE payment_status='success') AS successes,
 ROUND(100.0*COUNT(*) FILTER (WHERE payment_status='success')/COUNT(*),2) AS success_pct
FROM payments GROUP BY 1,2 ORDER BY 1,2;
