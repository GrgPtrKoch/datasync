"""Gemeinsame pytest-Fixtures für alle Tests.

Eine Fixture stellt einen vorbereiteten Zustand bereit (z. B. eine gefüllte
Test-Datenbank), den mehrere Tests wiederverwenden – ohne Code-Duplikation.
"""
import pytest

from vorsorge_datasync import database

# Kontrollierter Testdatensatz: 3 saubere + 4 fehlerhafte Datensätze.
# Bewusst unabhängig von der Mock-API, damit die Tests exakt wissen,
# welche Fehler vorhanden sind (reproduzierbar).
SAMPLE_MEMBERS = [
    # saubere Datensätze
    {"member_id": 1, "ahv": "756.1111.1111.11", "first_name": "A", "last_name": "Sauber",  "birth_year": 1980, "entry_year": 2005, "savings_capital": 100000.0},
    {"member_id": 2, "ahv": "756.2222.2222.22", "first_name": "B", "last_name": "Korrekt",  "birth_year": 1990, "entry_year": 2015, "savings_capital": 200000.0},
    {"member_id": 3, "ahv": "756.3333.3333.33", "first_name": "C", "last_name": "Richtig",  "birth_year": 1975, "entry_year": 2001, "savings_capital": 300000.0},
    # fehlerhafte Datensätze (je ein Fehlertyp)
    {"member_id": 4, "ahv": "",                 "first_name": "D", "last_name": "OhneAhv",  "birth_year": 1985, "entry_year": 2010, "savings_capital": 150000.0},
    {"member_id": 5, "ahv": "756.2222.2222.22", "first_name": "E", "last_name": "Duplikat", "birth_year": 1988, "entry_year": 2012, "savings_capital": 180000.0},
    {"member_id": 6, "ahv": "756.6666.6666.66", "first_name": "F", "last_name": "AltJahr",  "birth_year": 1850, "entry_year": 2011, "savings_capital": 120000.0},
    {"member_id": 7, "ahv": "756.7777.7777.77", "first_name": "G", "last_name": "Negativ",  "birth_year": 1992, "entry_year": 2018, "savings_capital":  -500.0},
]


@pytest.fixture
def sample_members():
    """Gibt eine Kopie des Testdatensatzes zurück."""
    return [dict(m) for m in SAMPLE_MEMBERS]


@pytest.fixture
def db_path(tmp_path):
    """Pfad zu einer temporären DB-Datei (pro Test frisch, danach weg).

    tmp_path ist eine eingebaute pytest-Fixture: ein eigenes temporäres
    Verzeichnis je Test – so beeinflussen sich Tests nicht gegenseitig.
    """
    return str(tmp_path / "test.db")


@pytest.fixture
def filled_db(db_path, sample_members):
    """Eine mit den Testdaten gefüllte Datenbank; liefert den DB-Pfad."""
    with database.get_connection(db_path) as conn:
        database.init_schema(conn)
        database.upsert_members(conn, sample_members)
    return db_path
