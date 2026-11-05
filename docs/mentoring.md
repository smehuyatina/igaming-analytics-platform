# Mentor walkthrough and interview practice

## Learning path

1. Run `igaming generate`, inspect the raw manifest and locate duplicate IDs. Explain why a duplicate row differs from two legitimate same-amount deposits.
2. Run `igaming clean`; reconcile raw = duplicate + quarantine + clean for every table. Explain why unknown country is retained but negative money is quarantined.
3. Read the entity diagram and constraints. Identify the grain of every table before joining anything.
4. Run DAU/MAU and GGR queries. Explain why summing DAU does not give MAU and why deposits are not revenue.
5. Read the ledger view. Draw the fanout produced by joining two deposits to three sessions (six rows); explain how pre-aggregation avoids it.
6. Inspect retention queries. For a signup on December 30, D1 is observable but D7 is not. Explain why immature users cannot be placed in the denominator.
7. Inspect the 90-day LTV and matched channel economics queries. Explain observation bias and why the result is not a lifetime forecast.
8. Run tests and dashboard. Change the observation filter, describe the chart and its limitations in plain business language.

## Example interview answers

**What did you build?** An independent synthetic portfolio simulation: 22,000 accounts, 402,000 pre-cleaning gameplay/payment events, constrained PostgreSQL tables, 19 SQL analyses, an audited cleaning layer and a tested Streamlit dashboard. No real company or employment is involved.

**What was the most important correctness decision?** Aligning grain and populations. A ledger prevents multiplying sessions by payments. ARPPU includes only revenue belonging to its depositor population, and retention excludes users without enough follow-up.

**What does NGR mean here?** GGR less a clearly labeled modeled bonus expense. It is not a full industry accounting definition or profit. Additional fees and taxes are unavailable.

**How did you validate results?** Seed reproducibility, row accounting, relationship checks, hand-calculated PostgreSQL fixtures with fanout traps and late registrations, independent monthly Pandas reconciliation, and a dashboard interaction test.

**What would change in production?** Add source contracts, incremental loads and late-arrival handling, secret management, migrations, observability, settlement and wallet reconciliation, event timestamps, and metric ownership. These are discussion topics, not claimed implemented features.

## Exercises for the junior analyst

- Explain query 19: why ages 0–6 span seven dates, and why immature registrations are excluded.
- Add a DAU rolling seven-day mean including zero calendar days.
- Compare registration and first-session retention without changing the original metric contract.
- Quantify how limited follow-up changes event density for late registrations before proposing a tenure-aware generator.
- Describe a test that would catch marketing spend duplication after a join.

Do not replace the project's actual measured findings with generic iGaming benchmarks. Recommendations should be phrased as next analyses or experiments, not causal conclusions from generated data.
