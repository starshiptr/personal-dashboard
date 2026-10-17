"""Regression tests from the 2026-10-17 red-team run. Each one failed against the old app.py.

Every test chdirs into a fresh tmp dir, so app.py's relative "dashboard.db" is a throwaway file.
"""
import sqlite3
from pathlib import Path

import pandas as pd
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from streamlit.testing.v1 import AppTest

from logic import invalid_rows, month_rows, save_table, valid_month

APP = str(Path(__file__).resolve().parents[1] / "app.py")
COLS = ["date", "amount", "category", "note"]


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    vault = tmp_path / "vault"
    (vault / "finance").mkdir(parents=True)
    (vault / "todolist").mkdir()
    (vault / "todolist" / "active.md").write_text("# tasks", encoding="utf-8")
    monkeypatch.setenv("VAULT_ROOT", str(vault))
    return tmp_path


def seed(rows):
    conn = sqlite3.connect("dashboard.db")
    conn.execute("CREATE TABLE IF NOT EXISTS spending (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 " date TEXT NOT NULL, amount REAL NOT NULL, category TEXT NOT NULL, note TEXT)")
    conn.executemany("INSERT INTO spending (date, amount, category, note) VALUES (?,?,?,?)", rows)
    conn.commit()
    conn.close()


def table():
    conn = sqlite3.connect("dashboard.db")
    out = pd.read_sql_query("SELECT * FROM spending ORDER BY id", conn)
    conn.close()
    return out


def run(at):
    return at.run(timeout=60)


def export_button(at, key=None):
    return next(b for b in at.button if b.label == "Export this month to vault" and b.key == key)


# A blank cell in a new row must roll the whole save back.
def test_save_with_empty_cell_keeps_existing_rows(sandbox):
    seed([("2026-10-01", 100.0, "Food & Dining", "a"), ("2026-10-02", 200.0, "Transport", "b")])
    edited = table()
    edited.loc[len(edited)] = [None, "2026-10-03", float("nan"), "Misc", None]
    conn = sqlite3.connect("dashboard.db")
    with pytest.raises(sqlite3.IntegrityError):
        save_table(conn, "spending", edited, COLS)
    conn.close()
    assert len(table()) == 2


# A no-op save must keep ids; edits update in place; removed rows are deleted.
def test_save_preserves_ids(sandbox):
    seed([("2026-10-01", 100.0, "Food & Dining", "a"), ("2026-10-02", 200.0, "Transport", "b")])
    before = table()
    conn = sqlite3.connect("dashboard.db")
    save_table(conn, "spending", before, COLS)
    assert table()["id"].tolist() == before["id"].tolist()
    edited = before.iloc[[1]].copy()
    edited.loc[edited.index[0], "amount"] = 250.0
    save_table(conn, "spending", edited, COLS)
    conn.close()
    after = table()
    assert after["id"].tolist() == [2] and after["amount"].tolist() == [250.0]


dates = st.dates(min_value=pd.Timestamp("2025-01-01").date(), max_value=pd.Timestamp("2027-12-31").date())


# The month filter counts exactly that month: "2026-1" must not count Oct-Dec, "" must count nothing.
@settings(max_examples=300, deadline=None)
@given(ds=st.lists(dates, min_size=1, max_size=20),
       month=st.one_of(st.just(""), st.text(alphabet="0123456789-", max_size=7)))
def test_month_total_only_counts_that_month(ds, month):
    df = pd.DataFrame({"date": [d.isoformat() for d in ds], "amount": [1.0] * len(ds)})
    total = month_rows(df, month)["amount"].sum()
    expected = sum(1.0 for d in ds if d.strftime("%Y-%m") == month)
    assert total == expected


def test_valid_month():
    assert valid_month("2026-10")
    for bad in ["", "2026-1", "2026-13", "2026-00", "26-10", "2026-10-01", None]:
        assert not valid_month(bad)


# Exporting October must not replace September's export.
def test_export_keeps_previous_month(sandbox):
    seed([("2026-09-05", 500.0, "Food & Dining", ""), ("2026-10-05", 700.0, "Transport", "")])
    at = run(AppTest.from_file(APP))
    for month in ["2026-09", "2026-10"]:
        at.sidebar.text_input[0].set_value(month)
        run(at)
        export_button(at).click()
        run(at)
    finance = sandbox / "vault" / "finance"
    assert "2026-09" in (finance / "dashboard-export-2026-09.md").read_text(encoding="utf-8")
    assert "2026-10" in (finance / "dashboard-export-2026-10.md").read_text(encoding="utf-8")


# Export must create a missing vault folder instead of crashing.
def test_export_without_vault_dir_does_not_crash(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("VAULT_ROOT", raising=False)
    at = run(AppTest.from_file(APP))
    export_button(at).click()
    run(at)
    assert not at.exception, at.exception[0].message


def test_empty_db_boots(sandbox):
    at = run(AppTest.from_file(APP))
    assert not at.exception
    export_button(at, key="export_fitness").click()
    run(at)
    assert not at.exception


def test_fitness_note_cannot_inject_markdown(sandbox):
    run(AppTest.from_file(APP))  # creates tables
    conn = sqlite3.connect("dashboard.db")
    month = pd.Timestamp.now().strftime("%Y-%m")
    conn.execute("INSERT INTO Fitness_Log (date, workout_day, exercise, weight, note) VALUES (?,?,?,?,?)",
                 (f"{month}-01", "Push", "OHP", 40.0, "ok\n\n## INJECTED HEADING\n- [ ] fake task"))
    conn.commit()
    conn.close()
    at = run(AppTest.from_file(APP))
    export_button(at, key="export_fitness").click()
    run(at)
    text = (sandbox / "vault" / "finance" / f"fitness-export-{month}.md").read_text(encoding="utf-8")
    assert "\n## INJECTED HEADING" not in text


# Non-ISO dates and negative amounts must block the save.
def test_editor_values_validated_before_save():
    edited = pd.DataFrame({"id": [1, None, None], "date": ["2026-10-01", "17/10/2026", "2026-10-05"],
                           "amount": [100.0, 400.0, -500.0], "category": ["Misc"] * 3, "note": [None] * 3})
    problems = invalid_rows(edited, "amount")
    assert len(problems) == 2
    assert "17/10/2026" in problems[0] and "Row 3" in problems[1]
