"""Golden fixture: multiple deposits, withdrawals, sessions; late signup; inactive payer; losing player.
Every test rolls back its dedicated-database changes, preserving the loaded portfolio dataset.
"""

import os
import pandas as pd
import pytest
from sqlalchemy import create_engine, text
from igaming.config import ROOT

pytestmark = pytest.mark.integration


@pytest.fixture
def connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        pytest.skip("Set DATABASE_URL to a dedicated, loaded portfolio PostgreSQL database")
    engine = create_engine(url)
    with engine.connect() as conn:
        transaction = conn.begin()
        conn.exec_driver_sql(
            "TRUNCATE analytics.campaign_attribution, analytics.deposits, analytics.withdrawals, "
            "analytics.game_sessions, analytics.marketing_campaigns, analytics.users"
        )
        conn.exec_driver_sql("""
        INSERT INTO analytics.users VALUES
          (1,'2024-01-01','KR','paid_search','mobile','active'),
          (2,'2025-12-30','JP','organic','desktop','active'),
          (3,'2024-01-01','KR','paid_search','mobile','active'),
          (4,'2024-01-02','TW','organic','mobile','closed');
        INSERT INTO analytics.marketing_campaigns VALUES (1,'paid_search','2024-01-01','2024-01-31',1000);
        INSERT INTO analytics.campaign_attribution VALUES (1,1),(3,1);
        INSERT INTO analytics.game_sessions VALUES
          (1,1,'slots','2024-01-02',100,20,5),(2,1,'slots','2024-01-08',200,50,5),
          (3,1,'sports','2024-01-31',300,100,5),(4,2,'slots','2025-12-31',20,30,5),
          (5,4,'slots','2024-01-02',40,20,5);
        INSERT INTO analytics.deposits VALUES
          (1,1,1000,'2024-01-02','success'),(2,1,1000,'2024-01-02','success'),
          (3,3,1000,'2024-01-02','success'),(4,1,9000,'2024-01-02','failed');
        INSERT INTO analytics.withdrawals VALUES
          (1,1,100,'2024-01-03','success'),(2,1,100,'2024-01-03','success');
        """)
        try:
            yield conn
        finally:
            transaction.rollback()
    engine.dispose()


def query(conn, name):
    path = next((ROOT / "sql/queries").glob(name + "*.sql"))
    return pd.read_sql(text(path.read_text()), conn)


def test_all_queries_execute(connection):
    for path in (ROOT / "sql/queries").glob("*.sql"):
        assert not pd.read_sql(text(path.read_text()), connection).empty


def test_financial_grains_and_failed_payments(connection):
    assert query(connection, "04").iloc[0].ggr_krw == 440
    jan = query(connection, "05").iloc[0]
    assert jan.ggr_krw == 450 and jan.bonus_krw == 150 and jan.ngr_krw == 300
    assert query(connection, "11").iloc[0].cac_krw == 500
    cash = query(connection, "15").iloc[0]
    assert cash.deposits_krw == 3000 and cash.withdrawals_krw == 200
    assert cash.deposit_withdrawal_ratio == 15


def test_arpu_and_arppu_coherent_populations(connection):
    assert query(connection, "06").iloc[0].arpu_krw == 225
    row = query(connection, "07").iloc[0]
    assert row.paying_users == 2 and row.payer_ggr_krw == 430 and row.arppu_krw == 215


def test_retention_censoring_and_inactive_users(connection):
    rows = query(connection, "08").set_index("horizon_days")
    assert rows.loc[1, "eligible_users"] == 4
    assert rows.loc[1, "retained_users"] == 2
    assert rows.loc[7, "eligible_users"] == 3
    assert rows.loc[7, "retained_users"] == 1
    assert rows.loc[30, "retained_users"] == 1
    cohorts = query(connection, "09")
    assert not (cohorts.activity_month.astype(str) > "2025-12-01").any()
    assert cohorts.iloc[0].cohort_users == 3


def test_observed_ltv_includes_inactive_payers(connection):
    rows = query(connection, "10").set_index("acquisition_channel")
    assert rows.loc["paid_search", "observed_90d_ltv_krw"] == 140
    assert rows.loc["paid_search", "mature_users"] == 2


def test_segments_reconcile_and_negative_revenue_survives(connection):
    rows = query(connection, "14")
    assert rows.users.sum() == 4 and rows.ggr_krw.sum() == 440
    assert rows.set_index("segment").loc["nonpositive_ggr", "ggr_krw"] == -10


def test_bonus_rounding_and_cap(connection):
    connection.exec_driver_sql("""
    INSERT INTO analytics.deposits VALUES
      (5,1,1010,'2024-02-01','success'),
      (6,1,250001,'2024-02-01','success');
    """)
    row = pd.read_sql(
        text("SELECT bonus_krw FROM analytics.monthly_revenue WHERE month='2024-02-01'"), connection
    )
    assert row.iloc[0].bonus_krw == 10051


def test_first_deposit_window_and_immature_signups(connection):
    connection.exec_driver_sql("""
    INSERT INTO analytics.users VALUES
      (5,'2024-01-01','KR','organic','mobile','active'),
      (6,'2024-01-01','KR','organic','mobile','active'),
      (7,'2024-01-01','KR','organic','mobile','active');
    INSERT INTO analytics.deposits VALUES
      (5,5,1000,'2024-01-07','success'),
      (6,6,1000,'2024-01-08','success'),
      (7,7,1000,'2024-01-01','failed'),
      (8,2,1000,'2025-12-30','success');
    """)
    rows = query(connection, "19").set_index("acquisition_channel")
    assert rows.loc["paid_search", "eligible_users"] == 2
    assert rows.loc["paid_search", "converted_users"] == 2
    assert rows.loc["organic", "eligible_users"] == 4
    assert rows.loc["organic", "converted_users"] == 1
    assert rows.loc["organic", "conversion_pct"] == 25
