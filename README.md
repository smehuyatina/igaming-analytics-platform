# iGaming Analytics Platform — Player Behavior, Revenue & Retention Analysis

**Independent portfolio simulation. Every user, company detail, transaction, and business scenario is fictional. This project is not employment experience.**

A reproducible analytics platform for **Haedam Interactive**, a fictional South Korea-based technology vendor supporting a simulated international iGaming product. KRW is the reporting currency; country labels are illustrative synthetic attributes, not a statement about market access or licensing. There is no live gambling functionality.

The business scenario: a product analyst needs reliable monthly revenue, gameplay engagement, registration retention, and acquisition economics before recommending further analysis. The work demonstrates junior analyst skills: data cleaning, relational modeling, SQL, metric design, Python reconciliation, communication, and a small tested dashboard.

![Synthetic revenue analysis](reports/revenue_trends.png)

## Reproduce locally (macOS Apple Silicon)

Requires Python 3.11+ and Docker Desktop or another working Docker Compose runtime. The official PostgreSQL image supports native ARM64. No paid services or API keys.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
docker compose up -d --wait
igaming all
streamlit run app.py
```

Open the Streamlit URL printed in the terminal (normally http://localhost:8501). Generation creates **22,000 users, 310,000 sessions, 70,000 deposits, and 22,000 withdrawals**, before cleaning. These are 402,000 gameplay/transaction records across January 2024–December 2025. Marketing tables contain 96 campaigns and one attribution per paid-channel registration.

For a quick dashboard preview, committed SQL exports work immediately after installation; PostgreSQL is needed to rebuild them. Full raw and clean CSVs are generated locally and excluded from Git. A separate delivery archive may include them.

The database is bound to `127.0.0.1:55437`. The credentials in Compose are deliberately public, local-demo credentials. Use a **dedicated portfolio database**: the loader transactionally replaces all six tables in the `analytics` schema. It never appends a second copy of a run. Keep the repository folder when installing: SQL and report assets are resolved relative to the editable checkout.

```bash
# Optional override; .env.example is a reference, NOT automatically loaded
export DATABASE_URL='postgresql+psycopg://portfolio:portfolio_local@localhost:55437/igaming'
igaming generate
igaming clean
igaming load
igaming analyze
ruff check src tests app.py
pytest -m 'not integration'
# Integration tests temporarily truncate dedicated tables in rollback transactions
pytest -v
# Stop database while retaining its data
docker compose down
```

Integration tests run when `DATABASE_URL` is explicitly set; otherwise they skip. Python 3.11 and 3.13 are configured in GitHub Actions; see [local validation evidence](reports/validation.md) for what was actually run. The Python dependency ranges are compatible constraints; [requirements-lock.txt](requirements-lock.txt) records the locally verified Python 3.13 environment (`pip install -r requirements-lock.txt` before editable install for the same versions). Container tag `postgres:17` tracks patch releases rather than a frozen image digest.

## Architecture

```mermaid
flowchart LR
    A[Seeded NumPy simulation] --> B[Raw CSV + SHA256 manifest]
    B --> C[Pandas cleaning + quarantine]
    C --> D[PostgreSQL constrained tables]
    D --> E[SQL views + 19 business queries]
    E --> F[Versioned result CSVs]
    F --> G[Streamlit / Plotly dashboard]
    F --> H[Matplotlib / Seaborn report]
    C --> I[Independent Pandas calculation]
    I --> J[SQL reconciliation]
    E --> J
```

## Metrics that need careful interpretation

| Metric | Contract |
|---|---|
| DAU / MAU | Distinct users with at least one gameplay session on a business day / calendar month |
| GGR | Session stakes minus payouts, including negative session and user values |
| NGR | GGR minus modeled bonus expense only; excludes taxes, fees, and other costs |
| Bonus | 5% of every successful deposit, rounded to integer KRW, capped at KRW 10,000 per deposit |
| ARPU | Monthly GGR / monthly gameplay-active users |
| ARPPU | Monthly GGR from same-month successful depositors / all such depositors, including those with no gameplay |
| D1 / D7 / D30 | Played exactly N days after registration / registrations with full follow-up |
| Cohort retention | Active users in month age / all users in that registration month; future cells absent |
| LTV proxy | Observed first 90 dates of bonus-only NGR per mature registered user, including inactive users |
| CAC | Campaign spend / single-touch attributed registrations; organic CAC unknown |
| Deposit / withdrawal ratio | Successful amounts divided; zero withdrawal denominator gives NULL |

Money uses integer KRW in source tables and PostgreSQL NUMERIC for division. Deposit/withdrawal amounts are cash movements, not gaming revenue. Independent facts are aggregated before joins or combined through a ledger; marketing cost is never multiplied by attributed user rows. Revenue by game is GGR because bonuses have no defensible game-level allocation.

## Explore the work

- [Business review](reports/business_review.md) — channel economics, concentration, game mix, and next investigations.
- [Executive findings](reports/executive_summary.md) — generated numbers and bounded recommendations.
- [Metric dictionary and SQL catalogue](docs/metrics.md) — all 19 questions, grain and caveats.
- [Synthetic generation rules](docs/synthetic_data.md) — assumptions, defect rates, and important limitations.
- [Data dictionary and entity diagram](docs/data_dictionary.md).
- [Resume project bullets](docs/resume_bullets.md).
- [Mentor walkthrough and interview guide](docs/mentoring.md).
- [Runbook](docs/runbook.md) — failures, reruns, and evidence.
- [Dashboard preview](reports/dashboard.png).

![Registration cohort retention](reports/cohort_retention.png)

## Repository map

```text
app.py                    Streamlit dashboard over SQL exports
src/igaming/              Generate → clean → load → analyze CLI
sql/schema.sql            Constraints, foreign keys, indexes
sql/views.sql             Calendar, activity, revenue ledger, monthly mart
sql/queries/              19 commented PostgreSQL analytics queries
tests/                    Data quality, golden SQL fixtures, dashboard behavior
reports/                  Findings, charts, SQL outputs, validation evidence
docs/                     Modeling decisions, definitions, mentoring, runbook
data/raw/ + data/clean/    Generated locally; intentionally untracked
.github/workflows/ci.yml  Python matrix + PostgreSQL end-to-end checks
```

## Honest scope

This is a batch analytics demonstration, not a production warehouse or gambling ledger. Sessions and cash transactions share user relationships and dates but do not simulate wallet conservation, KYC, real odds, real market retention, or temporal account-status changes. Long-tenure users have more opportunity to act; truncated follow-up and a fixed-size event target influence late-window activity. Findings reflect assumptions built into the generator and cannot validate a real commercial strategy.

Portfolio wording: “Built an independent synthetic analytics platform using PostgreSQL and Python; defined retention and revenue metrics, reconciled SQL against Pandas, and delivered a Streamlit dashboard.” Do not describe this as work for a real employer.

MIT licensed. No real personal information or external data is used.
