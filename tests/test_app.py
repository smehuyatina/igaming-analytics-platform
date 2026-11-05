from streamlit.testing.v1 import AppTest
from igaming.config import ROOT


def test_dashboard_renders_and_filter_changes_metrics():
    app = AppTest.from_file(str(ROOT / "app.py"), default_timeout=30).run()
    assert not app.exception
    if (ROOT / "reports/results/03_monthly_revenue.csv").exists():
        assert len(app.metric) == 3
        before = app.metric[0].value
        app.select_slider[0].set_value(("2024-01-01", "2024-01-01")).run()
        assert not app.exception
        assert app.metric[0].value != before
    else:
        assert len(app.info) == 1
