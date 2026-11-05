# Local validation evidence

Validated on **2026-11-05 (Asia/Seoul)** using macOS ARM64, Python 3.13.15, PostgreSQL 17.11 (official ARM64 Docker image), Pandas 2.3.3, NumPy 2.5.4, SQLAlchemy 2.1.8, Streamlit 1.66.1, and pytest 9.2.0. Exact Python packages are in `requirements-lock.txt`.

| Check | Observed result |
|---|---|
| Full generate → clean → PostgreSQL load → analyze | Completed successfully |
| Default users | 22,000 |
| Clean sessions / deposits / withdrawals | 310,000 / 69,930 / 21,978 |
| Clean combined gameplay/payment events | 401,908 |
| Marketing campaigns / attributed users | 96 / 15,295 |
| Raw duplicate rows removed (all tables) | 879 |
| Quarantined invalid payment rows | 92 |
| Country values retained as UNKNOWN | 110 |
| All PostgreSQL business queries | 19 executed on full dataset and golden fixture |
| Independent SQL vs Pandas reconciliation | GGR, bonus and NGR match in all 24 months |
| Full pytest suite with explicit DATABASE_URL | **14 passed**, 0 failed, 0 skipped (2.12 seconds) |
| Ruff lint / format check | Passed / 12 Python files formatted |
| Full-data regeneration | Exact raw manifests and hashes match |
| Second PostgreSQL load | Identical table counts and financial totals; no accumulation |
| Dashboard | Rendered in local browser; Overview and Retention visually inspected; month-filter behavior tested with AppTest |

The golden fixture checks independent hand-calculated answers for financial fanout, failed-payment exclusion, ARPU/ARPPU populations, late registration censoring, inactive accounts, negative user revenue, and bonus rounding/capping.

Full-dataset financial totals: GGR **KRW 6,120,352,862**, modeled bonus **KRW 242,428,850**, bonus-only NGR **KRW 5,877,924,012**. See `rebuild_evidence.json`, `results/reconciliation.json`, `generation_manifest.json`, and `quality_report.json` for machine-readable evidence.

The GitHub Actions workflow is configured for Python 3.11 and 3.13 with PostgreSQL 17. These remote jobs have **not** been run or observed in this local build. Python 3.11 is a configured CI target, not a claimed local test result. The repository is published at https://github.com/smehuyatina/igaming-analytics-platform. Remote CI status should be checked on the Actions page.
