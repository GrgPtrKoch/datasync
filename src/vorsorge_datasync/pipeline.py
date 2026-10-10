"""Orchestrierung: führt die komplette Datenpipeline in einem Lauf aus.

Ablauf (ETL + Qualitätssicherung):
  1. Extract  – Versicherte von der API holen
  2. Load     – idempotent in die SQLite-Datenbank schreiben
  3. Check    – Datenqualitäts-Checks ausführen
  4. Report   – Kennzahlen und Prüfergebnisse zusammenstellen

Die Funktion gibt ein Ergebnis-Objekt zurück; die Textausgabe und der
Exit-Code liegen in der CLI (__main__.py), damit die Logik testbar bleibt.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from . import analytics, api_client, database


@dataclass
class PipelineResult:
    """Ergebnis eines Pipeline-Laufs."""
    loaded: int = 0
    overview: dict = field(default_factory=dict)
    by_decade: list[dict] = field(default_factory=list)
    checks: dict[str, list[dict]] = field(default_factory=dict)

    @property
    def dq_issue_count(self) -> int:
        """Gesamtzahl gefundener Datenqualitäts-Verstösse über alle Checks."""
        return sum(len(treffer) for treffer in self.checks.values())

    @property
    def has_dq_issues(self) -> bool:
        return self.dq_issue_count > 0


def run_pipeline(
    base_url: str | None = None,
    db_path: str | None = None,
) -> PipelineResult:
    """Führt die gesamte Pipeline aus und liefert ein PipelineResult.

    Args:
        base_url: API-Basis-URL (Standard: Konfiguration).
        db_path:  Pfad zur SQLite-DB (Standard: Konfiguration).
    """
    # 1. Extract
    members = api_client.fetch_members(base_url=base_url)

    with database.get_connection(db_path) as conn:
        database.init_schema(conn)
        # 2. Load
        loaded = database.upsert_members(conn, members)
        # 3. Check + 4. Report
        result = PipelineResult(
            loaded=loaded,
            overview=analytics.reporting_overview(conn),
            by_decade=analytics.reporting_capital_by_decade(conn),
            checks=analytics.run_all_checks(conn),
        )
    return result
