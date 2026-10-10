"""Tests für die Datenbankschicht: Schema, Upsert, Idempotenz."""
from vorsorge_datasync import database


def test_init_and_upsert(db_path, sample_members):
    """Nach dem Laden stehen alle Datensätze in der DB."""
    with database.get_connection(db_path) as conn:
        database.init_schema(conn)
        n = database.upsert_members(conn, sample_members)
        assert n == len(sample_members)
        assert database.count_members(conn) == len(sample_members)


def test_upsert_is_idempotent(db_path, sample_members):
    """Zweimaliges Laden derselben Daten erzeugt keine Duplikate."""
    with database.get_connection(db_path) as conn:
        database.init_schema(conn)
        database.upsert_members(conn, sample_members)
        database.upsert_members(conn, sample_members)  # zweiter Lauf
        assert database.count_members(conn) == len(sample_members)


def test_upsert_updates_existing(db_path, sample_members):
    """Ein geänderter Datensatz wird aktualisiert, nicht dupliziert."""
    with database.get_connection(db_path) as conn:
        database.init_schema(conn)
        database.upsert_members(conn, sample_members)

        geaendert = dict(sample_members[0])
        geaendert["savings_capital"] = 999999.0
        database.upsert_members(conn, [geaendert])

        row = conn.execute(
            "SELECT savings_capital FROM members WHERE member_id = ?",
            (geaendert["member_id"],),
        ).fetchone()
        assert row["savings_capital"] == 999999.0
        assert database.count_members(conn) == len(sample_members)


def test_missing_field_becomes_null(db_path):
    """Ein fehlendes Feld im Eingabe-Dict darf den Lauf nicht abbrechen."""
    unvollstaendig = [{"member_id": 42, "ahv": "756.4242.4242.42"}]  # Rest fehlt
    with database.get_connection(db_path) as conn:
        database.init_schema(conn)
        database.upsert_members(conn, unvollstaendig)
        row = conn.execute(
            "SELECT last_name, savings_capital FROM members WHERE member_id = 42"
        ).fetchone()
        assert row["last_name"] is None
        assert row["savings_capital"] is None
