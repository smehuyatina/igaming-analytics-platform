-- Dedicated schema; dates represent Asia/Seoul business dates (no intraday timestamps).
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE TABLE IF NOT EXISTS analytics.users (
 user_id BIGINT PRIMARY KEY, registration_date DATE NOT NULL,
 country TEXT NOT NULL CHECK (country IN ('KR','JP','TW','CA','NZ','UNKNOWN')),
 acquisition_channel TEXT NOT NULL CHECK (acquisition_channel IN ('organic','paid_search','social','affiliate','influencer')),
 device_type TEXT NOT NULL CHECK (device_type IN ('mobile','desktop','tablet')),
 account_status TEXT NOT NULL CHECK (account_status IN ('active','closed','suspended'))
);
CREATE TABLE IF NOT EXISTS analytics.marketing_campaigns (
 campaign_id BIGINT PRIMARY KEY, channel TEXT NOT NULL CHECK (channel IN ('paid_search','social','affiliate','influencer')),
 campaign_start_date DATE NOT NULL, campaign_end_date DATE NOT NULL,
 campaign_cost_krw BIGINT NOT NULL CHECK (campaign_cost_krw>=0), CHECK (campaign_end_date>=campaign_start_date)
);
CREATE TABLE IF NOT EXISTS analytics.campaign_attribution (
 user_id BIGINT PRIMARY KEY REFERENCES analytics.users,
 campaign_id BIGINT NOT NULL REFERENCES analytics.marketing_campaigns
);
CREATE TABLE IF NOT EXISTS analytics.deposits (
 deposit_id BIGINT PRIMARY KEY, user_id BIGINT NOT NULL REFERENCES analytics.users,
 amount_krw BIGINT NOT NULL CHECK (amount_krw>0), transaction_date DATE NOT NULL,
 payment_status TEXT NOT NULL CHECK (payment_status IN ('success','failed','pending'))
);
CREATE TABLE IF NOT EXISTS analytics.withdrawals (
 withdrawal_id BIGINT PRIMARY KEY, user_id BIGINT NOT NULL REFERENCES analytics.users,
 amount_krw BIGINT NOT NULL CHECK (amount_krw>0), transaction_date DATE NOT NULL,
 payment_status TEXT NOT NULL CHECK (payment_status IN ('success','failed','pending'))
);
CREATE TABLE IF NOT EXISTS analytics.game_sessions (
 session_id BIGINT PRIMARY KEY, user_id BIGINT NOT NULL REFERENCES analytics.users,
 game_type TEXT NOT NULL CHECK (game_type IN ('slots','live_casino','sports','table_games')),
 session_date DATE NOT NULL, bet_amount_krw BIGINT NOT NULL CHECK (bet_amount_krw>0),
 win_amount_krw BIGINT NOT NULL CHECK (win_amount_krw>=0),
 session_duration_minutes NUMERIC(8,2) NOT NULL CHECK (session_duration_minutes BETWEEN 1 AND 240)
);
CREATE INDEX IF NOT EXISTS sessions_user_date ON analytics.game_sessions (user_id,session_date);
CREATE INDEX IF NOT EXISTS sessions_date ON analytics.game_sessions (session_date);
CREATE INDEX IF NOT EXISTS deposits_user_date ON analytics.deposits (user_id,transaction_date);
CREATE INDEX IF NOT EXISTS withdrawals_user_date ON analytics.withdrawals (user_id,transaction_date);
CREATE INDEX IF NOT EXISTS users_registration ON analytics.users (registration_date);
