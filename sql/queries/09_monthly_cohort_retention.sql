-- Business question: How does gameplay retention evolve across registration cohorts?
-- Metric contract: Denominator = all registrations in cohort, including inactive accounts. Future cells absent, not zero.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
WITH cohorts AS (
 SELECT date_trunc('month',registration_date)::date AS cohort_month,COUNT(*) AS cohort_users
 FROM analytics.users GROUP BY 1
), retained AS (
 SELECT date_trunc('month',u.registration_date)::date AS cohort_month,
 date_trunc('month',a.day)::date AS activity_month,COUNT(DISTINCT u.user_id) AS retained_users
 FROM analytics.users u JOIN analytics.activity a USING(user_id) GROUP BY 1,2
), grid AS (
 SELECT c.*,m.month::date AS activity_month FROM cohorts c
 CROSS JOIN LATERAL generate_series(c.cohort_month,DATE '2025-12-01',interval '1 month') m(month)
)
SELECT g.cohort_month,g.activity_month,
 (EXTRACT(YEAR FROM age(g.activity_month,g.cohort_month))*12+EXTRACT(MONTH FROM age(g.activity_month,g.cohort_month)))::int AS month_age,
 g.cohort_users,COALESCE(r.retained_users,0) AS retained_users,
 ROUND(100.0*COALESCE(r.retained_users,0)/g.cohort_users,2) AS retention_pct
FROM grid g LEFT JOIN retained r USING(cohort_month,activity_month) ORDER BY 1,2;
