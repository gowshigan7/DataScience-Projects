"""
test_filters.py
===============
Feature : Tests des filtres et du moteur de filtrage.

Description :
    Ce module teste chaque filtre pur (distance, mot-clé) ainsi que le moteur
    d'orchestration apply_filters. Les tests vérifient notamment le contrat
    « retourne la liste inchangée si le paramètre est None/falsy ».

Cas d'usage :
    - Validation du filtrage par distance et par mot-clé
    - Validation du tri par distance et de la limite dans apply_filters

Entrée  : MOCK_FACTS et listes construites à la main
Sortie  : Assertions pytest (pas d'effets de bord)
"""

from geolocation_facts.filters.filter_distance import filter_by_distance
from geolocation_facts.filters.filter_keyword import filter_by_keyword
from geolocation_facts.filters.filter_engine import apply_filters
from geolocation_facts.tests.mock_data import MOCK_FACTS


# ---------------------------------------------------------------------------
# filter_by_distance
# ---------------------------------------------------------------------------

class TestFilterByDistance:
    def test_none_returns_unchanged(self):
        """Un rayon None retourne la liste inchangée."""
        assert filter_by_distance(MOCK_FACTS, None) == MOCK_FACTS

    def test_zero_returns_unchanged(self):
        """Un rayon 0 retourne la liste inchangée."""
        assert filter_by_distance(MOCK_FACTS, 0) == MOCK_FACTS

    def test_filters_out_far_facts(self):
        """Un rayon 5 km exclut le fait situé à 5.8 km."""
        result = filter_by_distance(MOCK_FACTS, 5.0)
        titles = [f["title"] for f in result]
        assert "Basilique du Sacre-Coeur" not in titles
        assert "Tour Eiffel" in titles

    def test_small_radius_keeps_only_closest(self):
        """Un rayon 0.5 km ne garde que les faits très proches."""
        result = filter_by_distance(MOCK_FACTS, 0.5)
        assert all(f["distance_m"] <= 500 for f in result)

    def test_none_distance_excluded_when_active(self):
        """Un fait sans distance connue est exclu si le filtre est actif."""
        facts = [{"title": "X", "distance_m": None}]
        assert filter_by_distance(facts, 1.0) == []


# ---------------------------------------------------------------------------
# filter_by_keyword
# ---------------------------------------------------------------------------

class TestFilterByKeyword:
    def test_none_returns_unchanged(self):
        """Un mot-clé None retourne la liste inchangée."""
        assert filter_by_keyword(MOCK_FACTS, None) == MOCK_FACTS

    def test_empty_string_returns_unchanged(self):
        """Un mot-clé vide retourne la liste inchangée."""
        assert filter_by_keyword(MOCK_FACTS, "   ") == MOCK_FACTS

    def test_matches_title_case_insensitive(self):
        """Le mot-clé correspond au titre, insensible à la casse."""
        result = filter_by_keyword(MOCK_FACTS, "LOUVRE")
        assert len(result) == 1
        assert result[0]["title"] == "Musee du Louvre"

    def test_matches_fact_text(self):
        """Le mot-clé correspond au texte du fait."""
        result = filter_by_keyword(MOCK_FACTS, "napoleon")
        titles = [f["title"] for f in result]
        assert "Les Invalides" in titles
        assert "Arc de triomphe" in titles

    def test_no_match_returns_empty(self):
        """Un mot-clé absent retourne une liste vide."""
        assert filter_by_keyword(MOCK_FACTS, "zzzntropie") == []


# ---------------------------------------------------------------------------
# apply_filters
# ---------------------------------------------------------------------------

class TestApplyFilters:
    def test_no_filters_returns_all_sorted(self):
        """Sans filtre, tous les faits sont retournés, triés par distance."""
        result, total = apply_filters(MOCK_FACTS)
        assert total == len(MOCK_FACTS)
        assert len(result) == len(MOCK_FACTS)
        distances = [f["distance_m"] for f in result]
        assert distances == sorted(distances)

    def test_total_before_is_original_count(self):
        """total_before reflète la taille avant filtrage même si on filtre."""
        result, total = apply_filters(MOCK_FACTS, max_radius_km=0.5)
        assert total == len(MOCK_FACTS)
        assert len(result) < len(MOCK_FACTS)

    def test_limit_applied(self):
        """La limite tronque le résultat final."""
        result, _ = apply_filters(MOCK_FACTS, limit=3)
        assert len(result) == 3

    def test_combined_filters(self):
        """Distance + mot-clé se combinent correctement."""
        result, _ = apply_filters(MOCK_FACTS, keyword="Exposition", max_radius_km=5.0)
        titles = [f["title"] for f in result]
        # "Basilique du Sacre-Coeur" (>5km) exclue ; les faits mentionnant
        # "Exposition" et proches sont conservés.
        assert "Tour Eiffel" in titles
        assert all(f["distance_m"] <= 5000 for f in result)

    def test_closest_first(self):
        """Le fait le plus proche apparaît en premier."""
        result, _ = apply_filters(MOCK_FACTS)
        assert result[0]["title"] == "Tour Eiffel"
