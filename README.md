# vorsorge-datasync

Ein kleines, aber vollständiges Python-Projekt, das eine typische Aufgabe im
**Applikations-Management einer Pensionskasse** abbildet: Versichertendaten über
eine REST-Schnittstelle beziehen, in eine SQL-Datenbank laden, auswerten und
auf **Datenqualität** prüfen – vollständig automatisiert und durch
Regressionstests abgesichert.

> Lern- und Demonstrationsprojekt. Die Datenquelle ist eine mitgelieferte
> Mock-API im Stil einer PK/S.Open-Schnittstelle; alle Daten sind frei erfunden.

## Was das Projekt zeigt

| Fähigkeit | Wo im Code |
|---|---|
| Anbindung & Betrieb von **Schnittstellen (APIs)** | `api_client.py` |
| **SQL**-Abfragen für Analysen und Auswertungen | `analytics.py` |
| **Automatisierung** per Skript mit Exit-Codes | `pipeline.py`, `__main__.py` |
| **Datenqualität**: Stammdatenprüfung, Bereinigungslogik | `analytics.py` (dq_*) |
| **Regressionstests** und weitere Testarten | `tests/` (18 Tests) |
| Stabiler Betrieb: Fehlerbehandlung, idempotentes Laden | durchgängig |

## Architektur

```
Mock-API  ──►  api_client  ──►  database (SQLite)  ──►  analytics  ──►  Report
(PK/S.Open-     (HTTP, robust    (Schema + idempotentes   (Kennzahlen +    (CLI,
 ähnlich)        mit Timeout)     Upsert)                  DQ-Checks)       Exit-Code)
                         └──────────── pipeline (Orchestrierung) ───────────┘
```

Der Datenfluss folgt dem **ETL-Muster** (Extract – Load – Transform/Check):
Daten holen, idempotent speichern, prüfen, berichten.

## Schnellstart

```bash
# 1. Abhängigkeiten installieren
pip install -r requirements.txt

# 2. Mock-API in einem Terminal starten
python mock_api/server.py

# 3. In einem zweiten Terminal die Pipeline ausführen
python -m vorsorge_datasync

# Optionen
python -m vorsorge_datasync --help
python -m vorsorge_datasync --api-url http://127.0.0.1:5000 --db vorsorge.db
```

### Exit-Codes

Damit ein Scheduler oder eine CI-Pipeline den Lauf automatisch auswerten kann:

| Code | Bedeutung |
|---|---|
| `0` | Lauf erfolgreich, keine Datenqualitätsfehler |
| `1` | Lauf erfolgreich, aber Datenqualitätsfehler gefunden |
| `2` | technischer Fehler (z. B. API nicht erreichbar) |

## Tests

```bash
pytest
```

Die Tests mocken die HTTP-Aufrufe (Bibliothek `responses`) und nutzen eine
temporäre Datenbank pro Test – sie laufen daher ohne Netzwerk und ohne
laufende Mock-API, schnell und reproduzierbar.

Abgedeckt sind:
- **Unit-Tests** je Datenqualitätscheck (findet jeder Check genau seinen Fehler?)
- **Negativtests** des API-Clients (HTTP 500, kaputtes Antwortformat)
- **Idempotenz-Test** der Datenbank (kein doppeltes Laden)
- **Integrationstest** der gesamten Pipeline (End-to-End, API gemockt)

## Datenqualitäts-Checks

Der mitgelieferte Beispieldatensatz enthält bewusst vier typische Fehler, die
die Checks finden:

- fehlende AHV-Nummer (NULL oder leer)
- doppelte AHV-Nummer (sollte eindeutig sein)
- unplausibles Geburtsjahr (ausserhalb eines sinnvollen Fensters)
- negatives Sparkapital (fachlich unmöglich)

## Projektstruktur

```
vorsorge-datasync/
├── src/vorsorge_datasync/
│   ├── config.py         # zentrale Konfiguration (per Env überschreibbar)
│   ├── api_client.py     # HTTP-Client für die Vorsorge-API
│   ├── database.py       # SQLite-Schema + idempotentes Upsert
│   ├── analytics.py      # SQL-Auswertungen + Datenqualitäts-Checks
│   ├── pipeline.py       # Orchestrierung (ETL)
│   └── __main__.py       # Kommandozeilen-Einstieg
├── mock_api/server.py    # lokale Demo-API (Flask)
├── tests/                # 18 pytest-Tests
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Technologie

Python 3.11+, `requests`, `Flask` (nur Mock-API), `pytest` und `responses`
(Tests). SQLite dient als leichtgewichtiger Ersatz für eine SQL-/Oracle-DB –
die SQL-Logik ist dieselbe.
