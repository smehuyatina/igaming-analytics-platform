"""Conservative cleaning: normalize known fields, quarantine invalid facts, fail on conflicting keys."""

import json
import pandas as pd
from .config import ROOT, TABLES, KEYS, DATE_COLUMNS, START, END

ENUMS = {
    "country": {"KR", "JP", "TW", "CA", "NZ", "UNKNOWN"},
    "acquisition_channel": {"organic", "paid_search", "social", "affiliate", "influencer"},
    "channel": {"paid_search", "social", "affiliate", "influencer"},
    "device_type": {"mobile", "desktop", "tablet"},
    "account_status": {"active", "closed", "suspended"},
    "game_type": {"slots", "live_casino", "sports", "table_games"},
    "payment_status": {"success", "failed", "pending"},
}


def clean_frame(name, raw):
    df = raw.drop_duplicates().copy()
    duplicates = len(raw) - len(df)
    if name == "users":
        df["country"] = df.country.fillna("UNKNOWN").str.strip().str.upper()
    for col in df.columns:
        if col in ENUMS and col != "country":
            df[col] = df[col].astype("string").str.strip().str.lower()
    # Formatting variants can produce identical keys only after normalization.
    df = df.drop_duplicates()
    duplicates = len(raw) - len(df)
    if df[KEYS[name]].duplicated().any():
        raise ValueError(f"Conflicting primary keys in {name}; manual review required")
    valid = pd.Series(True, index=df.index)
    for col in df.columns:
        if col.endswith("_id"):
            df[col] = pd.to_numeric(df[col], errors="coerce")
            valid &= df[col].notna() & (df[col] > 0) & (df[col] % 1 == 0)
        if col in ENUMS:
            valid &= df[col].isin(ENUMS[col])
        if col.endswith("_krw") or col == "session_duration_minutes":
            df[col] = pd.to_numeric(df[col], errors="coerce")
            valid &= df[col].notna() & (df[col] >= 0)
            if col.endswith("_krw"):
                valid &= df[col] % 1 == 0
        if col in DATE_COLUMNS[name]:
            df[col] = pd.to_datetime(df[col], errors="coerce")
            valid &= df[col].between(START, END)
    if name == "game_sessions":
        valid &= (df.bet_amount_krw > 0) & df.session_duration_minutes.between(1, 240)
    if name in ("deposits", "withdrawals"):
        valid &= df.amount_krw > 0
    if name == "marketing_campaigns":
        valid &= df.campaign_end_date >= df.campaign_start_date
    good = df[valid].copy()
    for col in good:
        if col.endswith("_id") or col.endswith("_krw"):
            good[col] = good[col].astype("int64")
    return good, df[~valid].copy(), duplicates


def validate_relationships(frames):
    users = frames["users"].set_index("user_id")
    for name in ["deposits", "withdrawals", "game_sessions", "campaign_attribution"]:
        df = frames[name]
        if not df.user_id.isin(users.index).all():
            raise ValueError(f"Orphan user in {name}")
        if name != "campaign_attribution":
            datecol = DATE_COLUMNS[name][0]
            if (df[datecol].to_numpy() < df.user_id.map(users.registration_date).to_numpy()).any():
                raise ValueError(f"Event before registration: {name}")
    a = frames["campaign_attribution"].merge(
        frames["marketing_campaigns"], on="campaign_id", validate="many_to_one"
    )
    if len(a) != len(frames["campaign_attribution"]):
        raise ValueError("Orphan campaign")
    registered = a.user_id.map(users.registration_date)
    if not (registered.between(a.campaign_start_date, a.campaign_end_date)).all():
        raise ValueError("Attribution outside campaign window")
    if not (a.channel == a.user_id.map(users.acquisition_channel)).all():
        raise ValueError("Channel mismatch")


def clean(root=ROOT):
    frames, rejects, report = {}, {}, {}
    for name in TABLES:
        raw = pd.read_csv(root / f"data/raw/{name}.csv")
        good, bad, duplicates = clean_frame(name, raw)
        frames[name], rejects[name] = good, bad
        report[name] = {
            "raw_rows": len(raw),
            "duplicate_rows": duplicates,
            "quarantined_rows": len(bad),
            "clean_rows": len(good),
            "unknown_country_rows": int((good.country == "UNKNOWN").sum()) if name == "users" else 0,
        }
    validate_relationships(frames)
    out = root / "data/clean"
    out.mkdir(parents=True, exist_ok=True)
    for name in TABLES:
        frames[name].to_csv(out / f"{name}.csv", index=False, date_format="%Y-%m-%d")
        rejects[name].to_csv(out / f"{name}_quarantine.csv", index=False, date_format="%Y-%m-%d")
    (out / "quality_report.json").write_text(json.dumps(report, indent=2))
    return report
