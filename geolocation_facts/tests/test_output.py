"""
test_output.py
==============
Feature : Tests des formatters (terminal et JSON).

Description :
    Ce module teste l'affichage terminal et l'export JSON. Aucun fichier n'est
    écrit sur disque : l'export JSON est testé en mode dry-run (qui n'écrit pas)
    et via la fonction pure format_json.

Cas d'usage :
    - Validation de la sérialisation JSON
    - Validation que le mode dry-run n'écrit aucun fichier
    - Validation de l'affichage terminal (titres, bandeau dry-run)

Entrée  : MOCK_FACTS
Sortie  : Assertions pytest (pas d'effets de bord, pas de fichier écrit)
"""

import json

from geolocation_facts.output.formatter_json import format_json, save_json
from geolocation_facts.output.formatter_terminal import format_terminal, _format_distance
from geolocation_facts.tests.mock_data import MOCK_FACTS


# ---------------------------------------------------------------------------
# formatter_json
# ---------------------------------------------------------------------------

class TestFormatJson:
    def test_produces_valid_json(self):
        """format_json produit une chaîne JSON valide et ré-parsable."""
        text = format_json(MOCK_FACTS)
        parsed = json.loads(text)
        assert len(parsed) == len(MOCK_FACTS)
        assert parsed[0]["title"] == MOCK_FACTS[0]["title"]

    def test_unicode_preserved(self):
        """Les caractères accentués ne sont pas échappés (ensure_ascii=False)."""
        facts = [{"title": "Café", "fact": "Un café éphémère."}]
        text = format_json(facts)
        assert "Café" in text


class TestSaveJsonDryRun:
    def test_dry_run_does_not_write(self, tmp_path, capsys):
        """En dry-run, save_json n'écrit aucun fichier."""
        target = tmp_path / "facts.json"
        result = save_json(MOCK_FACTS, str(target), dry_run=True)
        assert result == "[DRY-RUN]"
        assert not target.exists()

    def test_dry_run_prints_json(self, capsys):
        """En dry-run, le JSON est affiché dans stdout."""
        save_json(MOCK_FACTS, "output/facts.json", dry_run=True)
        captured = capsys.readouterr()
        assert "DRY-RUN" in captured.out
        assert MOCK_FACTS[0]["title"] in captured.out


# ---------------------------------------------------------------------------
# formatter_terminal
# ---------------------------------------------------------------------------

class TestFormatDistance:
    def test_meters(self):
        """Une distance < 1000 m est affichée en mètres."""
        assert _format_distance(320.0) == "320m"

    def test_kilometers(self):
        """Une distance >= 1000 m est affichée en kilomètres."""
        assert _format_distance(1500.0) == "1.5km"

    def test_none(self):
        """Une distance inconnue est affichée 'N/A'."""
        assert _format_distance(None) == "N/A"


class TestFormatTerminal:
    def test_prints_titles(self, capsys):
        """L'affichage terminal contient les titres des faits."""
        format_terminal(MOCK_FACTS, total_before_filter=len(MOCK_FACTS))
        captured = capsys.readouterr()
        assert "Tour Eiffel" in captured.out

    def test_dry_run_banner(self, capsys):
        """Le bandeau [DRY-RUN] apparaît en mode dry-run."""
        format_terminal(MOCK_FACTS, total_before_filter=len(MOCK_FACTS), dry_run=True)
        captured = capsys.readouterr()
        assert "DRY-RUN" in captured.out

    def test_empty_list_message(self, capsys):
        """Une liste vide affiche un message explicite."""
        format_terminal([], total_before_filter=0)
        captured = capsys.readouterr()
        assert "Aucun fun fact" in captured.out
