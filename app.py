"""Dashboard reads reproducible SQL exports; PostgreSQL is required to rebuild, not to view."""

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parent
st.set_page_config(page_title="iGaming Analytics | Synthetic Portfolio", page_icon="📊", layout="wide")
st.title("iGaming Analytics Platform")
st.caption(
    "Independent portfolio simulation · fictional users and business · KRW · Asia/Seoul business dates"
)


@st.cache_data
def read_result(name, modified):
    return pd.read_csv(ROOT / f"reports/results/{name}.csv")


def get(name):
    path = ROOT / f"reports/results/{name}.csv"
    return read_result(name, path.stat().st_mtime_ns)


if not (ROOT / "reports/results/03_monthly_revenue.csv").exists():
    st.info("Build analytics first: igaming all (PostgreSQL must be running).")
    st.stop()

st.sidebar.header("Observation window")
monthly = get("03_monthly_revenue")
months = monthly.month.tolist()
selected = st.sidebar.select_slider(
    "Revenue / activity months", options=months, value=(months[0], months[-1])
)
mask = monthly.month.between(*selected)
selected_months = monthly[mask]
st.sidebar.caption(
    "The date filter applies to Overview only. Retention and channel totals use the full observation window."
)
overview, retention, channels, quality = st.tabs(
    ["Overview", "Retention", "Games & channels", "Data quality & definitions"]
)
with overview:
    a, b, c = st.columns(3)
    a.metric("GGR · selected months", f"₩{selected_months.ggr_krw.sum() / 1e6:,.1f}m")
    b.metric("NGR · bonus-only", f"₩{selected_months.ngr_krw.sum() / 1e6:,.1f}m")
    mau = get("02_mau")
    c.metric("Mean monthly active users", f"{mau[mau.month.between(*selected)].mau.mean():,.0f}")
    st.plotly_chart(
        px.line(
            selected_months,
            x="month",
            y=["ggr_krw", "ngr_krw"],
            labels={"value": "KRW"},
            title="Monthly revenue",
        ),
        width="stretch",
    )
    dau = get("01_dau")
    dau = dau[
        (dau.day >= selected[0])
        & (dau.day < (pd.Timestamp(selected[1]) + pd.offsets.MonthBegin(1)).strftime("%Y-%m-%d"))
    ]
    st.plotly_chart(px.line(dau, x="day", y="dau", title="Daily gameplay-active users"), width="stretch")
    st.download_button(
        "Download selected monthly metrics",
        selected_months.to_csv(index=False),
        "monthly_metrics.csv",
        "text/csv",
    )
with retention:
    st.subheader("Registration-based retention · full window")
    st.dataframe(get("08_exact_day_retention"), hide_index=True)
    cohort = get("09_monthly_cohort_retention")
    matrix = cohort.pivot(index="cohort_month", columns="month_age", values="retention_pct")
    st.plotly_chart(
        px.imshow(
            matrix,
            zmin=0,
            zmax=100,
            color_continuous_scale="Blues",
            aspect="auto",
            labels={"x": "Month age", "y": "Registration cohort", "color": "Retention %"},
        ),
        width="stretch",
    )
    st.caption(
        "Exact-day retention excludes immature registrations. Blank cohort cells have no follow-up; observed inactivity is 0%. Month 0 need not be 100%."
    )
with channels:
    st.subheader("First successful deposit · first seven calendar dates")
    st.dataframe(get("19_first_deposit_conversion"), hide_index=True)
    st.caption(
        "Registration day through day 6; only users with complete follow-up. Failed and pending attempts do not convert."
    )
    st.subheader("Historical channel and game comparisons · full window")
    st.plotly_chart(
        px.bar(
            get("12_revenue_by_channel"), x="acquisition_channel", y="ngr_krw", title="NGR by signup channel"
        ),
        width="stretch",
    )
    st.dataframe(get("13_revenue_by_game"), hide_index=True)
    st.subheader("Mature, matched 90-day channel economics")
    st.dataframe(get("18_channel_unit_economics"), hide_index=True)
    st.caption(
        "Descriptive simulation only. Channel differences are encoded assumptions, not evidence for real marketing spend."
    )
with quality:
    st.markdown(
        "**Active user:** at least one gameplay session. **GGR:** stakes − payouts. **NGR:** GGR − modeled bonus expense. "
        "**Bonus:** 5% of each successful deposit, capped at ₩10,000. Deposits and withdrawals are cash movements. "
        "**ARPPU:** GGR attributable to same-month successful depositors divided by those depositors. "
        "**LTV:** observed 90-day NGR per mature registration; excludes operating costs."
    )
    path = ROOT / "data/clean/quality_report.json"
    if not path.exists():
        path = ROOT / "reports/quality_report.json"
    if path.exists():
        st.json(path.read_text())
    else:
        st.info("Run igaming clean to rebuild row-level quality artifacts.")
    st.dataframe(get("17_payment_success"), hide_index=True)
    st.warning(
        "Synthetic portfolio data. No real personal information, company performance, or employment claim."
    )
