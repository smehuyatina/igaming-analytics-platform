import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START = "2024-01-01"
END = "2025-12-31"
SEED = 20261105
TABLES = ["users", "deposits", "withdrawals", "game_sessions", "marketing_campaigns", "campaign_attribution"]
KEYS = dict(zip(TABLES, ["user_id", "deposit_id", "withdrawal_id", "session_id", "campaign_id", "user_id"]))
DATE_COLUMNS = {
    "users": ["registration_date"],
    "deposits": ["transaction_date"],
    "withdrawals": ["transaction_date"],
    "game_sessions": ["session_date"],
    "marketing_campaigns": ["campaign_start_date", "campaign_end_date"],
    "campaign_attribution": [],
}


def database_url():
    return os.getenv("DATABASE_URL", "postgresql+psycopg://portfolio:portfolio_local@localhost:55437/igaming")
