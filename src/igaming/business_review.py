"""Turn query outputs into a bounded, reproducible stakeholder narrative."""

import pandas as pd


def write_business_review(results, root):
    revenue = results["05_ngr"]
    segments = results["14_value_segments"].set_index("segment")
    games = results["13_revenue_by_game"]
    economics = results["18_channel_unit_economics"].sort_values("ltv_cac_ratio", ascending=False)
    payments = results["17_payment_success"]
    annual = (
        revenue.assign(year=pd.to_datetime(revenue.month).dt.year)
        .groupby("year")[["ggr_krw", "ngr_krw"]]
        .sum()
    )
    total_ggr = revenue.ggr_krw.sum()
    inactive = segments.loc["no_gameplay", "users"]
    top_share = 100 * segments.loc["top_ggr_decile", "ggr_krw"] / total_ggr
    bonus_share = 100 * revenue.bonus_krw.sum() / total_ggr
    lines = [
        "# Business review — fictional platform\n",
        "This independent simulation is an interview artifact. Findings describe generated data and do not establish real market performance or commercial causality.\n",
        "## Revenue and engagement\n",
        f"Modeled bonus expense consumes {bonus_share:.2f}% of observed GGR. This is an accounting assumption, not a measured promotion return. NGR excludes taxes, payment charges, vendor costs and operating expense.\n",
        "| Year | GGR (KRW) | Bonus-only NGR (KRW) |\n|---|---:|---:|",
    ]
    lines += [f"| {year} | {int(row.ggr_krw):,} | {int(row.ngr_krw):,} |" for year, row in annual.iterrows()]
    lines += [
        "\nYear-on-year growth includes platform launch ramp-up, cumulative registrations, modeled seasonality and acquisition mix. It must not be attributed to a campaign without a control or comparison design.\n",
        f"{int(inactive):,} registered users have no observed gameplay ({100 * inactive / segments.users.sum():.2f}% of registrations). A no-gameplay account may still have a deposit; this is deliberate and reinforces why payer and active populations differ.\n",
        "## Acquisition economics\n",
        "These figures use the same fully observed campaigns for both cost and 90-day user value. Organic is omitted because its cost is unknown. A ratio above one is not evidence of profitability; the numerator has limited deductions and the horizon is only 90 days.\n",
        "| Channel | Mature attributed registrations | 90-day NGR / user | CAC (KRW) | Ratio |\n|---|---:|---:|---:|---:|",
    ]
    lines += [
        f"| {r.channel} | {int(r.acquired_users):,} | {r.observed_90d_ltv_krw:,.2f} | {r.cac_krw:,.2f} | {r.ltv_cac_ratio:.2f} |"
        for r in economics.itertuples()
    ]
    lines += [
        "\nChannel differences partly come directly from engagement factors in the generator. Suggested decision: retain this as a measurement framework and test incremental value in a real controlled setting before reallocating spend.\n",
        "## Revenue concentration and game mix\n",
        f"The top GGR decile of observed players contributes {top_share:.2f}% of total GGR. Negative-GGR users are preserved, so segment shares need not all be positive. Ranking by realized operator revenue is volatile; it is not a responsible-gaming risk classifier or a targeting rule.\n",
        "| Game | Sessions | GGR (KRW) | Realized hold |\n|---|---:|---:|---:|",
    ]
    lines += [
        f"| {r.game_type} | {int(r.sessions):,} | {int(r.ggr_krw):,} | {r.hold_pct:.2f}% |"
        for r in games.itertuples()
    ]
    lines += [
        "\nHigher game revenue can reflect more volume as well as different hold. Bonus NGR is not allocated to games because deposits carry no game attribution.\n",
        "## Payments and next investigations\n",
    ]
    for kind, frame in payments.groupby("type"):
        rate = 100 * frame.successes.sum() / frame.attempts.sum()
        lines.append(
            f"- {kind.title()} snapshot completion: {rate:.2f}% across {int(frame.attempts.sum()):,} cleaned attempts. Failed and pending attempts remain in the denominator."
        )
    lines += [
        "\nA pending snapshot is not a final failure. Payment data has no provider or reason code, so those drivers cannot be diagnosed here. Deposits minus withdrawals is cash movement, not profit or reconciled wallet balance.\n",
        "Recommended follow-ups: validate event and settlement contracts; compare channel retention at matched tenure; investigate data-quality rejects before production reporting; and design randomized acquisition measurement. Avoid extrapolating generated values to a real South Korean or international iGaming market.\n",
        "## Evidence\n",
        "All figures derive from committed SQL exports in `reports/results/`. The analyzer independently reconciles GGR, bonuses and NGR for all 24 months against Pandas. Hand-calculated SQL tests cover fanout, failed payments, right censoring, inactive users, negative GGR and bonus rounding/caps.\n",
    ]
    (root / "reports/business_review.md").write_text("\n".join(lines))
