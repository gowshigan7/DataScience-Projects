"""
test_engine.py
================
Feature : Tests unitaires du point d'entrée principal get_fun_facts.

Description :
    Teste l'orchestration entre résolution de localisation et fournisseur.
    Utilise exclusivement des coordonnées GPS directes ("lat,lng") pour éviter
    tout appel réseau de geocoding, et la source "mock" pour éviter tout appel
    réseau côté fournisseur.

Entrée  : Coordonnées GPS directes, source="mock"
Sortie  : Assertions pytest
"""

import pytest

from geo_fun_facts.engine import get_fun_facts

EIFFEL_TOWER_COORDS = "48.8584,2.2945"


class TestGetFunFacts:
    def test_returns_facts_for_direct_coordinates(self):
        """Des coordonnées directes retournent des fun facts sans appel réseau."""
        results = get_fun_facts(EIFFEL_TOWER_COORDS, radius_km=1.0, limit=5, source="mock")
        assert len(results) >= 1
        assert results[0]["title"] == "Tour Eiffel"

    def test_respects_limit(self):
        """Le nombre de résultats ne dépasse jamais la limite demandée."""
        results = get_fun_facts(EIFFEL_TOWER_COORDS, radius_km=20000, limit=2, source="mock")
        assert len(results) == 2

    def test_default_source_is_mock(self):
        """Sans source précisée, le fournisseur par défaut (mock) est utilisé, sans réseau."""
        results = get_fun_facts(EIFFEL_TOWER_COORDS, radius_km=1.0, limit=5)
        assert all(f["source"] == "mock" for f in results)

    def test_unknown_source_raises(self):
        """Une source inconnue lève une ValueError explicite."""
        with pytest.raises(ValueError):
            get_fun_facts(EIFFEL_TOWER_COORDS, source="scraping_not_implemented_yet")

    def test_unresolvable_location_raises(self, monkeypatch):
        """Une localisation non résolvable (ni coordonnées, ni geocoding réussi) lève une ValueError."""
        monkeypatch.setattr(
            "geo_fun_facts.geo.geolocation._geocode_nominatim", lambda address: None
        )
        with pytest.raises(ValueError):
            get_fun_facts("###invalid-location-string###", source="mock")
