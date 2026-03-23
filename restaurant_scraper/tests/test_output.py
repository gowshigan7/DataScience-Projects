"""
test_output.py
==============
Feature : Tests des formateurs de sortie (terminal, JSON, CSV).

Description :
    Ce module teste les trois formateurs de sortie disponibles.
    Les tests vérifient :
    - formatter_terminal : affichage correct, gestion liste vide, dry-run
    - formatter_json : sérialisation valide, contenu correct
    - formatter_csv : format CSV valide, colonnes correctes, contenu correct

    Aucun fichier n'est écrit sur le disque grâce au mode dry-run et aux
    tests sur les fonctions de formatage pur (retour string).

Entrée  : Données mockées (sous-ensemble de MOCK_RESTAURANTS)
Sortie  : Assertions pytest (pas d'effets de bord sur le système de fichiers)
"""

import json
import csv
import io
import os
import tempfile
import pytest

from restaurant_scraper.tests.mock_data import MOCK_RESTAURANTS
from restaurant_scraper.output.formatter_terminal import (
    format_terminal,
    _format_rating,
    _format_price,
    _format_distance,
    _format_open,
    _truncate,
)
from restaurant_scraper.output.formatter_json import format_json, save_json
from restaurant_scraper.output.formatter_csv import format_csv, save_csv, CSV_COLUMNS


# Sous-ensemble de 5 restaurants pour les tests
SAMPLE = MOCK_RESTAURANTS[:5]


# ---------------------------------------------------------------------------
# Tests formatter_terminal (helpers)
# ---------------------------------------------------------------------------

class TestTerminalHelpers:
    def test_format_rating_with_value(self):
        """Note valide retourne le format attendu."""
        assert "4.5" in _format_rating(4.5)

    def test_format_rating_none(self):
        """Note None retourne 'N/A'."""
        assert _format_rating(None) == "N/A"

    def test_format_price_level_1(self):
        """Niveau 1 retourne '€'."""
        assert _format_price(1) == "€"

    def test_format_price_level_4(self):
        """Niveau 4 retourne '€€€€'."""
        assert _format_price(4) == "€€€€"

    def test_format_price_none(self):
        """Niveau None retourne 'N/A'."""
        assert _format_price(None) == "N/A"

    def test_format_distance_meters(self):
        """Distance < 1000m retourne le format en mètres."""
        assert _format_distance(320.0) == "320m"

    def test_format_distance_km(self):
        """Distance >= 1000m retourne le format en km."""
        assert _format_distance(1500.0) == "1.5km"

    def test_format_distance_none(self):
        """Distance None retourne 'N/A'."""
        assert _format_distance(None) == "N/A"

    def test_format_open_true(self):
        """Statut True retourne 'Oui'."""
        assert _format_open(True) == "Oui"

    def test_format_open_false(self):
        """Statut False retourne 'Non'."""
        assert _format_open(False) == "Non"

    def test_format_open_none(self):
        """Statut None retourne '?'."""
        assert _format_open(None) == "?"

    def test_truncate_short_string(self):
        """Chaîne courte n'est pas tronquée."""
        assert _truncate("Hello", 10) == "Hello"

    def test_truncate_long_string(self):
        """Chaîne longue est tronquée avec '...'."""
        result = _truncate("Hello World", 8)
        assert len(result) == 8
        assert result.endswith("...")

    def test_truncate_empty_string(self):
        """Chaîne vide retourne chaîne vide."""
        assert _truncate("", 10) == ""


# ---------------------------------------------------------------------------
# Tests format_terminal (affichage complet)
# ---------------------------------------------------------------------------

class TestFormatTerminal:
    def test_displays_count_with_dry_run_param(self, capsys):
        """Le mode dry-run n'affecte pas le tableau (le bandeau est géré par main.py)."""
        format_terminal(SAMPLE, total_before_filter=15, dry_run=True)
        captured = capsys.readouterr()
        assert str(len(SAMPLE)) in captured.out

    def test_displays_count(self, capsys):
        """L'affichage inclut le nombre de résultats."""
        format_terminal(SAMPLE, total_before_filter=15)
        captured = capsys.readouterr()
        assert str(len(SAMPLE)) in captured.out
        assert "15" in captured.out

    def test_empty_list_shows_no_results_message(self, capsys):
        """Une liste vide affiche un message approprié."""
        format_terminal([], total_before_filter=10)
        captured = capsys.readouterr()
        assert "Aucun" in captured.out or "aucun" in captured.out.lower()

    def test_restaurant_names_appear(self, capsys):
        """Les noms des restaurants apparaissent dans l'affichage."""
        format_terminal(SAMPLE[:2])
        captured = capsys.readouterr()
        assert SAMPLE[0]["name"][:5] in captured.out

    def test_no_dry_run_banner_in_formatter(self, capsys):
        """Le formateur terminal n'affiche pas le bandeau DRY-RUN (géré par main.py)."""
        format_terminal(SAMPLE)
        captured = capsys.readouterr()
        assert "DRY-RUN" not in captured.out


# ---------------------------------------------------------------------------
# Tests format_json
# ---------------------------------------------------------------------------

class TestFormatJson:
    def test_returns_valid_json(self):
        """format_json retourne du JSON valide et parseable."""
        json_str = format_json(SAMPLE)
        parsed = json.loads(json_str)
        assert isinstance(parsed, list)
        assert len(parsed) == len(SAMPLE)

    def test_json_contains_all_fields(self):
        """Chaque restaurant dans le JSON contient tous les champs."""
        json_str = format_json(SAMPLE)
        parsed = json.loads(json_str)
        required_keys = ["id", "name", "address", "latitude", "longitude", "source"]
        for r in parsed:
            for key in required_keys:
                assert key in r

    def test_json_preserves_values(self):
        """Les valeurs sont correctement préservées."""
        json_str = format_json(SAMPLE[:1])
        parsed = json.loads(json_str)
        assert parsed[0]["name"] == SAMPLE[0]["name"]
        assert parsed[0]["rating"] == SAMPLE[0]["rating"]

    def test_json_is_indented(self):
        """Le JSON est indenté (lisible)."""
        json_str = format_json(SAMPLE)
        assert "\n" in json_str  # Indenté = multi-lignes

    def test_save_json_dry_run(self, capsys, tmp_path):
        """En dry-run, save_json affiche sans écrire de fichier."""
        filepath = str(tmp_path / "test.json")
        result = save_json(SAMPLE, filepath, dry_run=True)
        assert result == "[DRY-RUN]"
        assert not os.path.exists(filepath)

    def test_save_json_writes_file(self, tmp_path):
        """save_json écrit le fichier correctement."""
        filepath = str(tmp_path / "output.json")
        result = save_json(SAMPLE, filepath, dry_run=False)
        assert result == filepath
        assert os.path.exists(filepath)
        with open(filepath, encoding="utf-8") as f:
            parsed = json.load(f)
        assert len(parsed) == len(SAMPLE)

    def test_empty_list_produces_empty_array(self):
        """Liste vide produit un tableau JSON vide."""
        json_str = format_json([])
        assert json.loads(json_str) == []


# ---------------------------------------------------------------------------
# Tests format_csv
# ---------------------------------------------------------------------------

class TestFormatCsv:
    def test_returns_string(self):
        """format_csv retourne une chaîne."""
        result = format_csv(SAMPLE)
        assert isinstance(result, str)

    def test_csv_has_header(self):
        """Le CSV commence par la ligne d'en-tête."""
        csv_str = format_csv(SAMPLE)
        first_line = csv_str.split("\n")[0]
        for col in ["id", "name", "rating"]:
            assert col in first_line

    def test_csv_correct_column_count(self):
        """Chaque ligne CSV a le bon nombre de colonnes."""
        csv_str = format_csv(SAMPLE)
        reader = csv.DictReader(io.StringIO(csv_str))
        rows = list(reader)
        assert len(rows) == len(SAMPLE)
        for row in rows:
            assert set(CSV_COLUMNS).issubset(set(row.keys()))

    def test_csv_contains_names(self):
        """Les noms des restaurants sont présents dans le CSV."""
        csv_str = format_csv(SAMPLE[:2])
        assert SAMPLE[0]["name"] in csv_str
        assert SAMPLE[1]["name"] in csv_str

    def test_save_csv_dry_run(self, capsys, tmp_path):
        """En dry-run, save_csv affiche sans écrire de fichier."""
        filepath = str(tmp_path / "test.csv")
        result = save_csv(SAMPLE, filepath, dry_run=True)
        assert result == "[DRY-RUN]"
        assert not os.path.exists(filepath)

    def test_save_csv_writes_file(self, tmp_path):
        """save_csv écrit le fichier correctement."""
        filepath = str(tmp_path / "output.csv")
        result = save_csv(SAMPLE, filepath, dry_run=False)
        assert result == filepath
        assert os.path.exists(filepath)
        with open(filepath, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        assert len(rows) == len(SAMPLE)

    def test_empty_list_produces_only_header(self):
        """Liste vide produit un CSV avec uniquement l'en-tête."""
        csv_str = format_csv([])
        lines = [l for l in csv_str.split("\n") if l.strip()]
        assert len(lines) == 1  # Uniquement l'en-tête
