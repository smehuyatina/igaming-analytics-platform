-- Business question: Which signup channels contribute revenue?
-- Metric contract: Lifetime in-window GGR and bonus-only NGR by signup channel; no causal marketing claim.
-- Scope: clean synthetic data, 2024-01-01 through 2025-12-31, Asia/Seoul dates.
SELECT u.acquisition_channel,SUM(r.ggr) AS ggr_krw,SUM(r.bonus) AS bonus_krw,SUM(r.ggr-r.bonus) AS ngr_krw
FROM analytics.revenue_ledger r JOIN analytics.users u USING(user_id)
GROUP BY u.acquisition_channel ORDER BY ngr_krw DESC;
