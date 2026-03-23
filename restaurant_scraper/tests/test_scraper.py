"""
test_scraper.py
===============
Feature : Tests des scrapers en mode dry-run.

Description :
    Ce module teste les scrapers en mode dry-run uniquement.
    Aucun appel API réel n'est effectué. Les tests vérifient :
    - Le comportement du mode dry-run (retour liste vide + message)
    - La validité du format des données mockées
    - La méthode make_restaurant de BaseScraper
    - Les utilitaires de géolocalisation (parse_coordinates, calculate_distance)

Cas d'usage :
    - Tests d'intégration légère sans consommation d'API
    - Validation du format de données standardisé
    - Tests de robustesse des parsers

Entrée  : Données mockées, instances de scrapers en dry-run
Sortie  : Assertions pytest (pas d'effets de bord)
"""

import pytest

from restaurant_scraper.scraper.base_scraper import BaseScraper
from restaurant_scraper.scraper.google_places import GooglePlacesScraper
from restaurant_scraper.scraper.overpass_osm import OverpassOSMScraper
from restaurant_scraper.geo.geolocation import parse_coordinates, calculate_distance
from restaurant_scraper.tests.mock_data import MOCK_RESTAURANTS


# ---------------------------------------------------------------------------
# Tests BaseScraper.make_restaurant
# ---------------------------------------------------------------------------

class TestMakeRestaurant:
    def test_make_restaurant_required_fields(self):
        """make_restaurant crée un dict avec tous les champs obligatoires."""
        r = BaseScraper.make_restaurant(
            id="test_001",
            name="Test Restaurant",
            address="123 Rue de Test",
            latitude=48.8566,
            longitude=2.3522,
        )
        required_keys = [
            "id", "name", "address", "latitude", "longitude",
            "rating", "price_level", "cuisine", "is_open_now",
            "distance_m", "phone", "website", "source",
        ]
        for key in required_keys:
            assert key in r

    def test_make_restaurant_default_nones(self):
        """Les champs optionnels sont None par défaut."""
        r = BaseScraper.make_restaurant(
            id="test_002",
            name="Test",
            address="",
            latitude=0.0,
            longitude=0.0,
        )
        assert r["rating"] is None
        assert r["price_level"] is None
        assert r["cuisine"] is None
        assert r["is_open_now"] is None
        assert r["distance_m"] is None
        assert r["phone"] is None
        assert r["website"] is None

    def test_make_restaurant_with_all_fields(self):
        """make_restaurant conserve toutes les valeurs fournies."""
        r = BaseScraper.make_restaurant(
            id="test_003",
            name="Full Restaurant",
            address="456 Avenue Test",
            latitude=48.8566,
            longitude=2.3522,
            rating=4.5,
            price_level=2,
            cuisine="french",
            is_open_now=True,
            distance_m=250.0,
            phone="+33 1 00 00 00 00",
            website="https://example.com",
            source="test",
        )
        assert r["id"] == "test_003"
        assert r["rating"] == 4.5
        assert r["price_level"] == 2
        assert r["cuisine"] == "french"
        assert r["is_open_now"] is True
        assert r["source"] == "test"


# ---------------------------------------------------------------------------
# Tests GooglePlacesScraper en dry-run
# ---------------------------------------------------------------------------

class TestGooglePlacesScraperDryRun:
    def test_dry_run_returns_empty_list(self, capsys):
        """En dry-run, GooglePlacesScraper retourne une liste vide."""
        scraper = GooglePlacesScraper(dry_run=True)
        result = scraper.fetch_restaurants(
            latitude=48.8566,
            longitude=2.3522,
            radius_m=1000,
            limit=20,
        )
        assert result == []

    def test_dry_run_prints_message(self, capsys):
        """En dry-run, un message explicatif est affiché."""
        scraper = GooglePlacesScraper(dry_run=True)
        scraper.fetch_restaurants(48.8566, 2.3522, 1000, 20)
        captured = capsys.readouterr()
        assert "DRY-RUN" in captured.out

    def test_no_api_key_raises_in_live_mode(self):
        """Sans clé API et sans dry-run, une ValueError est levée."""
        scraper = GooglePlacesScraper(api_key="", dry_run=False)
        with pytest.raises(ValueError, match="API"):
            scraper.fetch_restaurants(48.8566, 2.3522, 1000, 20)

    def test_repr(self):
        """La représentation textuelle contient le nom de la classe."""
        scraper = GooglePlacesScraper(dry_run=True)
        assert "GooglePlacesScraper" in repr(scraper)
        assert "dry_run=True" in repr(scraper)


# ---------------------------------------------------------------------------
# Tests OverpassOSMScraper en dry-run
# ---------------------------------------------------------------------------

class TestOverpassOSMScraperDryRun:
    def test_dry_run_returns_empty_list(self, capsys):
        """En dry-run, OverpassOSMScraper retourne une liste vide."""
        scraper = OverpassOSMScraper(dry_run=True)
        result = scraper.fetch_restaurants(
            latitude=48.8566,
            longitude=2.3522,
            radius_m=1000,
            limit=20,
        )
        assert result == []

    def test_dry_run_prints_message(self, capsys):
        """En dry-run, un message explicatif est affiché."""
        scraper = OverpassOSMScraper(dry_run=True)
        scraper.fetch_restaurants(48.8566, 2.3522, 1000, 20)
        captured = capsys.readouterr()
        assert "DRY-RUN" in captured.out

    def test_build_query_contains_coordinates(self):
        """La requête Overpass contient les coordonnées et le rayon."""
        scraper = OverpassOSMScraper()
        query = scraper._build_query(48.8566, 2.3522, 1000, 10)
        assert "48.8566" in query
        assert "2.3522" in query
        assert "1000" in query
        assert "restaurant" in query


# ---------------------------------------------------------------------------
# Tests de géolocalisation
# ---------------------------------------------------------------------------

class TestParseCoordinates:
    def test_valid_coordinates(self):
        """Parse des coordonnées valides 'lat,lng'."""
        result = parse_coordinates("48.8566,2.3522")
        assert result == (48.8566, 2.3522)

    def test_valid_coordinates_with_spaces(self):
        """Parse des coordonnées avec espaces autour de la virgule."""
        result = parse_coordinates("48.8566, 2.3522")
        assert result == (48.8566, 2.3522)

    def test_negative_coordinates(self):
        """Parse des coordonnées négatives (hémisphère sud/ouest)."""
        result = parse_coordinates("-33.8688,151.2093")
        assert result == (-33.8688, 151.2093)

    def test_invalid_string_returns_none(self):
        """Une adresse textuelle retourne None."""
        result = parse_coordinates("Paris, France")
        assert result is None

    def test_invalid_range_returns_none(self):
        """Des coordonnées hors plage retournent None."""
        result = parse_coordinates("91.0,200.0")  # lat > 90, lng > 180
        assert result is None

    def test_single_value_returns_none(self):
        """Une seule valeur retourne None."""
        result = parse_coordinates("48.8566")
        assert result is None


class TestCalculateDistance:
    def test_same_point_is_zero(self):
        """Distance entre un point et lui-même est 0."""
        d = calculate_distance(48.8566, 2.3522, 48.8566, 2.3522)
        assert d == pytest.approx(0.0, abs=1e-6)

    def test_known_distance(self):
        """Distance approximative entre Paris et Lyon (~391km)."""
        d = calculate_distance(48.8566, 2.3522, 45.7640, 4.8357)
        assert 380_000 < d < 400_000  # en mètres

    def test_short_distance(self):
        """Distance courte (quelques centaines de mètres) est cohérente."""
        d = calculate_distance(48.8566, 2.3522, 48.8601, 2.2978)
        assert 100 < d < 5000  # en mètres


# ---------------------------------------------------------------------------
# Tests de validation des données mockées
# ---------------------------------------------------------------------------

class TestMockData:
    def test_mock_restaurants_not_empty(self):
        """Les données mockées ne sont pas vides."""
        assert len(MOCK_RESTAURANTS) > 0

    def test_all_restaurants_have_required_fields(self):
        """Tous les restaurants mockés ont les champs obligatoires."""
        required = ["id", "name", "address", "latitude", "longitude", "source"]
        for r in MOCK_RESTAURANTS:
            for field in required:
                assert field in r, f"Champ '{field}' manquant dans {r.get('name', '?')}"

    def test_all_ids_are_unique(self):
        """Tous les IDs sont uniques."""
        ids = [r["id"] for r in MOCK_RESTAURANTS]
        assert len(ids) == len(set(ids))

    def test_ratings_are_valid(self):
        """Les notes sont dans la plage [0.0, 5.0] ou None."""
        for r in MOCK_RESTAURANTS:
            if r["rating"] is not None:
                assert 0.0 <= r["rating"] <= 5.0

    def test_price_levels_are_valid(self):
        """Les niveaux de prix sont dans [1, 4] ou None."""
        for r in MOCK_RESTAURANTS:
            if r["price_level"] is not None:
                assert 1 <= r["price_level"] <= 4
