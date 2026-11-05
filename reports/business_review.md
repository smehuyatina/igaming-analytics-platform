# Business review — fictional platform

This independent simulation is an interview artifact. Findings describe generated data and do not establish real market performance or commercial causality.

## Revenue and engagement

Modeled bonus expense consumes 3.96% of observed GGR. This is an accounting assumption, not a measured promotion return. NGR excludes taxes, payment charges, vendor costs and operating expense.

| Year | GGR (KRW) | Bonus-only NGR (KRW) |
|---|---:|---:|
| 2024 | 2,233,453,689 | 2,148,266,139 |
| 2025 | 3,886,899,173 | 3,729,657,873 |

Year-on-year growth includes platform launch ramp-up, cumulative registrations, modeled seasonality and acquisition mix. It must not be attributed to a campaign without a control or comparison design.

4,374 registered users have no observed gameplay (19.88% of registrations). A no-gameplay account may still have a deposit; this is deliberate and reinforces why payer and active populations differ.

## Acquisition economics

These figures use the same fully observed campaigns for both cost and 90-day user value. Organic is omitted because its cost is unknown. A ratio above one is not evidence of profitability; the numerator has limited deductions and the horizon is only 90 days.

| Channel | Mature attributed registrations | 90-day NGR / user | CAC (KRW) | Ratio |
|---|---:|---:|---:|---:|
| paid_search | 4,536 | 203,427.15 | 43,093.07 | 4.72 |
| social | 3,735 | 128,611.94 | 32,765.63 | 3.93 |
| affiliate | 3,149 | 171,188.98 | 47,250.82 | 3.62 |
| influencer | 1,435 | 83,714.54 | 58,648.98 | 1.43 |

Channel differences partly come directly from engagement factors in the generator. Suggested decision: retain this as a measurement framework and test incremental value in a real controlled setting before reallocating spend.

## Revenue concentration and game mix

The top GGR decile of observed players contributes 83.14% of total GGR. Negative-GGR users are preserved, so segment shares need not all be positive. Ranking by realized operator revenue is volatile; it is not a responsible-gaming risk classifier or a targeting rule.

| Game | Sessions | GGR (KRW) | Realized hold |
|---|---:|---:|---:|
| slots | 148,950 | 2,982,323,850 | 13.76% |
| live_casino | 74,519 | 1,338,184,575 | 12.29% |
| sports | 55,787 | 1,224,741,862 | 15.05% |
| table_games | 30,744 | 575,102,575 | 12.88% |

Higher game revenue can reflect more volume as well as different hold. Bonus NGR is not allocated to games because deposits carry no game attribution.

## Payments and next investigations

- Deposit snapshot completion: 90.93% across 69,930 cleaned attempts. Failed and pending attempts remain in the denominator.
- Withdrawal snapshot completion: 90.91% across 21,978 cleaned attempts. Failed and pending attempts remain in the denominator.

A pending snapshot is not a final failure. Payment data has no provider or reason code, so those drivers cannot be diagnosed here. Deposits minus withdrawals is cash movement, not profit or reconciled wallet balance.

Recommended follow-ups: validate event and settlement contracts; compare channel retention at matched tenure; investigate data-quality rejects before production reporting; and design randomized acquisition measurement. Avoid extrapolating generated values to a real South Korean or international iGaming market.

## Evidence

All figures derive from committed SQL exports in `reports/results/`. The analyzer independently reconciles GGR, bonuses and NGR for all 24 months against Pandas. Hand-calculated SQL tests cover fanout, failed payments, right censoring, inactive users, negative GGR and bonus rounding/caps.
