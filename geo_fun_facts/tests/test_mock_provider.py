"""
test_mock_provider.py
=======================
Feature : Tests unitaires du fournisseur de fun facts statiques (mock).

Description :
    Teste le filtrage par rayon, le tri par distance et la limite de résultats
    du MockFactProvider. Aucun appel réseau n'est effectué : les données
    viennent exclusivement de MOCK_FUN_FACTS.

Entrée  : Aucune (utilise MOCK_FUN_FACTS)
Sortie  : Assertions pytest
"""

import pytest

from geo_fun_facts.providers.mock_provider import MOCK_FUN_FACTS, MockFactProvider

EIFFEL_TOWER = (48.8584, 2.2945)
REMOTE_OCEAN_POINT = (0.0, -140.0)


class TestMockFactProvider:
    def test_returns_facts_within_radius(self):
        """Un rayon suffisant autour de la Tour Eiffel retourne au moins ce fun fact."""
        provider = MockFactProvider()
        results = provider.get_facts(*EIFFEL_TOWER, radius_km=1.0, limit=10)
        assert any(f["id"] == "mock_001" for f in results)

    def test_excludes_facts_outside_radius(self):
        """Un point isolé en plein océan avec un petit rayon ne retourne rien."""
        provider = MockFactProvider()
        results = provider.get_facts(*REMOTE_OCEAN_POINT, radius_km=10.0, limit=10)
        assert results == []

    def test_results_sorted_by_distance(self):
        """Les résultats sont triés par distance croissante."""
        provider = MockFactProvider()
        results = provider.get_facts(*EIFFEL_TOWER, radius_km=20000, limit=len(MOCK_FUN_FACTS))
        distances = [f["distance_km"] for f in results]
        assert distances == sorted(distances)

    def test_limit_is_respected(self):
        """Le nombre de résultats ne dépasse jamais la limite demandée."""
        provider = MockFactProvider()
        results = provider.get_facts(*EIFFEL_TOWER, radius_km=20000, limit=3)
        assert len(results) == 3

    def test_fact_format_has_required_keys(self):
        """Chaque fun fact contient toutes les clés du format standardisé."""
        provider = MockFactProvider()
        results = provider.get_facts(*EIFFEL_TOWER, radius_km=1.0, limit=1)
        required_keys = [
            "id", "title", "fact", "category", "latitude", "longitude",
            "distance_km", "url", "source",
        ]
        for key in required_keys:
            assert key in results[0]
        assert results[0]["source"] == "mock"
