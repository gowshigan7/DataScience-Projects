"""
test_source.py
==============
Feature : Tests de la source Wikipedia en mode dry-run et des utilitaires purs.

Description :
    Ce module teste la source de fun facts sans effectuer d'appel réseau réel :
    - Le comportement du mode dry-run (retour liste vide + message)
    - La fabrique make_fact de BaseFactSource
    - Le résumé/troncature d'un extrait (_summarize)
    - La construction d'un fait à partir d'une page brute (_build_fact)
    - La validité du format des données mockées

Cas d'usage :
    - Tests d'intégration légère sans consommation d'API
    - Validation du format de données standardisé

Entrée  : Données mockées, instance de source en dry-run
Sortie  : Assertions pytest (pas d'effets de bord)
"""

from geolocation_facts.source.base_source import BaseFactSource
from geolocation_facts.source.wikipedia_geo import WikipediaGeoSource
from geolocation_facts.config import MAX_FACT_LENGTH
from geolocation_facts.tests.mock_data import MOCK_FACTS


# ---------------------------------------------------------------------------
# Tests BaseFactSource.make_fact
# ---------------------------------------------------------------------------

class TestMakeFact:
    def test_make_fact_required_fields(self):
        """make_fact crée un dict avec tous les champs standardisés."""
        f = BaseFactSource.make_fact(
            id="test_1",
            title="Test",
            fact="Un fait interessant.",
            latitude=48.8584,
            longitude=2.2945,
        )
        required_keys = [
            "id", "title", "fact", "latitude", "longitude",
            "distance_m", "category", "url", "source",
        ]
        for key in required_keys:
            assert key in f

    def test_make_fact_default_nones(self):
        """Les champs optionnels sont None par défaut."""
        f = BaseFactSource.make_fact(
            id="test_2", title="T", fact="F", latitude=0.0, longitude=0.0,
        )
        assert f["distance_m"] is None
        assert f["category"] is None
        assert f["url"] is None
        assert f["source"] == "unknown"

    def test_make_fact_preserves_values(self):
        """make_fact conserve toutes les valeurs fournies."""
        f = BaseFactSource.make_fact(
            id="test_3",
            title="Tour Eiffel",
            fact="Une tour de fer.",
            latitude=48.8584,
            longitude=2.2945,
            distance_m=15.0,
            category="monument",
            url="https://fr.wikipedia.org/?curid=1",
            source="wikipedia",
        )
        assert f["title"] == "Tour Eiffel"
        assert f["distance_m"] == 15.0
        assert f["category"] == "monument"
        assert f["source"] == "wikipedia"


# ---------------------------------------------------------------------------
# Tests WikipediaGeoSource en dry-run
# ---------------------------------------------------------------------------

class TestWikipediaGeoSourceDryRun:
    def test_dry_run_returns_empty_list(self):
        """En dry-run, la source retourne une liste vide."""
        source = WikipediaGeoSource(dry_run=True)
        result = source.fetch_facts(48.8584, 2.2945, 5000, 5)
        assert result == []

    def test_dry_run_prints_message(self, capsys):
        """En dry-run, un message explicatif est affiché."""
        source = WikipediaGeoSource(dry_run=True)
        source.fetch_facts(48.8584, 2.2945, 5000, 5)
        captured = capsys.readouterr()
        assert "DRY-RUN" in captured.out

    def test_repr(self):
        """La représentation textuelle contient le nom de la classe."""
        source = WikipediaGeoSource(dry_run=True)
        assert "WikipediaGeoSource" in repr(source)
        assert "dry_run=True" in repr(source)

    def test_api_url_uses_language(self):
        """L'URL de l'API dépend de la langue demandée."""
        source = WikipediaGeoSource()
        assert "fr.wikipedia.org" in source._api_url("fr")
        assert "en.wikipedia.org" in source._api_url("en")


# ---------------------------------------------------------------------------
# Tests du résumé d'extrait
# ---------------------------------------------------------------------------

class TestSummarize:
    def test_short_text_unchanged(self):
        """Un extrait court est retourné tel quel (espaces normalisés)."""
        text = "Un fait court."
        assert WikipediaGeoSource._summarize(text) == "Un fait court."

    def test_whitespace_normalized(self):
        """Les espaces multiples et sauts de ligne sont normalisés."""
        text = "Un   fait\n\navec   des espaces."
        assert WikipediaGeoSource._summarize(text) == "Un fait avec des espaces."

    def test_long_text_truncated(self):
        """Un extrait long est tronqué à MAX_FACT_LENGTH et suffixé de '…'."""
        text = "mot " * 200  # bien plus long que MAX_FACT_LENGTH
        summary = WikipediaGeoSource._summarize(text)
        assert len(summary) <= MAX_FACT_LENGTH + 1  # +1 pour le caractère '…'
        assert summary.endswith("…")

    def test_truncation_does_not_split_word(self):
        """La troncature se fait sur une frontière de mot."""
        text = "alpha bravo charlie " * 50
        summary = WikipediaGeoSource._summarize(text)
        # Le corps (hors '…') ne se termine pas au milieu d'un mot tronqué.
        assert not summary.rstrip("…").endswith("alph")


# ---------------------------------------------------------------------------
# Tests _build_fact
# ---------------------------------------------------------------------------

class TestBuildFact:
    def test_build_fact_from_page(self):
        """_build_fact assemble un fait standardisé à partir d'une page + extrait."""
        source = WikipediaGeoSource()
        page = {"pageid": 42, "title": "Tour Eiffel", "lat": 48.8584, "lon": 2.2945}
        extracts = {42: "La Tour Eiffel est une tour de fer."}
        fact = source._build_fact(page, extracts, 48.8600, 2.3000, "fr")

        assert fact is not None
        assert fact["id"] == "wikipedia_fr_42"
        assert fact["title"] == "Tour Eiffel"
        assert fact["source"] == "wikipedia"
        assert "wikipedia.org" in fact["url"]
        assert fact["distance_m"] is not None and fact["distance_m"] >= 0

    def test_build_fact_without_extract_returns_none(self):
        """Sans extrait pour la page, _build_fact retourne None."""
        source = WikipediaGeoSource()
        page = {"pageid": 99, "title": "Sans extrait", "lat": 48.0, "lon": 2.0}
        assert source._build_fact(page, {}, 48.0, 2.0, "fr") is None

    def test_build_fact_missing_fields_returns_none(self):
        """Une page incomplète (pas de coordonnées) retourne None."""
        source = WikipediaGeoSource()
        page = {"pageid": 5, "title": "Incomplet"}
        extracts = {5: "Un extrait."}
        assert source._build_fact(page, extracts, 48.0, 2.0, "fr") is None


# ---------------------------------------------------------------------------
# Tests de validation des données mockées
# ---------------------------------------------------------------------------

class TestMockData:
    def test_mock_facts_not_empty(self):
        """Les données mockées ne sont pas vides."""
        assert len(MOCK_FACTS) > 0

    def test_all_facts_have_required_fields(self):
        """Tous les faits mockés ont les champs obligatoires."""
        required = ["id", "title", "fact", "latitude", "longitude", "source"]
        for f in MOCK_FACTS:
            for field in required:
                assert field in f, f"Champ '{field}' manquant dans {f.get('title', '?')}"

    def test_all_ids_are_unique(self):
        """Tous les IDs sont uniques."""
        ids = [f["id"] for f in MOCK_FACTS]
        assert len(ids) == len(set(ids))

    def test_all_facts_are_wikipedia_source(self):
        """Toutes les données mockées proviennent de la source 'wikipedia'."""
        for f in MOCK_FACTS:
            assert f["source"] == "wikipedia"
