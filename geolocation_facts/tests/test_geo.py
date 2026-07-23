"""
test_geo.py
===========
Feature : Tests des utilitaires de géolocalisation.

Description :
    Ce module teste le parsing de coordonnées, le calcul de distance haversine
    et la résolution de localisation quand des coordonnées directes sont fournies.
    Aucun appel réseau n'est effectué (seul le chemin "coordonnées directes" de
    resolve_location est testé).

Cas d'usage :
    - Validation du parsing "lat,lng"
    - Validation de la formule haversine sur des distances connues

Entrée  : Chaînes de coordonnées, paires de points GPS
Sortie  : Assertions pytest (pas d'effets de bord)
"""

import pytest

from geolocation_facts.geo.geolocation import (
    parse_coordinates,
    calculate_distance,
    resolve_location,
)


class TestParseCoordinates:
    def test_valid_coordinates(self):
        """Parse des coordonnées valides 'lat,lng'."""
        assert parse_coordinates("48.8584,2.2945") == (48.8584, 2.2945)

    def test_valid_coordinates_with_spaces(self):
        """Parse des coordonnées avec espaces autour de la virgule."""
        assert parse_coordinates("48.8584, 2.2945") == (48.8584, 2.2945)

    def test_negative_coordinates(self):
        """Parse des coordonnées négatives (hémisphère sud/ouest)."""
        assert parse_coordinates("-33.8688,151.2093") == (-33.8688, 151.2093)

    def test_invalid_string_returns_none(self):
        """Une adresse textuelle retourne None."""
        assert parse_coordinates("Paris, France") is None

    def test_out_of_range_returns_none(self):
        """Des coordonnées hors plage retournent None."""
        assert parse_coordinates("91.0,200.0") is None

    def test_single_value_returns_none(self):
        """Une seule valeur retourne None."""
        assert parse_coordinates("48.8584") is None


class TestCalculateDistance:
    def test_same_point_is_zero(self):
        """Distance entre un point et lui-même est 0."""
        d = calculate_distance(48.8584, 2.2945, 48.8584, 2.2945)
        assert d == pytest.approx(0.0, abs=1e-6)

    def test_known_distance_paris_lyon(self):
        """Distance approximative entre Paris et Lyon (~391km)."""
        d = calculate_distance(48.8566, 2.3522, 45.7640, 4.8357)
        assert 380_000 < d < 400_000

    def test_short_distance_is_symmetric(self):
        """La distance est symétrique entre deux points."""
        d1 = calculate_distance(48.8584, 2.2945, 48.8606, 2.3376)
        d2 = calculate_distance(48.8606, 2.3376, 48.8584, 2.2945)
        assert d1 == pytest.approx(d2, rel=1e-9)


class TestResolveLocationCoordinates:
    def test_direct_coordinates_no_network(self):
        """resolve_location retourne directement des coordonnées sans réseau."""
        assert resolve_location("48.8584,2.2945") == (48.8584, 2.2945)
