"""
test_filters.py
===============
Feature : Tests unitaires des filtres de restaurants.

Description :
    Ce module contient les tests unitaires pour tous les filtres disponibles.
    Les tests utilisent exclusivement les données mockées de mock_data.py —
    aucun appel API réel n'est effectué.

    Tests couverts :
    - filter_by_rating : note minimale, sans filtre, restaurants sans note
    - filter_by_cuisine : cuisine unique, multi-cuisine, sans filtre
    - filter_by_price : niveau unique, multi-niveaux, sans filtre
    - filter_by_open_now : ouvert, fermé, inconnu
    - filter_by_distance : dans le rayon, hors rayon, sans filtre
    - apply_filters (FilterEngine) : combinaison de filtres, cas limites

Entrée  : Données mockées (mock_data.MOCK_RESTAURANTS)
Sortie  : Assertions pytest (pas d'effets de bord)
"""

import pytest

from restaurant_scraper.tests.mock_data import MOCK_RESTAURANTS
from restaurant_scraper.filters.filter_rating import filter_by_rating
from restaurant_scraper.filters.filter_cuisine import filter_by_cuisine
from restaurant_scraper.filters.filter_price import filter_by_price
from restaurant_scraper.filters.filter_open_now import filter_by_open_now
from restaurant_scraper.filters.filter_distance import filter_by_distance
from restaurant_scraper.filters.filter_engine import apply_filters, FilterEngine


# ---------------------------------------------------------------------------
# Tests filter_by_rating
# ---------------------------------------------------------------------------

class TestFilterByRating:
    def test_no_filter_returns_all(self):
        """Sans filtre (None), tous les restaurants sont retournés."""
        result = filter_by_rating(MOCK_RESTAURANTS, None)
        assert result == MOCK_RESTAURANTS

    def test_zero_rating_returns_all(self):
        """Note = 0.0 (aucun filtre), tous les restaurants sont retournés."""
        result = filter_by_rating(MOCK_RESTAURANTS, 0.0)
        assert result == MOCK_RESTAURANTS

    def test_high_rating_filters_correctly(self):
        """Filtre >= 4.5 : seuls les restaurants avec note >= 4.5 sont conservés."""
        result = filter_by_rating(MOCK_RESTAURANTS, 4.5)
        assert all(r["rating"] is not None and r["rating"] >= 4.5 for r in result)

    def test_excludes_restaurants_without_rating(self):
        """Les restaurants sans note (None) sont exclus quand un filtre est actif."""
        result = filter_by_rating(MOCK_RESTAURANTS, 4.0)
        assert all(r["rating"] is not None for r in result)

    def test_no_results_for_impossible_rating(self):
        """Note > 5.0 : aucun restaurant ne peut correspondre."""
        result = filter_by_rating(MOCK_RESTAURANTS, 5.1)
        assert result == []

    def test_count_with_rating_4(self):
        """Vérifie le nombre correct de restaurants avec note >= 4.0."""
        result = filter_by_rating(MOCK_RESTAURANTS, 4.0)
        expected = [r for r in MOCK_RESTAURANTS if r["rating"] is not None and r["rating"] >= 4.0]
        assert len(result) == len(expected)


# ---------------------------------------------------------------------------
# Tests filter_by_cuisine
# ---------------------------------------------------------------------------

class TestFilterByCuisine:
    def test_no_filter_returns_all(self):
        """Sans filtre (None), tous les restaurants sont retournés."""
        result = filter_by_cuisine(MOCK_RESTAURANTS, None)
        assert result == MOCK_RESTAURANTS

    def test_empty_list_returns_all(self):
        """Liste vide, tous les restaurants sont retournés."""
        result = filter_by_cuisine(MOCK_RESTAURANTS, [])
        assert result == MOCK_RESTAURANTS

    def test_single_cuisine(self):
        """Filtre sur une cuisine unique retourne uniquement cette cuisine."""
        result = filter_by_cuisine(MOCK_RESTAURANTS, ["italian"])
        assert all(r["cuisine"] == "italian" for r in result)
        assert len(result) >= 1

    def test_multi_cuisine(self):
        """Filtre multi-cuisine retourne les deux cuisines."""
        result = filter_by_cuisine(MOCK_RESTAURANTS, ["italian", "japanese"])
        cuisines = {r["cuisine"] for r in result}
        assert cuisines.issubset({"italian", "japanese"})

    def test_case_insensitive(self):
        """Le filtre est insensible à la casse."""
        result_lower = filter_by_cuisine(MOCK_RESTAURANTS, ["italian"])
        result_upper = filter_by_cuisine(MOCK_RESTAURANTS, ["ITALIAN"])
        assert len(result_lower) == len(result_upper)

    def test_unknown_cuisine_returns_empty(self):
        """Cuisine inexistante dans les données retourne une liste vide."""
        result = filter_by_cuisine(MOCK_RESTAURANTS, ["peruvian"])
        assert result == []


# ---------------------------------------------------------------------------
# Tests filter_by_price
# ---------------------------------------------------------------------------

class TestFilterByPrice:
    def test_no_filter_returns_all(self):
        """Sans filtre (None), tous les restaurants sont retournés."""
        result = filter_by_price(MOCK_RESTAURANTS, None)
        assert result == MOCK_RESTAURANTS

    def test_empty_list_returns_all(self):
        """Liste vide, tous les restaurants sont retournés."""
        result = filter_by_price(MOCK_RESTAURANTS, [])
        assert result == MOCK_RESTAURANTS

    def test_single_price_level(self):
        """Filtre sur le niveau 1 retourne uniquement les restaurants €."""
        result = filter_by_price(MOCK_RESTAURANTS, [1])
        assert all(r["price_level"] == 1 for r in result)

    def test_multi_price_levels(self):
        """Filtre multi-niveaux retourne les niveaux demandés."""
        result = filter_by_price(MOCK_RESTAURANTS, [1, 2])
        assert all(r["price_level"] in [1, 2] for r in result)

    def test_expensive_level_4(self):
        """Niveau 4 (€€€€) : seul le restaurant haut de gamme."""
        result = filter_by_price(MOCK_RESTAURANTS, [4])
        assert all(r["price_level"] == 4 for r in result)
        assert len(result) >= 1


# ---------------------------------------------------------------------------
# Tests filter_by_open_now
# ---------------------------------------------------------------------------

class TestFilterByOpenNow:
    def test_no_filter_returns_all(self):
        """Sans filtre (False), tous les restaurants sont retournés."""
        result = filter_by_open_now(MOCK_RESTAURANTS, False)
        assert result == MOCK_RESTAURANTS

    def test_filter_returns_only_open(self):
        """Filtre actif : seuls les restaurants ouverts (True) sont conservés."""
        result = filter_by_open_now(MOCK_RESTAURANTS, True)
        assert all(r["is_open_now"] is True for r in result)

    def test_excludes_unknown_status(self):
        """Les restaurants avec statut inconnu (None) sont exclus."""
        result = filter_by_open_now(MOCK_RESTAURANTS, True)
        assert all(r["is_open_now"] is not None for r in result)

    def test_excludes_closed_restaurants(self):
        """Les restaurants fermés (False) sont exclus."""
        result = filter_by_open_now(MOCK_RESTAURANTS, True)
        assert all(r["is_open_now"] is not False for r in result)


# ---------------------------------------------------------------------------
# Tests filter_by_distance
# ---------------------------------------------------------------------------

class TestFilterByDistance:
    def test_no_filter_returns_all(self):
        """Sans filtre (None), tous les restaurants sont retournés."""
        result = filter_by_distance(MOCK_RESTAURANTS, None)
        assert result == MOCK_RESTAURANTS

    def test_zero_returns_all(self):
        """Rayon = 0 (désactivé), tous les restaurants sont retournés."""
        result = filter_by_distance(MOCK_RESTAURANTS, 0)
        assert result == MOCK_RESTAURANTS

    def test_narrow_radius_filters(self):
        """Rayon de 0.5km : seuls les restaurants à moins de 500m."""
        result = filter_by_distance(MOCK_RESTAURANTS, 0.5)
        assert all(r["distance_m"] <= 500 for r in result)

    def test_excludes_far_restaurants(self):
        """Les restaurants à 2.1km sont exclus avec un rayon de 2km."""
        result = filter_by_distance(MOCK_RESTAURANTS, 2.0)
        assert all(r["distance_m"] <= 2000 for r in result)
        pho = next((r for r in MOCK_RESTAURANTS if r["id"] == "mock_014"), None)
        assert pho is not None and pho["distance_m"] > 2000
        assert pho not in result

    def test_large_radius_returns_all(self):
        """Rayon très grand : tous les restaurants dans les données mockées."""
        result = filter_by_distance(MOCK_RESTAURANTS, 100.0)
        assert len(result) == len(MOCK_RESTAURANTS)


# ---------------------------------------------------------------------------
# Tests apply_filters (moteur combiné)
# ---------------------------------------------------------------------------

class TestApplyFilters:
    def test_no_filters_returns_all_sorted_by_distance(self):
        """Sans filtres, retourne tous les restaurants triés par distance."""
        result, total = apply_filters(MOCK_RESTAURANTS)
        assert total == len(MOCK_RESTAURANTS)
        distances = [r["distance_m"] for r in result]
        assert distances == sorted(distances)

    def test_combined_filters(self):
        """Combinaison : italian + note >= 4.0 + ouvert maintenant."""
        result, _ = apply_filters(
            MOCK_RESTAURANTS,
            min_rating=4.0,
            cuisines=["italian"],
            open_now=True,
        )
        for r in result:
            assert r["cuisine"] == "italian"
            assert r["rating"] is not None and r["rating"] >= 4.0
            assert r["is_open_now"] is True

    def test_limit_applied(self):
        """La limite est respectée."""
        result, _ = apply_filters(MOCK_RESTAURANTS, limit=3)
        assert len(result) <= 3

    def test_total_before_filter_is_correct(self):
        """Le total avant filtrage correspond à la taille initiale."""
        _, total = apply_filters(MOCK_RESTAURANTS, min_rating=4.5)
        assert total == len(MOCK_RESTAURANTS)

    def test_filter_engine_class(self):
        """La classe FilterEngine produit les mêmes résultats que apply_filters."""
        engine = FilterEngine(min_rating=4.0, cuisines=["french"], limit=5)
        result_engine, total_engine = engine.apply(MOCK_RESTAURANTS)
        result_func, total_func = apply_filters(
            MOCK_RESTAURANTS, min_rating=4.0, cuisines=["french"], limit=5
        )
        assert result_engine == result_func
        assert total_engine == total_func

    def test_filter_engine_describe(self):
        """FilterEngine.describe() retourne une description non vide si filtres actifs."""
        engine = FilterEngine(min_rating=4.0, open_now=True)
        description = engine.describe()
        assert "4.0" in description
        assert "ouvert" in description
