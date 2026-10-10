"""Kommandozeilen-Einstieg: python -m vorsorge_datasync [Optionen]

Exit-Codes (wichtig für geplante/automatisierte Läufe, z. B. in einem Scheduler):
  0  Lauf erfolgreich, keine Datenqualitäts-Fehler
  1  Lauf erfolgreich, aber Datenqualitäts-Fehler gefunden
  2  technischer Fehler (z. B. API nicht erreichbar)
"""
from __future__ import annotations

import argparse
import sys

from . import __version__, config
from .api_client import ApiError
from .pipeline import PipelineResult, run_pipeline


def _format_report(result: PipelineResult) -> str:
    """Baut einen lesbaren Textreport aus dem Pipeline-Ergebnis."""
    lines: list[str] = []
    lines.append("=" * 52)
    lines.append("  VORSORGE-DATASYNC – LAUFBERICHT")
    lines.append("=" * 52)
    lines.append(f"Geladen:           {result.loaded} Versicherte")

    ov = result.overview
    lines.append("")
    lines.append("Kennzahlen (ohne fehlerhafte Datensätze):")
    lines.append(f"  Versicherte:     {ov.get('anzahl_versicherte')}")
    lines.append(f"  Summe Kapital:   {ov.get('summe_kapital'):,.2f} CHF")
    lines.append(f"  Ø Kapital:       {ov.get('durchschnitt_kapital'):,.2f} CHF")

    lines.append("")
    lines.append("Ø Sparkapital je Eintritts-Jahrzehnt:")
    for row in result.by_decade:
        lines.append(
            f"  {row['jahrzehnt']}er: {row['anzahl']:>2} Versicherte, "
            f"Ø {row['durchschnitt_kapital']:,.2f} CHF"
        )

    lines.append("")
    lines.append("Datenqualitäts-Checks:")
    labels = {
        "fehlende_ahv": "Fehlende AHV-Nummer",
        "doppelte_ahv": "Doppelte AHV-Nummer",
        "unplausibles_geburtsjahr": "Unplausibles Geburtsjahr",
        "negatives_kapital": "Negatives Sparkapital",
    }
    for key, treffer in result.checks.items():
        label = labels.get(key, key)
        if not treffer:
            lines.append(f"  [OK]   {label}: keine Auffälligkeiten")
        else:
            lines.append(f"  [WARN] {label}: {len(treffer)} Datensatz/-sätze")
            for t in treffer:
                lines.append(f"           -> {t}")

    lines.append("")
    if result.has_dq_issues:
        lines.append(f"ERGEBNIS: {result.dq_issue_count} Datenqualitäts-Fehler gefunden.")
    else:
        lines.append("ERGEBNIS: Alle Checks bestanden.")
    lines.append("=" * 52)
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vorsorge-datasync",
        description="Versichertendaten von der API laden, speichern und auf "
                    "Datenqualität prüfen.",
    )
    parser.add_argument(
        "--api-url", default=config.API_BASE_URL,
        help=f"Basis-URL der API (Standard: {config.API_BASE_URL})",
    )
    parser.add_argument(
        "--db", default=config.DB_PATH,
        help=f"Pfad zur SQLite-Datenbank (Standard: {config.DB_PATH})",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Haupteinstieg. Gibt den Exit-Code zurück."""
    args = build_parser().parse_args(argv)

    try:
        result = run_pipeline(base_url=args.api_url, db_path=args.db)
    except ApiError as exc:
        print(f"FEHLER: {exc}", file=sys.stderr)
        return 2

    print(_format_report(result))
    # Exit-Code 1, wenn DQ-Fehler gefunden wurden – so kann ein Scheduler
    # oder eine Pipeline automatisch Alarm schlagen.
    return 1 if result.has_dq_issues else 0


if __name__ == "__main__":
    sys.exit(main())
