import pytest

from app import seed
from app.services import estimate_service
from fastapi import HTTPException


@pytest.fixture
def db(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    seed.init_db()


def count_runs() -> int:
    from app.db import connect

    conn = connect()
    try:
        return conn.execute("SELECT COUNT(*) c FROM calc_runs").fetchone()["c"]
    finally:
        conn.close()


def test_dry_run_without_waste_matches_old_behavior(db):
    out = estimate_service.run_estimate(1, 1, save=False, note="")
    assert out["rolls"] == 11
    assert out["waste_enabled"] is False
    assert out["waste_pct"] is None
    assert out["order_rolls"] == 11
    assert out["run_id"] is None
    assert count_runs() == 0


def test_dry_run_with_waste_returns_base_and_order(db):
    out = estimate_service.run_estimate(1, 1, False, "", waste_enabled=True, waste_pct=10)
    assert out["rolls"] == 11
    assert out["waste_pct"] == 10.0
    # ceil(11 * 1.1) = 13
    assert out["order_rolls"] == 13
    assert count_runs() == 0


def test_waste_uses_settings_default_when_pct_omitted(db):
    out = estimate_service.run_estimate(1, 1, False, "", waste_enabled=True)
    assert out["waste_pct"] == 10.0
    assert out["order_rolls"] == 13


def test_negative_waste_fails_and_writes_no_history(db):
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_estimate(1, 1, True, "", waste_enabled=True, waste_pct=-5)
    assert exc.value.status_code == 422
    assert count_runs() == 0


def test_over_max_waste_fails_and_writes_no_history(db):
    with pytest.raises(HTTPException) as exc:
        estimate_service.run_estimate(1, 1, True, "", waste_enabled=True, waste_pct=100.1)
    assert exc.value.status_code == 422
    assert count_runs() == 0


def test_saved_run_stores_base_order_and_pct_together(db):
    out = estimate_service.run_estimate(1, 1, True, "下单", waste_enabled=True, waste_pct=10)
    assert out["run_id"] is not None
    from app.repositories import history

    saved = history.list_runs()[0]["result"]
    assert saved["rolls"] == 11
    assert saved["order_rolls"] == 13
    assert saved["waste_pct"] == 10.0
    assert saved["waste_enabled"] is True


def test_saved_run_without_waste_orders_base_rolls(db):
    estimate_service.run_estimate(1, 1, True, "", waste_enabled=False)
    from app.repositories import history

    saved = history.list_runs()[0]["result"]
    assert saved["order_rolls"] == saved["rolls"] == 11
    assert saved["waste_enabled"] is False


def test_changing_default_does_not_rewrite_old_run(db):
    estimate_service.run_estimate(1, 1, True, "旧单", waste_enabled=True, waste_pct=10)
    from app.repositories import history, settings_repo

    old = history.list_runs()[0]["result"]
    assert old["order_rolls"] == 13

    settings_repo.set_default_waste_pct(50)
    # 旧 run 详情仍是写入时的订货卷数
    assert history.list_runs()[0]["result"]["order_rolls"] == 13
    # 新算则按新默认百分比
    new = estimate_service.run_estimate(1, 1, False, "", waste_enabled=True)
    assert new["waste_pct"] == 50.0
    assert new["order_rolls"] == 17
