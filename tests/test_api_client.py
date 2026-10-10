"""Tests für den API-Client.

Die HTTP-Aufrufe werden mit `responses` gemockt – es läuft kein echter Server.
So sind die Tests schnell, stabil und unabhängig vom Netzwerk.
"""
import pytest
import responses

from vorsorge_datasync import api_client

BASE = "http://testserver"
URL = f"{BASE}/api/v1/members"


@responses.activate
def test_fetch_members_ok():
    """Erfolgsfall: gültige Antwort wird als Liste zurückgegeben."""
    responses.add(
        responses.GET, URL,
        json={"members": [{"member_id": 1, "ahv": "756.1111.1111.11"}], "count": 1},
        status=200,
    )
    members = api_client.fetch_members(base_url=BASE)
    assert len(members) == 1
    assert members[0]["member_id"] == 1


@responses.activate
def test_fetch_members_http_error():
    """HTTP 500 muss in einen ApiError übersetzt werden."""
    responses.add(responses.GET, URL, status=500)
    with pytest.raises(api_client.ApiError):
        api_client.fetch_members(base_url=BASE)


@responses.activate
def test_fetch_members_malformed_payload():
    """Fehlt das Feld 'members', muss ein ApiError kommen."""
    responses.add(responses.GET, URL, json={"unerwartet": True}, status=200)
    with pytest.raises(api_client.ApiError):
        api_client.fetch_members(base_url=BASE)


@responses.activate
def test_fetch_members_not_a_list():
    """Ist 'members' keine Liste, muss ein ApiError kommen."""
    responses.add(responses.GET, URL, json={"members": "kaputt"}, status=200)
    with pytest.raises(api_client.ApiError):
        api_client.fetch_members(base_url=BASE)
