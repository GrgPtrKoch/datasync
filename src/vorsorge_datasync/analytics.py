"""Auswertungen und Datenqualitäts-Checks – alles per SQL.

Zwei Arten von Abfragen:
  1. Kennzahlen (reporting_*): fachliche Auswertungen für den Fachbereich.
  2. Datenqualitäts-Checks (dq_*): finden fehlerhafte Datensätze.

Die SQL steht bewusst als lesbare Konstanten im Code, damit sie sich leicht
prüfen und erweitern lässt.
"""
from __future__ import annotations

import datetime
import sqlite3

# Plausibles Fenster für Geburtsjahre: niemand ist über 120 oder in der Zukunft
# geboren. Dient dem Datenqualitäts-Check "unplausibles Geburtsjahr".
_CURRENT_YEAR = datetime.date.today().year
_MIN_BIRTH_YEAR = _CURRENT_YEAR - 120


# --------------------------------------------------------------------------- #
# 1. Kennzahlen / Reporting
# --------------------------------------------------------------------------- #

def reporting_overview(conn: sqlite3.Connection) -> dict:
    """Gesamtkennzahlen: Anzahl, Summe und Durchschnitt des Sparkapitals."""
    sql = """
        SELECT
            COUNT(*)                        AS anzahl_versicherte,
            ROUND(SUM(savings_capital), 2)  AS summe_kapital,
            ROUND(AVG(savings_capital), 2)  AS durchschnitt_kapital
        FROM members
        WHERE savings_capital >= 0;   -- fehlerhafte Negativwerte ausklammern
    """
    return dict(conn.execute(sql).fetchone())


def reporting_capital_by_decade(conn: sqlite3.Connection) -> list[dict]:
    """Durchschnittliches Sparkapital je Eintritts-Jahrzehnt."""
    sql = """
        SELECT
            (entry_year / 10) * 10          AS jahrzehnt,
            COUNT(*)                        AS anzahl,
            ROUND(AVG(savings_capital), 2)  AS durchschnitt_kapital
        FROM members
        WHERE savings_capital >= 0
        GROUP BY jahrzehnt
        ORDER BY jahrzehnt;
    """
    return [dict(row) for row in conn.execute(sql).fetchall()]


# --------------------------------------------------------------------------- #
# 2. Datenqualitäts-Checks
# --------------------------------------------------------------------------- #

def dq_missing_ahv(conn: sqlite3.Connection) -> list[dict]:
    """Versicherte ohne AHV-Nummer (NULL oder leer)."""
    sql = """
        SELECT member_id, first_name, last_name
        FROM members
        WHERE ahv IS NULL OR TRIM(ahv) = ''
        ORDER BY member_id;
    """
    return [dict(row) for row in conn.execute(sql).fetchall()]


def dq_duplicate_ahv(conn: sqlite3.Connection) -> list[dict]:
    """AHV-Nummern, die mehrfach vorkommen (sollten eindeutig sein)."""
    sql = """
        SELECT ahv, COUNT(*) AS anzahl
        FROM members
        WHERE ahv IS NOT NULL AND TRIM(ahv) <> ''
        GROUP BY ahv
        HAVING COUNT(*) > 1
        ORDER BY ahv;
    """
    return [dict(row) for row in conn.execute(sql).fetchall()]


def dq_implausible_birth_year(conn: sqlite3.Connection) -> list[dict]:
    """Geburtsjahre ausserhalb des plausiblen Fensters."""
    sql = """
        SELECT member_id, first_name, last_name, birth_year
        FROM members
        WHERE birth_year < :min_year OR birth_year > :max_year
        ORDER BY member_id;
    """
    params = {"min_year": _MIN_BIRTH_YEAR, "max_year": _CURRENT_YEAR}
    return [dict(row) for row in conn.execute(sql, params).fetchall()]


def dq_negative_capital(conn: sqlite3.Connection) -> list[dict]:
    """Negatives Sparkapital – fachlich nicht möglich."""
    sql = """
        SELECT member_id, first_name, last_name, savings_capital
        FROM members
        WHERE savings_capital < 0
        ORDER BY member_id;
    """
    return [dict(row) for row in conn.execute(sql).fetchall()]


def run_all_checks(conn: sqlite3.Connection) -> dict[str, list[dict]]:
    """Führt alle DQ-Checks aus und gibt die Treffer je Check zurück.

    Ein leeres Ergebnis bedeutet: Check bestanden, keine Fehler gefunden.
    """
    return {
        "fehlende_ahv": dq_missing_ahv(conn),
        "doppelte_ahv": dq_duplicate_ahv(conn),
        "unplausibles_geburtsjahr": dq_implausible_birth_year(conn),
        "negatives_kapital": dq_negative_capital(conn),
    }
