"""Lokale Mock-API, die eine PK/S.Open-ähnliche Schnittstelle simuliert.

Start:  python mock_api/server.py
Dann:   GET http://localhost:5000/api/v1/members

Der Datensatz ist bewusst klein und enthält einige fehlerhafte Einträge
(fehlende AHV-Nummer, Duplikat, unplausibles Geburtsjahr, negatives
Sparkapital), damit die Datenqualitäts-Checks im Projekt etwas zu melden haben.
"""
from flask import Flask, jsonify

app = Flask(__name__)

# Feste Beispieldaten → reproduzierbar für Demos und Tests.
# AHV-Nummer im Schweizer Format 756.XXXX.XXXX.XX
MEMBERS = [
    {"member_id": 1001, "ahv": "756.1234.5678.97", "first_name": "Anna",   "last_name": "Meier",     "birth_year": 1985, "entry_year": 2010, "savings_capital": 142500.00},
    {"member_id": 1002, "ahv": "756.2345.6789.08", "first_name": "Beat",   "last_name": "Müller",    "birth_year": 1972, "entry_year": 2001, "savings_capital": 310250.50},
    {"member_id": 1003, "ahv": "756.3456.7890.19", "first_name": "Carla",  "last_name": "Rossi",     "birth_year": 1990, "entry_year": 2015, "savings_capital":  88000.00},
    {"member_id": 1004, "ahv": "756.4567.8901.20", "first_name": "Daniel", "last_name": "Keller",    "birth_year": 1965, "entry_year": 1992, "savings_capital": 540900.00},
    {"member_id": 1005, "ahv": "756.5678.9012.31", "first_name": "Elena",  "last_name": "Schmid",    "birth_year": 1998, "entry_year": 2022, "savings_capital":  25300.00},
    # --- ab hier bewusste Datenfehler ---
    {"member_id": 1006, "ahv": "",                 "first_name": "Fabio",  "last_name": "Fischer",   "birth_year": 1980, "entry_year": 2008, "savings_capital": 197400.00},  # AHV fehlt
    {"member_id": 1007, "ahv": "756.2345.6789.08", "first_name": "Gina",   "last_name": "Weber",     "birth_year": 1979, "entry_year": 2005, "savings_capital": 203000.00},  # AHV-Duplikat von 1002
    {"member_id": 1008, "ahv": "756.7890.1234.53", "first_name": "Hans",   "last_name": "Baumann",   "birth_year": 1875, "entry_year": 2011, "savings_capital": 150000.00},  # unplausibles Geburtsjahr
    {"member_id": 1009, "ahv": "756.8901.2345.64", "first_name": "Irene",  "last_name": "Graf",      "birth_year": 1988, "entry_year": 2013, "savings_capital":  -1200.00},  # negatives Kapital
]


@app.get("/api/v1/members")
def get_members():
    """Gibt alle Versicherten als JSON zurück."""
    return jsonify({"members": MEMBERS, "count": len(MEMBERS)})


@app.get("/health")
def health():
    """Einfacher Health-Check-Endpoint."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
