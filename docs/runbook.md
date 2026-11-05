# Runbook

## Standard execution

Activate the virtual environment, start `docker compose up -d --wait`, then run `igaming all`. Each phase can be run separately for debugging. The pipeline is an offline batch build. It does not schedule itself or call third-party services.

- Generator rewrites deterministic raw CSVs and manifest.
- Cleaner validates all frames before writing clean output; failures should be corrected before loading.
- Loader runs schema setup, truncation, append, and view installation in a single PostgreSQL transaction. Failure rolls back replacement; successful reruns do not accumulate duplicates.
- Analyzer executes every SQL file, exports results, checks independent financial reconciliation, and regenerates charts/findings. Reports are file outputs; a failed analysis may leave partial report files. Treat a run as successful only after the CLI exits 0 and reconciliation evidence exists.

## Troubleshooting

| Symptom | Action |
|---|---|
| Port 55437 occupied | Change Compose host port and exported DATABASE_URL together |
| Docker daemon unavailable | Start Docker Desktop or your chosen runtime and retry `docker info` |
| Database authentication fails | Check URL and existing volume credentials; retain volume unless you intentionally want to erase local demo data |
| `igaming` command missing | Activate the venv and run `pip install -e '.[dev]'` from the repository |
| Missing CSV or relation | Run generate → clean → load in order |
| Conflicting IDs / orphan keys | Inspect raw files and quarantine; do not suppress validation |
| Dashboard missing results | Run `igaming analyze`; exported CSVs are the dashboard source |
| Integration tests skip | Explicitly export DATABASE_URL for a dedicated loaded database |
| Different generated hashes | Use requirements-lock.txt, the same seed, and compare manifests |

`docker compose down` stops services and retains the volume. Removing a volume erases this demo database; that is not needed for normal reruns. Schema files are intended for a fresh dedicated project database; this project does not implement database migrations for arbitrary existing schemas.

## Release checklist

Run lint, complete generation/load/analysis, all tests with DATABASE_URL, inspect charts/dashboard, and review `reports/validation.md`. Commit source code, small SQL outputs, charts and docs; leave large generated CSVs ignored. CI uploads report artifacts but its success must be verified on GitHub after a push. A local pass is not evidence that remote CI has run.

## Published repository

The portfolio repository is public at https://github.com/smehuyatina/igaming-analytics-platform.

Clone it with:

```bash
git clone https://github.com/smehuyatina/igaming-analytics-platform.git
cd igaming-analytics-platform
```

Follow the README to build the dataset and open the dashboard. Full generated data stays out of Git; SQL results and images are included for preview. GitHub Actions runs the complete pipeline and tests on pushes and pull requests. Inspect the latest run before claiming remote CI success.
