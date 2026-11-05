# SQL catalogue and metric contracts

All queries use the clean `analytics` schema and fixed observation end (2025-12-31), avoiding changes caused by the date of execution. Each SQL file comments its question, grain and caveats. NULL ratios mean an undefined denominator, never a fabricated zero.

## [01_dau](../sql/queries/01_dau.sql)

How many unique users played each business day?

One row per calendar day; active = at least one gameplay session; zero days included.

## [02_mau](../sql/queries/02_mau.sql)

How many unique users played each month?

Unique gameplay users in each calendar month; do not sum DAU.

## [03_monthly_revenue](../sql/queries/03_monthly_revenue.sql)

How does monthly revenue change?

GGR and NGR in KRW. MoM uses previous calendar month; first month is NULL.

## [04_ggr](../sql/queries/04_ggr.sql)

What is gross gaming revenue and realized hold?

All settled simulated sessions; stakes minus payouts. Negative GGR is allowed.

## [05_ngr](../sql/queries/05_ngr.sql)

How much gaming revenue remains after modeled bonuses?

Bonus expense = min(round(successful deposit * 5%), KRW 10000) per deposit; no other deductions.

## [06_arpu](../sql/queries/06_arpu.sql)

What is monthly revenue per gameplay-active user?

GGR / distinct monthly gameplay users. GGR ARPU; not per all registered accounts.

## [07_arppu](../sql/queries/07_arppu.sql)

What is monthly gaming revenue attributable to depositors per depositor?

Payer = >=1 successful deposit that month; numerator includes only their GGR in the same month, including zero.

## [08_exact_day_retention](../sql/queries/08_exact_day_retention.sql)

What fraction play exactly 1, 7, or 30 days after signup?

Registration-based exact-day retention; excludes registrations without complete follow-up for each horizon.

## [09_monthly_cohort_retention](../sql/queries/09_monthly_cohort_retention.sql)

How does gameplay retention evolve across registration cohorts?

Denominator = all registrations in cohort, including inactive accounts. Future cells absent, not zero.

## [10_ltv_90d](../sql/queries/10_ltv_90d.sql)

What is observed 90-day NGR per acquired user?

LTV proxy, not a lifetime forecast: first 90 dates [signup, signup+90); only fully mature users. No discount/tax/opex.

## [11_cac](../sql/queries/11_cac.sql)

What did each paid channel spend per attributed registration?

Single-touch signup attribution. Aggregate cost at campaign grain before joining users; organic CAC is undefined.

## [12_revenue_by_channel](../sql/queries/12_revenue_by_channel.sql)

Which signup channels contribute revenue?

Lifetime in-window GGR and bonus-only NGR by signup channel; no causal marketing claim.

## [13_revenue_by_game](../sql/queries/13_revenue_by_game.sql)

How do game categories differ in volume and realized hold?

GGR only: deposit bonuses cannot be allocated to games without an additional allocation assumption.

## [14_value_segments](../sql/queries/14_value_segments.sql)

How concentrated is observed revenue?

Historical descriptive segments, not a targeting recommendation. NTILE among players only; inactive separate.

## [15_deposit_withdrawal_ratio](../sql/queries/15_deposit_withdrawal_ratio.sql)

How do successful deposits compare with successful withdrawals?

Amount ratio and cash movement, not revenue, margin, or wallet balance. Independent monthly aggregates avoid fanout.

## [16_returning_users](../sql/queries/16_returning_users.sql)

How many monthly players returned after at least 30 days without gameplay?

Return = gap >=31 days between distinct active dates; first-ever gameplay excluded. Not proof of marketing impact.

## [17_payment_success](../sql/queries/17_payment_success.sql)

Does payment completion vary by month and transaction type?

Snapshot success rates: pending and failed remain in denominator; not eventual settlement conversion.

## [18_channel_unit_economics](../sql/queries/18_channel_unit_economics.sql)

How does mature 90-day NGR per user compare with CAC for the same signup cohorts?

Only campaigns with complete 90-day follow-up: every attributed signup has 90 dates of follow-up. Ratio is a proxy, not ROAS forecast.


## Interpretation choices

ARPU uses gameplay activity because it corresponds to the source of GGR. ARPPU restricts both numerator and denominator to same-month successful depositors; using total platform GGR over depositor count would mix populations. Retention anchors to registration, not first deposit or first session. Monthly age is calendar-month difference, not elapsed 30-day blocks.

The 90-day LTV proxy uses ages 0–89 inclusive. Mature-user query 10 includes only users whose 90th observation date is available. Query 18 compares LTV/CAC using entire campaigns with full 90-day follow-up for every possible registration; query 11 full-window CAC should not be naively compared to query 10's partially filtered population.

Top-value deciles use GGR, a volatile operator-revenue measure; inactive users are separate and nonpositive GGR users retain their negative values. Segments are historical descriptions and should not become offers or targeting rules without separate review and context.

## Primary documentation

- [PostgreSQL date/time functions](https://www.postgresql.org/docs/17/functions-datetime.html)
- [PostgreSQL window functions](https://www.postgresql.org/docs/17/tutorial-window.html)
- [PostgreSQL generate_series](https://www.postgresql.org/docs/17/functions-srf.html)
- [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing)

## [19_first_deposit_conversion](../sql/queries/19_first_deposit_conversion.sql)

Successful first-deposit conversion by signup channel, ages 0–6 inclusive. Includes only registrations with seven fully observed calendar dates. Non-depositors stay in the denominator; repeated deposits count once.
