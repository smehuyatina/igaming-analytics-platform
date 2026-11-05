-- Calendar makes zero-activity periods explicit; immutable observation boundary avoids CURRENT_DATE drift.
CREATE OR REPLACE VIEW analytics.calendar AS
SELECT d::date AS day FROM generate_series(timestamp '2024-01-01',timestamp '2025-12-31',interval '1 day') d;
CREATE OR REPLACE VIEW analytics.activity AS
SELECT DISTINCT user_id, session_date AS day FROM analytics.game_sessions;
-- Ledger grain = user, date, source event. No join between independent fact tables.
CREATE OR REPLACE VIEW analytics.revenue_ledger AS
SELECT user_id,session_date AS day,bet_amount_krw AS bets,win_amount_krw AS wins,
       bet_amount_krw-win_amount_krw AS ggr,0::numeric AS bonus
FROM analytics.game_sessions
UNION ALL
SELECT user_id,transaction_date,0::bigint,0::bigint,0::bigint,
       LEAST(ROUND(amount_krw*0.05),10000) AS bonus
FROM analytics.deposits WHERE payment_status='success';
CREATE OR REPLACE VIEW analytics.monthly_revenue AS
SELECT date_trunc('month',c.day)::date AS month,
       COALESCE(SUM(r.bets),0) AS bets_krw,COALESCE(SUM(r.wins),0) AS wins_krw,
       COALESCE(SUM(r.ggr),0) AS ggr_krw,COALESCE(SUM(r.bonus),0) AS bonus_krw,
       COALESCE(SUM(r.ggr-r.bonus),0) AS ngr_krw
FROM analytics.calendar c LEFT JOIN analytics.revenue_ledger r USING(day) GROUP BY 1;
