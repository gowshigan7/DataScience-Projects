"""
test_geolocation.py
====================
Feature : Tests unitaires des utilitaires de géolocalisation.

Description :
    Teste le parsing de coordonnées, la résolution de localisation (sans réseau,
    via des coordonnées directes) et le calcul de distance haversine.
    Aucun appel réseau n'est effectué dans ces tests.

Entrée  : Aucune (valeurs de test en dur)
Sortie  : Assertions pytest
"""

import pytest

from geo_fun_facts.geo.geolocation import (
    calculate_distance_km,
    parse_coordinates,
    resolve_location,
)


class TestParseCoordinates:
    def test_valid_coordinates(self):
        """Une chaîne "lat,lng" valide est correctement parsée."""
        result = parse_coordinates("48.8566,2.3522")
        assert result == (48.8566, 2.3522)

    def test_valid_coordinates_with_spaces(self):
        """Les espaces autour de la virgule sont tolérés."""
        result = parse_coordinates("48.8566, 2.3522")
        assert result == (48.8566, 2.3522)

    def test_address_returns_none(self):
        """Une adresse textuelle (non-coordonnées) retourne None."""
        assert parse_coordinates("Paris, France") is None

    def test_out_of_range_returns_none(self):
        """Des coordonnées hors plage (-90/90, -180/180) retournent None."""
        assert parse_coordinates("200.0,2.3522") is None

    def test_malformed_returns_none(self):
        """Une chaîne mal formée retourne None."""
        assert parse_coordinates("not,coordinates") is None


class TestResolveLocation:
    def test_resolves_direct_coordinates_without_network(self):
        """Des coordonnées directes sont résolues sans appel réseau."""
        result = resolve_location("48.8566,2.3522")
        assert result == (48.8566, 2.3522)


class TestCalculateDistanceKm:
    def test_same_point_is_zero(self):
        """La distance entre un point et lui-même est nulle."""
        assert calculate_distance_km(48.8566, 2.3522, 48.8566, 2.3522) == pytest.approx(0.0)

    def test_paris_to_london_known_distance(self):
        """La distance Paris-Londres est d'environ 344 km (à ±5km près)."""
        distance = calculate_distance_km(48.8566, 2.3522, 51.5074, -0.1278)
        assert distance == pytest.approx(344, abs=5)
