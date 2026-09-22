import sqlite3
from pathlib import Path

import pytest

pytestmark = pytest.mark.sql
SQL_DIR = Path(__file__).resolve().parents[1] / "sql"


def test_join_aggregation_preserves_inventory_invariant(api, lab):
    assert api.reserve(quantity=3).status_code == 201
    cancelled = api.reserve(quantity=2)
    assert cancelled.status_code == 201
    assert api.request("DELETE", f"/api/reservations/{cancelled.json()['id']}").status_code == 200
    with sqlite3.connect(lab.database) as connection:
        rows = connection.execute((SQL_DIR / "stock_reconciliation.sql").read_text()).fetchall()
    assert rows == [("CUP-001", 3, 0, 3), ("TEA-001", 7, 3, 10)]


def test_failed_request_leaves_no_reservation(api, lab):
    assert api.reserve(quantity=11).status_code == 409
    with sqlite3.connect(lab.database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM reservations").fetchone()[0] == 0
        assert connection.execute("SELECT stock FROM products WHERE sku = ?", ("TEA-001",)).fetchone()[0] == 10


def test_window_query_ranks_only_active_reservations(api, lab):
    assert api.reserve(quantity=2, email="first@example.com").status_code == 201
    assert api.reserve(quantity=4, email="second@example.com").status_code == 201
    with sqlite3.connect(lab.database) as connection:
        rows = connection.execute((SQL_DIR / "reservation_ranking.sql").read_text()).fetchall()
    assert rows == [("second@example.com", 4, 1), ("first@example.com", 2, 2)]
