import datetime
import sqlite3

import pandas as pd
import pytest

from logic import DEFAULT_BUDGET, get_budget, set_budget, week_total


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.execute("CREATE TABLE budgets (month TEXT PRIMARY KEY, monthly REAL NOT NULL, weekly REAL NOT NULL)")
    return c


def test_default_then_edit_midmonth_then_inherit(conn):
    assert get_budget(conn, "2026-11") == DEFAULT_BUDGET
    set_budget(conn, "2026-11", 5000, 1200)
    set_budget(conn, "2026-11", 6000, 1500)  # edited halfway through: overwrites, no duplicate
    assert get_budget(conn, "2026-11") == (6000, 1500)
    assert get_budget(conn, "2026-12") == (6000, 1500)  # new month inherits
    assert get_budget(conn, "2026-10") == DEFAULT_BUDGET  # earlier month unaffected


def test_negative_budget_rejected(conn):
    with pytest.raises(ValueError):
        set_budget(conn, "2026-11", -1, 100)


def test_week_total_is_monday_to_sunday():
    df = pd.DataFrame({"date": ["2026-11-08", "2026-11-09", "2026-11-15", "2026-11-16"],
                       "amount": [1, 10, 100, 1000]})
    assert week_total(df, datetime.date(2026, 11, 11)) == 110  # Mon 9th..Sun 15th
