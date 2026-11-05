"""Execute versioned PostgreSQL queries; reconcile core financial results with independent Pandas."""

import json
import shutil
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sqlalchemy import text
from .config import ROOT
from .db import engine
from .business_review import write_business_review


def pandas_monthly(root=ROOT):
    sessions = pd.read_csv(root / "data/clean/game_sessions.csv", parse_dates=["session_date"])
    deposits = pd.read_csv(root / "data/clean/deposits.csv", parse_dates=["transaction_date"])
    sessions["month"] = sessions.session_date.dt.to_period("M").dt.to_timestamp()
    sessions["ggr_krw"] = sessions.bet_amount_krw - sessions.win_amount_krw
    ggr = sessions.groupby("month").ggr_krw.sum()
    deposits = deposits[deposits.payment_status == "success"].copy()
    deposits["month"] = deposits.transaction_date.dt.to_period("M").dt.to_timestamp()
    # Integer KRW amounts make 5% integral in this generator; floor(x+.5) matches PG positive ROUND.
    deposits["bonus_krw"] = ((deposits.amount_krw * 5 + 50) // 100).clip(upper=10000)
    bonus = deposits.groupby("month").bonus_krw.sum()
    out = pd.DataFrame(index=pd.date_range("2024-01-01", "2025-12-01", freq="MS"))
    out["ggr_krw"] = ggr
    out["bonus_krw"] = bonus
    out = out.fillna(0)
    out["ngr_krw"] = out.ggr_krw - out.bonus_krw
    return out.rename_axis("month").reset_index()


def analyze(root=ROOT):
    out = root / "reports/results"
    out.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(root / "data/clean/quality_report.json", root / "reports/quality_report.json")
    shutil.copyfile(root / "data/raw/manifest.json", root / "reports/generation_manifest.json")
    results = {}
    with engine().connect() as conn:
        for path in sorted((root / "sql/queries").glob("*.sql")):
            results[path.stem] = pd.read_sql(text(path.read_text()), conn)
            results[path.stem].to_csv(out / f"{path.stem}.csv", index=False)
    sql = results["05_ngr"].copy()
    sql["month"] = pd.to_datetime(sql.month)
    independent = pandas_monthly(root)
    for col in ["ggr_krw", "bonus_krw", "ngr_krw"]:
        pd.testing.assert_series_equal(
            sql[col].astype("int64"), independent[col].astype("int64"), check_names=False
        )
    (out / "reconciliation.json").write_text(
        json.dumps({"months_checked": len(sql), "ggr_bonus_ngr_match": True}, indent=2)
    )
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(11, 4.5))
    x = pd.to_datetime(sql.month)
    ax.plot(x, sql.ggr_krw / 1e6, label="GGR")
    ax.plot(x, sql.ngr_krw / 1e6, label="NGR (bonus-only)")
    ax.set(
        ylabel="KRW millions", xlabel="Business month", title="Fictional platform · monthly gaming revenue"
    )
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(root / "reports/revenue_trends.png", dpi=160)
    plt.close(fig)
    cohort = results["09_monthly_cohort_retention"].copy()
    cohort["cohort_month"] = pd.to_datetime(cohort.cohort_month).dt.strftime("%Y-%m")
    fig, ax = plt.subplots(figsize=(12, 8))
    sns.heatmap(
        cohort.pivot(index="cohort_month", columns="month_age", values="retention_pct"),
        cmap="Blues",
        vmin=0,
        vmax=100,
        ax=ax,
        cbar_kws={"label": "Gameplay retention %"},
    )
    ax.set(
        title="Registration cohorts · unobserved months blank",
        xlabel="Months since registration",
        ylabel="Cohort",
    )
    fig.tight_layout()
    fig.savefig(root / "reports/cohort_retention.png", dpi=160)
    plt.close(fig)
    ggr = int(sql.ggr_krw.sum())
    ngr = int(sql.ngr_krw.sum())
    retention = results["08_exact_day_retention"]
    channels = results["12_revenue_by_channel"]
    best = channels.iloc[0]
    (root / "reports/executive_summary.md").write_text(
        "# Synthetic portfolio findings\n\nIndependent simulation; no real company or employment experience.\n\n"
        f"- Observation: January 2024–December 2025 (24 complete months).\n"
        f"- Observed GGR: KRW {ggr:,}; bonus-only NGR: KRW {ngr:,}.\n"
        f"- Highest total NGR signup channel: {best.acquisition_channel} (KRW {int(best.ngr_krw):,}). "
        "This is an association shaped by generator assumptions, not incremental return.\n"
        + "".join(
            f"- Exact D{int(r.horizon_days)} registration retention: {r.retention_pct:.2f}% "
            f"({int(r.retained_users):,}/{int(r.eligible_users):,} eligible users).\n"
            for r in retention.itertuples()
        )
        + "\n## Suggested next analysis\n\nCompare channels with matched 90-day cohorts (query 18), then design a randomized "
        "measurement plan before changing budget. Review payment failures by provider only if such a field is collected. "
        "Investigate retention differences after adjusting for tenure; the simulation does not establish causality.\n\n"
        "## Limits\n\nNo real market benchmarks, wallet accounting, fraud labels, taxes, payment fees or bonus redemption. "
        "The NGR model is deliberately simplified; 90-day LTV is an observed proxy. Account status is an end-of-window snapshot.\n"
    )
    write_business_review(results, root)
    return {"queries": len(results), "months_reconciled": len(sql), "ggr_krw": ggr, "ngr_krw": ngr}
