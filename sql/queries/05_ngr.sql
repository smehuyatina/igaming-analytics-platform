-- Business question: How much gaming revenue remains after modeled bonuses?
-- Metric contract: Bonus expense = min(round(successful deposit * 5%), KRW 10000) per deposit; no other deductions.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
SELECT month,ggr_krw,bonus_krw,ngr_krw FROM analytics.monthly_revenue ORDER BY month;
