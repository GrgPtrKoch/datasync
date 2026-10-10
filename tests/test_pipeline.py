"""Integrationstest: die komplette Pipeline von der (gemockten) API bis zum
Ergebnis-Objekt. Prüft das Zusammenspiel aller Module in einem Durchlauf.
"""
import responses

from vorsorge_datasync.pipeline import run_pipeline

BASE = "http://testserver"
URL = f"{BASE}/api/v1/members"


@responses.activate
def test_full_pipeline(db_path, sample_members):
    """Ein kompletter Lauf lädt die Daten und findet die 4 bekannten Fehler."""
    responses.add(
        responses.GET, URL,
        json={"members": sample_members, "count": len(sample_members)},
        status=200,
    )

    result = run_pipeline(base_url=BASE, db_path=db_path)

    assert result.loaded == len(sample_members)
    assert result.dq_issue_count == 4
    assert result.has_dq_issues is True
    # Kennzahlen vorhanden
    assert result.overview["anzahl_versicherte"] == 6  # ohne Negativwert
    assert len(result.by_decade) == 2


@responses.activate
def test_pipeline_clean_data_no_issues(db_path):
    """Saubere Daten -> keine DQ-Fehler, has_dq_issues False."""
    sauber = [
        {"member_id": 1, "ahv": "756.1111.1111.11", "first_name": "A", "last_name": "Clean",
         "birth_year": 1980, "entry_year": 2010, "savings_capital": 50000.0},
    ]
    responses.add(responses.GET, URL, json={"members": sauber, "count": 1}, status=200)

    result = run_pipeline(base_url=BASE, db_path=db_path)

    assert result.loaded == 1
    assert result.dq_issue_count == 0
    assert result.has_dq_issues is False
