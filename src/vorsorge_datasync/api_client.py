"""API-Client für die Vorsorge-Schnittstelle.

Kapselt alle HTTP-Details an einer Stelle. Der Rest des Programms arbeitet
nur noch mit Python-Datenstrukturen und muss nichts über HTTP wissen.
"""
from __future__ import annotations

import requests

from . import config


class ApiError(RuntimeError):
    """Wird geworfen, wenn die API nicht erreichbar ist oder Fehler meldet."""


def fetch_members(
    base_url: str | None = None,
    timeout: float | None = None,
) -> list[dict]:
    """Holt alle Versicherten von der API.

    Args:
        base_url: Basis-URL der API. Standard: Wert aus der Konfiguration.
        timeout:  HTTP-Timeout in Sekunden. Standard: Wert aus der Konfiguration.

    Returns:
        Liste von Versicherten-Dicts (so, wie die API sie liefert).

    Raises:
        ApiError: bei Netzwerkfehlern, Timeouts, HTTP-Fehlern oder
                  unerwartetem Antwortformat.
    """
    base_url = base_url if base_url is not None else config.API_BASE_URL
    timeout = timeout if timeout is not None else config.API_TIMEOUT
    url = f"{base_url}/api/v1/members"

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        # Alle requests-Fehler (Timeout, Verbindung, HTTP-Status) in einen
        # klaren, projekteigenen Fehlertyp übersetzen.
        raise ApiError(f"API-Aufruf an {url} fehlgeschlagen: {exc}") from exc

    try:
        payload = response.json()
        members = payload["members"]
    except (ValueError, KeyError, TypeError) as exc:
        raise ApiError(f"Unerwartetes Antwortformat von {url}: {exc}") from exc

    if not isinstance(members, list):
        raise ApiError(f"Feld 'members' ist keine Liste: {type(members)!r}")

    return members
