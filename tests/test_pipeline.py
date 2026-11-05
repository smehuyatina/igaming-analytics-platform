import json
import pandas as pd
import pytest
from igaming.generate import generate_frames, generate
from igaming.clean import clean_frame, clean, validate_relationships


@pytest.fixture(scope="module")
def frames():
    return generate_frames(n_users=250, n_sessions=1800, n_deposits=450, n_withdrawals=150, seed=42)


def test_generator_is_reproducible_and_dated(frames):
    again = generate_frames(n_users=250, n_sessions=1800, n_deposits=450, n_withdrawals=150, seed=42)
    for name in frames:
        pd.testing.assert_frame_equal(frames[name], again[name])
    validate_relationships(frames)
    assert len(frames["users"]) == 250
    assert len(frames["game_sessions"]) == 1800
    assert len(set(frames["users"].user_id) - set(frames["game_sessions"].user_id)) > 0


def test_raw_clean_accounting_and_determinism(tmp_path):
    params = dict(n_users=250, n_sessions=1800, n_deposits=450, n_withdrawals=150, seed=42)
    first = generate(tmp_path, **params)
    second = generate(tmp_path, **params)
    assert first == second
    report = clean(tmp_path)
    for counts in report.values():
        assert (
            counts["raw_rows"] == counts["duplicate_rows"] + counts["quarantined_rows"] + counts["clean_rows"]
        )
    assert report["users"]["unknown_country_rows"] > 0
    assert report["deposits"]["quarantined_rows"] > 0
    assert json.loads((tmp_path / "data/clean/quality_report.json").read_text()) == report


def test_normalization_duplicates_and_invalid_amount():
    raw = pd.DataFrame(
        {
            "deposit_id": [1, 1, 2, 3],
            "user_id": [1, 1, 2, 2],
            "amount_krw": [1000, 1000, -20, 2000],
            "transaction_date": ["2024-01-01"] * 4,
            "payment_status": [" SUCCESS ", " SUCCESS ", "success", "nonsense"],
        }
    )
    good, bad, duplicates = clean_frame("deposits", raw)
    assert duplicates == 1
    assert len(bad) == 2
    assert good.payment_status.tolist() == ["success"]


def test_conflicting_duplicate_key_fails():
    raw = pd.DataFrame(
        {
            "deposit_id": [1, 1],
            "user_id": [1, 1],
            "amount_krw": [1000, 2000],
            "transaction_date": ["2024-01-01"] * 2,
            "payment_status": ["success"] * 2,
        }
    )
    with pytest.raises(ValueError, match="Conflicting primary keys"):
        clean_frame("deposits", raw)


def test_orphan_and_pre_registration_events_fail(frames):
    copy = {name: df.copy() for name, df in frames.items()}
    copy["deposits"].loc[0, "user_id"] = 999999
    with pytest.raises(ValueError, match="Orphan"):
        validate_relationships(copy)
    copy = {name: df.copy() for name, df in frames.items()}
    copy["deposits"].loc[0, "transaction_date"] = pd.Timestamp("2023-12-31")
    with pytest.raises(ValueError, match="before registration"):
        validate_relationships(copy)
