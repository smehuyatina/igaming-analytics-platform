"""Generate a fixed-size event simulation, then inject auditable raw-layer defects."""

import hashlib
import json
import numpy as np
import pandas as pd
from .config import ROOT, START, END, SEED, KEYS

CHANNELS = ["organic", "paid_search", "social", "affiliate", "influencer"]


def generate_frames(n_users=22000, n_sessions=310000, n_deposits=70000, n_withdrawals=22000, seed=SEED):
    rng = np.random.default_rng(seed)
    days = pd.date_range(START, END)
    # Gradual growth, annual winter peak, and weekend uplift in registrations.
    weights = (1 + np.arange(len(days)) / 1600) * (1 + 0.18 * np.cos(2 * np.pi * days.dayofyear / 365.25))
    weights = np.asarray(weights) * np.where(days.dayofweek >= 5, 1.12, 1)
    reg_idx = rng.choice(len(days), n_users, p=np.asarray(weights / weights.sum()))
    ch = rng.choice(CHANNELS, n_users, p=[0.30, 0.25, 0.20, 0.17, 0.08])
    users = pd.DataFrame(
        {
            "user_id": np.arange(1, n_users + 1),
            "registration_date": days[reg_idx],
            "country": rng.choice(["KR", "JP", "TW", "CA", "NZ"], n_users, p=[0.25, 0.30, 0.20, 0.15, 0.10]),
            "acquisition_channel": ch,
            "device_type": rng.choice(["mobile", "desktop", "tablet"], n_users, p=[0.74, 0.21, 0.05]),
            "account_status": rng.choice(["active", "closed", "suspended"], n_users, p=[0.94, 0.04, 0.02]),
        }
    )
    # Latent engagement differs by acquisition channel. 18% never play or transact.
    channel_factor = pd.Series(ch).map(dict(zip(CHANNELS, [1.25, 1.05, 0.75, 0.95, 0.65]))).to_numpy()
    engagement = rng.lognormal(0, 0.85, n_users) * channel_factor
    engagement[rng.random(n_users) < 0.18] = 0
    available = len(days) - reg_idx
    early_mass = 0.72 * (1 - np.exp(-available / 38))
    observable_mass = early_mass + 0.28 * available / len(days)
    # New signups have fewer event opportunities; avoid an artificial final-month surge.
    event_weight = engagement * observable_mass
    prob = event_weight / event_weight.sum()

    def events(n):
        ix = rng.choice(n_users, n, p=prob)
        remaining = len(days) - 1 - reg_idx[ix]
        # Early-life decay plus long-tail returners; bounded by observation end.
        early_age = -38 * np.log1p(-rng.random(n) * (1 - np.exp(-(remaining + 1) / 38)))
        early_probability = early_mass[ix] / observable_mass[ix]
        age = np.where(rng.random(n) < early_probability, early_age, rng.random(n) * (remaining + 1))
        age = np.minimum(age.astype(int), remaining)
        dates = days[reg_idx[ix] + age]
        # Rejection-resample a subset toward weekends and winter (dates never predate signup).
        seasonal = 1 + 0.20 * np.cos(2 * np.pi * dates.dayofyear / 365.25) + 0.12 * (dates.dayofweek >= 5)
        keep = rng.random(n) < np.asarray(seasonal) / 1.32
        for _ in range(3):
            candidates = days[reg_idx[ix] + rng.integers(0, remaining + 1)]
            preference = (
                1
                + 0.20 * np.cos(2 * np.pi * candidates.dayofyear / 365.25)
                + 0.12 * (candidates.dayofweek >= 5)
            )
            accept = (~keep) & (rng.random(n) < np.asarray(preference) / 1.32)
            dates = pd.DatetimeIndex(np.where(accept, candidates.values, dates.values))
            keep |= accept
        return ix, dates

    ix, dates = events(n_sessions)
    games = rng.choice(
        ["slots", "live_casino", "sports", "table_games"], n_sessions, p=[0.48, 0.24, 0.18, 0.10]
    )
    bets = np.maximum(
        1000, np.round(rng.lognormal(10.8, 1.1, n_sessions) * np.sqrt(engagement[ix]) / 100) * 100
    ).astype(int)
    # Session-level payout multiplier: zeros, typical payouts, rare large payouts.
    payout = rng.choice([0.0, 0.75, 1.5, 8.0], n_sessions, p=[0.20, 0.62, 0.16, 0.02])
    game_factor = (
        pd.Series(games)
        .map({"slots": 1.0, "live_casino": 1.02, "sports": 0.98, "table_games": 1.03})
        .to_numpy()
    )
    sessions = pd.DataFrame(
        {
            "session_id": np.arange(1, n_sessions + 1),
            "user_id": ix + 1,
            "game_type": games,
            "session_date": dates,
            "bet_amount_krw": bets,
            "win_amount_krw": np.round(bets * payout * game_factor).astype(int),
            "session_duration_minutes": np.round(np.clip(rng.lognormal(3, 0.6, n_sessions), 1, 240), 2),
        }
    )
    frames = {"users": users, "game_sessions": sessions}
    for table, count, median in [("deposits", n_deposits, 60000), ("withdrawals", n_withdrawals, 100000)]:
        ix, dates = events(count)
        frames[table] = pd.DataFrame(
            {
                table[:-1] + "_id": np.arange(1, count + 1),
                "user_id": ix + 1,
                "amount_krw": np.maximum(
                    1000, np.round(rng.lognormal(np.log(median), 0.8, count) / 1000) * 1000
                ).astype(int),
                "transaction_date": dates,
                "payment_status": rng.choice(["success", "failed", "pending"], count, p=[0.91, 0.06, 0.03]),
            }
        )
    campaigns = []
    for month in pd.date_range(START, END, freq="MS"):
        for channel, cost in zip(CHANNELS[1:], [9000000, 6000000, 7000000, 4000000]):
            campaigns.append(
                [
                    len(campaigns) + 1,
                    channel,
                    month,
                    month + pd.offsets.MonthEnd(0),
                    int(cost * rng.uniform(0.8, 1.2)),
                ]
            )
    campaigns = pd.DataFrame(
        campaigns,
        columns=["campaign_id", "channel", "campaign_start_date", "campaign_end_date", "campaign_cost_krw"],
    )
    lookup = {
        (r.channel, r.campaign_start_date.to_period("M")): r.campaign_id for r in campaigns.itertuples()
    }
    attribution = [
        [r.user_id, lookup[(r.acquisition_channel, r.registration_date.to_period("M"))]]
        for r in users.itertuples()
        if r.acquisition_channel != "organic"
    ]
    frames.update(
        marketing_campaigns=campaigns,
        campaign_attribution=pd.DataFrame(attribution, columns=["user_id", "campaign_id"]),
    )
    return frames


def generate(root=ROOT, **kwargs):
    raw = root / "data/raw"
    raw.mkdir(parents=True, exist_ok=True)
    frames = generate_frames(**kwargs)
    rng = np.random.default_rng(kwargs.get("seed", SEED) + 1)
    manifest = {"seed": kwargs.get("seed", SEED), "start": START, "end": END, "tables": {}}
    for name, frame in frames.items():
        df = frame.copy()
        defects = {}
        if name == "users":
            ix = rng.choice(df.index, max(1, len(df) // 200), replace=False)
            df.loc[ix, "country"] = None
            defects["missing_country"] = len(ix)
        if name in ("deposits", "withdrawals"):
            ix = rng.choice(df.index, max(1, len(df) // 1000), replace=False)
            df.loc[ix, "amount_krw"] *= -1
            defects["negative_amount"] = len(ix)
            ix = rng.choice(df.index, max(1, len(df) // 500), replace=False)
            df.loc[ix, "payment_status"] = " SUCCESS "
            defects["inconsistent_status"] = len(ix)
        duplicates = df.sample(frac=0.002, random_state=SEED)
        if not duplicates.empty:
            df = pd.concat([df, duplicates], ignore_index=True)
        path = raw / f"{name}.csv"
        df.to_csv(path, index=False, date_format="%Y-%m-%d")
        manifest["tables"][name] = {
            "base_rows": len(frame),
            "raw_rows": len(df),
            "exact_duplicates": len(duplicates),
            "injected_defects": defects,
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "key": KEYS[name],
        }
    (raw / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest
