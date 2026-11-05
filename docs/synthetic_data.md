# Synthetic-data design

## Observation and fictional business

Haedam Interactive is invented solely for this project. Business dates are Asia/Seoul calendar dates, from 2024-01-01 through 2025-12-31 inclusive (731 days). There are no timestamps to convert, exchange rates, real identities, geolocation, or actual company data. No real-world gambling regulation assumptions are encoded.

## Generation rules

Default seed: **20261105**; independent raw-defect stream uses seed + 1. NumPy's Generator is local to each call; repeated calls with the same dependency versions and seed produce identical file hashes. Exact bytes across future NumPy/Pandas releases are not promised; use the recorded environment lock for reproduction.

1. **22,000 registrations.** Sample dates using gradual growth (`1 + day_index/1600`), annual cosine seasonality (18% amplitude), and a 12% weekend uplift. All users have a fictional integer ID.
2. **Acquisition.** Organic 30%, paid search 25%, social 20%, affiliate 17%, influencer 8%. Device mix: mobile 74%, desktop 21%, tablet 5%. Countries: KR 25%, JP 30%, TW 20%, CA 15%, NZ 10%. These are invented sampling probabilities.
3. **Status.** Active 94%, closed 4%, suspended 2% as an end-of-window snapshot. Status does not filter historical sessions; no status history is available.
4. **Engagement.** User latent propensity follows lognormal(0, 0.85), multiplied by channel factors (organic 1.25, paid search 1.05, social 0.75, affiliate 0.95, influencer 0.65). A random 18% have zero propensity and no sessions or payments. Other users may also have zero observed gameplay by chance.
5. **Dates and returners.** Each event samples a user by engagement multiplied by observable activity mass. The latent activity-age mixture is 72% exponential(scale 38 days) and 28% uniform across 731 days. For available follow-up T, mass = 0.72 × (1 − exp(−T/38)) + 0.28 × T/731. The conditional early-age probability is the first term divided by this mass; ages are sampled from the truncated exponential or uniform available dates. This reduces event counts for newly registered users. A numerical bound keeps dates inside the observation window; a bounded resampling step favors winter and weekends. This creates early engagement, long gaps and returns, with realistic variation rather than a fitted industry process. Fixed event totals and bounded seasonal resampling remain modeling simplifications.
6. **310,000 sessions.** Game mix: slots 48%, live casino 24%, sports 18%, table games 10%. Stakes are lognormal(10.8, 1.1) scaled by square root of user engagement, rounded to KRW 100 (minimum KRW 1,000). Session payout multipliers are 0, 0.75, 1.5, 8 with probabilities 20%, 62%, 16%, 2%. Category multipliers: 1.00, 1.02, 0.98, 1.03 respectively. Expected base payout ratio is 86.5% before category effects. Individual sessions/users can generate negative GGR. Duration is lognormal(3, 0.6), clipped to 1–240 minutes.
7. **70,000 deposits / 22,000 withdrawals.** Amounts are lognormal around KRW 60,000 / 100,000 with log standard deviation 0.8, rounded to KRW 1,000, minimum KRW 1,000. Status probabilities: success 91%, failed 6%, pending 3%. Payments are sampled independently conditional on engagement; they are not funded by a wallet simulation. Success normalization defects can modestly change the final empirical success mix.
8. **96 marketing campaigns.** One per paid channel per calendar month. Baseline costs KRW 9m / 6m / 7m / 4m, with uniform 0.8–1.2 variation. Each paid registration is attributed to that channel's matching calendar-month campaign. Organic registrations have no attribution row. Exactly one attribution per paid user; this is a simplifying single-touch assumption.
9. **Bonus model.** Every successful cleaned deposit incurs an assumed expense of min(round(amount × 0.05), KRW 10,000), recognized on deposit date. It is an expense proxy, not actual bonus redemption. NGR excludes payment fees, taxes, vendor fees, chargebacks and operating costs; it is not profit.

## Raw layer and cleaning contract

Raw defects are deterministic and separate from valid source-frame generation:

| Defect | Injection | Resolution |
|---|---|---|
| Missing user country | 0.5% of users | Preserve user, set `UNKNOWN`; do not invent country |
| Negative payment amount | 0.1% of each payment table | Quarantine, never convert silently to positive |
| Status case / whitespace | 0.2% of each payment table set to ` SUCCESS ` | Strip and normalize known enum |
| Exact duplicate rows | Approximately 0.2% per table, rounded by Pandas sample | Drop identical rows |

A minimum of one defect is injected into small test fixtures. No ground-truth clean frames are used to repair data. `manifest.json` stores base/raw counts, defect counts, seed, dates and raw-file SHA256 hashes. `quality_report.json` accounts for every row as clean, duplicate, or quarantined. Quarantine CSVs preserve rejected values; raw data remains the audit source. Missing-country counts are also recorded.

Cleaning validates positive integer IDs, integer nonnegative money (payments strictly positive), known enums, date bounds and session duration. Conflicting primary-key duplicates fail the pipeline. Foreign keys, registration-before-event, campaign attribution dates and channel agreement fail before loading. Database constraints add a second defense. Missing required columns fail with an explicit Python exception rather than being inferred.

This generated dataset supports descriptive analysis and software verification. It does not support real market estimates, causal inference, bonus-abuse detection, solvency analysis, responsible-gaming risk scoring or financial reporting.
