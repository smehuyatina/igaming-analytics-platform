-- Business question: Which signup channels convert to a first successful deposit within seven dates?
-- Contract: ages 0..6 inclusive [registration, registration+7); only registrations with full follow-up.
-- Failed/pending attempts do not convert. One earliest successful deposit per user avoids double counting.
-- Scope: clean synthetic data, Asia/Seoul dates, observation ends 2025-12-31.
WITH first_deposit AS (
 SELECT user_id, MIN(transaction_date) AS first_success_date
 FROM analytics.deposits WHERE payment_status='success' GROUP BY user_id
), eligible AS (
 SELECT u.user_id,u.acquisition_channel,
        CASE WHEN d.first_success_date>=u.registration_date
                   AND d.first_success_date<u.registration_date+7 THEN 1 ELSE 0 END AS converted
 FROM analytics.users u LEFT JOIN first_deposit d USING(user_id)
 WHERE u.registration_date+6<=DATE '2025-12-31'
)
SELECT acquisition_channel,COUNT(*) AS eligible_users,SUM(converted) AS converted_users,
 ROUND(100.0*SUM(converted)/NULLIF(COUNT(*),0),2) AS conversion_pct
FROM eligible GROUP BY acquisition_channel ORDER BY acquisition_channel;
