"""Datenbankschicht (SQLite).

Legt das Schema an und schreibt die Versichertendaten idempotent ("Upsert"):
Ein erneuter Lauf mit denselben Daten erzeugt keine Duplikate, sondern
aktualisiert bestehende Datensätze. Das ist für wiederholbare Ladejobs wichtig.
"""
from __future__ import annotations

import sqlite3
from contextlib import contextmanager

from . import config

# DDL: Das Tabellenschema. member_id ist der Primärschlüssel, über den
# das Upsert entscheidet, ob eingefügt oder aktualisiert wird.
SCHEMA = """
CREATE TABLE IF NOT EXISTS members (
    member_id       INTEGER PRIMARY KEY,
    ahv             TEXT,
    first_name      TEXT,
    last_name       TEXT,
    birth_year      INTEGER,
    entry_year      INTEGER,
    savings_capital REAL,
    loaded_at       TEXT DEFAULT (datetime('now'))
);
"""

UPSERT = """
INSERT INTO members
    (member_id, ahv, first_name, last_name, birth_year, entry_year, savings_capital)
VALUES
    (:member_id, :ahv, :first_name, :last_name, :birth_year, :entry_year, :savings_capital)
ON CONFLICT(member_id) DO UPDATE SET
    ahv             = excluded.ahv,
    first_name      = excluded.first_name,
    last_name       = excluded.last_name,
    birth_year      = excluded.birth_year,
    entry_year      = excluded.entry_year,
    savings_capital = excluded.savings_capital,
    loaded_at       = datetime('now');
"""


@contextmanager
def get_connection(db_path: str | None = None):
    """Öffnet eine SQLite-Verbindung als Context-Manager.
    Commit bei Erfolg, Rollback bei Fehler, Verbindung wird immer geschlossen.
    """
    db_path = db_path if db_path is not None else config.DB_PATH
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Zugriff auf Spalten per Name
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_schema(conn: sqlite3.Connection) -> None:
    """Legt die Tabelle an, falls sie noch nicht existiert."""
    conn.executescript(SCHEMA)


def upsert_members(conn: sqlite3.Connection, members: list[dict]) -> int:
    """Schreibt die Versicherten idempotent in die Datenbank.
    Returns:
        Anzahl der verarbeiteten Datensätze.
    """
    # Nur die bekannten Felder übernehmen; fehlende Schlüssel auf None setzen,
    # damit ein unvollständiger Datensatz den Lauf nicht abbricht.
    columns = ("member_id", "ahv", "first_name", "last_name",
               "birth_year", "entry_year", "savings_capital")
    rows = [{col: m.get(col) for col in columns} for m in members]
    conn.executemany(UPSERT, rows)
    return len(rows)


def count_members(conn: sqlite3.Connection) -> int:
    """Zählt die Datensätze in der Tabelle (praktisch für Tests/Checks)."""
    cur = conn.execute("SELECT COUNT(*) AS n FROM members;")
    return cur.fetchone()["n"]
