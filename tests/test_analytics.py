"""Tests für Auswertungen und Datenqualitäts-Checks.

Der Testdatensatz (conftest.py) enthält genau 4 bekannte Fehler – je einen
pro Check. Die Tests prüfen, dass jeder Check genau seinen Fehler findet
und saubere Daten keine Fehlalarme auslösen.
"""
from vorsorge_datasync import analytics, database


def test_overview_excludes_negative_capital(filled_db):
    """Der Überblick klammert den negativen Kapitalwert aus."""
    with database.get_connection(filled_db) as conn:
        ov = analytics.reporting_overview(conn)
    # 7 Datensätze gesamt, 1 mit negativem Kapital -> 6 fliessen ein.
    assert ov["anzahl_versicherte"] == 6


def test_capital_by_decade_groups_correctly(filled_db):
    """Gruppierung je Eintritts-Jahrzehnt liefert plausible Gruppen."""
    with database.get_connection(filled_db) as conn:
        rows = analytics.reporting_capital_by_decade(conn)
    jahrzehnte = {r["jahrzehnt"] for r in rows}
    # Eintrittsjahre 2005,2015,2001,2010,2012,2011 -> Jahrzehnte 2000 & 2010
    assert jahrzehnte == {2000, 2010}


def test_dq_missing_ahv(filled_db):
    with database.get_connection(filled_db) as conn:
        treffer = analytics.dq_missing_ahv(conn)
    assert len(treffer) == 1
    assert treffer[0]["member_id"] == 4


def test_dq_duplicate_ahv(filled_db):
    with database.get_connection(filled_db) as conn:
        treffer = analytics.dq_duplicate_ahv(conn)
    assert len(treffer) == 1
    assert treffer[0]["ahv"] == "756.2222.2222.22"
    assert treffer[0]["anzahl"] == 2


def test_dq_implausible_birth_year(filled_db):
    with database.get_connection(filled_db) as conn:
        treffer = analytics.dq_implausible_birth_year(conn)
    assert len(treffer) == 1
    assert treffer[0]["member_id"] == 6  # Jahrgang 1850


def test_dq_negative_capital(filled_db):
    with database.get_connection(filled_db) as conn:
        treffer = analytics.dq_negative_capital(conn)
    assert len(treffer) == 1
    assert treffer[0]["member_id"] == 7


def test_run_all_checks_counts(filled_db):
    """run_all_checks findet insgesamt genau 4 Verstösse."""
    with database.get_connection(filled_db) as conn:
        checks = analytics.run_all_checks(conn)
    total = sum(len(t) for t in checks.values())
    assert total == 4


def test_clean_data_has_no_issues(db_path):
    """Ein komplett sauberer Datensatz löst keinen einzigen Check aus."""
    sauber = [
        {"member_id": 10, "ahv": "756.1010.1010.10", "first_name": "X", "last_name": "Clean",
         "birth_year": 1980, "entry_year": 2010, "savings_capital": 50000.0},
    ]
    with database.get_connection(db_path) as conn:
        database.init_schema(conn)
        database.upsert_members(conn, sauber)
        checks = analytics.run_all_checks(conn)
    assert all(len(t) == 0 for t in checks.values())
