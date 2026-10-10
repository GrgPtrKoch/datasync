"""Zentrale Konfiguration.

Werte lassen sich per Umgebungsvariable überschreiben – so bleibt der Code
unverändert, egal ob er lokal, in einer Testumgebung oder gegen eine echte
Schnittstelle läuft (12-Factor-Prinzip).
"""
import os

# Basis-URL der Vorsorge-API (Mock-API im Standard).
API_BASE_URL = os.environ.get("VDS_API_BASE_URL", "http://127.0.0.1:5000")

# Timeout für HTTP-Aufrufe in Sekunden – nie ohne Timeout anfragen,
# sonst kann ein hängender Server den ganzen Job blockieren.
API_TIMEOUT = float(os.environ.get("VDS_API_TIMEOUT", "10"))

# Pfad zur lokalen SQLite-Datenbank.
DB_PATH = os.environ.get("VDS_DB_PATH", "vorsorge.db")
