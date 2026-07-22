"""
test_wikipedia_provider.py
============================
Feature : Tests unitaires du fournisseur de fun facts Wikipedia.

Description :
    Teste exclusivement la logique de parsing (_parse_response) avec des
    réponses JSON canned, ainsi que le comportement de get_facts lorsque
    l'appel réseau échoue. Aucun appel réseau réel n'est effectué : la
    méthode _fetch_raw est monkeypatchée dans tous les tests.

Entrée  : Réponses JSON factices imitant l'API Wikipedia
Sortie  : Assertions pytest
"""

import pytest

from geo_fun_facts.providers.wikipedia_provider import WikipediaFactProvider

SAMPLE_RESPONSE = {
    "query": {
        "pages": {
            "12345": {
                "pageid": 12345,
                "title": "Tour Eiffel",
                "extract": "La Tour Eiffel est une tour de fer puddlé construite en 1889.",
                "coordinates": [{"lat": 48.8584, "lon": 2.2945, "dist": 120.5}],
            },
            "67890": {
                "pageid": 67890,
                "title": "Sans extrait",
                "coordinates": [{"lat": 48.86, "lon": 2.30, "dist": 500.0}],
            },
        }
    }
}


class TestParseResponse:
    def test_parses_valid_pages(self):
        """Une page avec extrait et coordonnées produit un fun fact standardisé."""
        results = WikipediaFactProvider._parse_response(SAMPLE_RESPONSE, "wikipedia", "fr")
        assert len(results) == 1
        assert results[0]["id"] == "wiki_12345"
        assert results[0]["title"] == "Tour Eiffel"
        assert results[0]["source"] == "wikipedia"
        assert results[0]["distance_km"] == pytest.approx(0.1205)

    def test_skips_pages_without_extract(self):
        """Une page sans extrait est ignorée."""
        results = WikipediaFactProvider._parse_response(SAMPLE_RESPONSE, "wikipedia", "fr")
        assert all(f["title"] != "Sans extrait" for f in results)

    def test_empty_pages_returns_empty_list(self):
        """Une réponse sans page retourne une liste vide."""
        results = WikipediaFactProvider._parse_response({"query": {"pages": {}}}, "wikipedia", "fr")
        assert results == []


class TestGetFacts:
    def test_network_failure_returns_empty_list(self, monkeypatch):
        """Si l'appel réseau échoue (_fetch_raw retourne None), get_facts retourne []."""
        monkeypatch.setattr(WikipediaFactProvider, "_fetch_raw", staticmethod(lambda *a, **k: None))
        provider = WikipediaFactProvider()
        results = provider.get_facts(48.8584, 2.2945, radius_km=1.0, limit=5)
        assert results == []

    def test_successful_fetch_returns_parsed_facts(self, monkeypatch):
        """Un appel réseau simulé avec succès retourne des fun facts parsés."""
        monkeypatch.setattr(
            WikipediaFactProvider, "_fetch_raw", staticmethod(lambda *a, **k: SAMPLE_RESPONSE)
        )
        provider = WikipediaFactProvider()
        results = provider.get_facts(48.8584, 2.2945, radius_km=1.0, limit=5)
        assert len(results) == 1
        assert results[0]["title"] == "Tour Eiffel"
