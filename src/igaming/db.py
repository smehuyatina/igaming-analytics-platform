"""Replace this dedicated portfolio schema atomically; never infer SQL column types."""

import pandas as pd
from sqlalchemy import create_engine, text
from .config import ROOT, TABLES, DATE_COLUMNS, database_url
from .clean import validate_relationships


def engine():
    return create_engine(database_url(), pool_pre_ping=True)


def load(root=ROOT):
    frames = {
        name: pd.read_csv(root / f"data/clean/{name}.csv", parse_dates=DATE_COLUMNS[name]) for name in TABLES
    }
    validate_relationships(frames)
    with engine().begin() as conn:
        conn.exec_driver_sql((root / "sql/schema.sql").read_text())
        conn.execute(
            text(
                "TRUNCATE analytics.campaign_attribution, analytics.deposits, analytics.withdrawals, "
                "analytics.game_sessions, analytics.marketing_campaigns, analytics.users"
            )
        )
        for name in [
            "users",
            "marketing_campaigns",
            "campaign_attribution",
            "deposits",
            "withdrawals",
            "game_sessions",
        ]:
            frames[name].to_sql(
                name,
                conn,
                schema="analytics",
                if_exists="append",
                index=False,
                chunksize=5000,
                method="multi",
            )
        conn.exec_driver_sql((root / "sql/views.sql").read_text())
    return {name: len(frame) for name, frame in frames.items()}
