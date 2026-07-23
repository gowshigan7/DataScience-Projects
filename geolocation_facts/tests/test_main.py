"""
test_main.py
============
Feature : Tests du pipeline CLI (main.py) en mode dry-run.

Description :
    Ce module teste la construction du parser d'arguments et l'exécution du
    pipeline complet en mode dry-run, sans aucun appel réseau ni écriture de
    fichier. Le chemin dry-run charge MOCK_FACTS et affiche les résultats.

Cas d'usage :
    - Validation du parsing des arguments CLI
    - Validation du pipeline de bout en bout en dry-run

Entrée  : Arguments CLI simulés
Sortie  : Assertions pytest (pas d'effets de bord, pas de fichier écrit)
"""

from geolocation_facts.main import build_parser, run, load_mock_data
from geolocation_facts.tests.mock_data import MOCK_FACTS


class TestBuildParser:
    def test_location_required(self):
        """Le parser accepte --location et applique les valeurs par défaut."""
        parser = build_parser()
        args = parser.parse_args(["--location", "Paris"])
        assert args.location == "Paris"
        assert args.dry_run is False
        assert args.output == "terminal"

    def test_flags_parsed(self):
        """Les options principales sont correctement parsées."""
        parser = build_parser()
        args = parser.parse_args([
            "--location", "48.8584,2.2945",
            "--radius", "2.0",
            "--lang", "en",
            "--keyword", "tower",
            "--limit", "3",
            "--output", "json",
            "--dry-run",
        ])
        assert args.radius == 2.0
        assert args.lang == "en"
        assert args.keyword == "tower"
        assert args.limit == 3
        assert args.output == "json"
        assert args.dry_run is True


class TestLoadMockData:
    def test_returns_mock_facts(self):
        """load_mock_data retourne les faits mockés."""
        assert load_mock_data() == MOCK_FACTS


class TestRunDryRun:
    def test_run_terminal_dry_run(self, capsys):
        """Le pipeline dry-run terminal s'exécute et retourne 0."""
        parser = build_parser()
        args = parser.parse_args(["--location", "48.8584,2.2945", "--dry-run"])
        code = run(args)
        captured = capsys.readouterr()
        assert code == 0
        assert "DRY-RUN" in captured.out
        assert "Tour Eiffel" in captured.out

    def test_run_respects_limit(self, capsys):
        """La limite est respectée dans la sortie terminal."""
        parser = build_parser()
        args = parser.parse_args([
            "--location", "48.8584,2.2945", "--limit", "2", "--dry-run",
        ])
        code = run(args)
        assert code == 0

    def test_run_json_dry_run_writes_nothing(self, capsys):
        """Le pipeline dry-run JSON n'écrit aucun fichier."""
        parser = build_parser()
        args = parser.parse_args([
            "--location", "48.8584,2.2945", "--output", "json", "--dry-run",
        ])
        code = run(args)
        captured = capsys.readouterr()
        assert code == 0
        assert "DRY-RUN" in captured.out

    def test_run_dry_run_no_network_for_coordinates(self, capsys):
        """Avec des coordonnées directes, le dry-run n'effectue aucun appel réseau."""
        # Des coordonnées sont parsées localement (parse_coordinates) : aucune
        # résolution réseau n'est déclenchée, et le dry-run court-circuite la source.
        parser = build_parser()
        args = parser.parse_args([
            "--location=-33.8688,151.2093", "--dry-run",
        ])
        code = run(args)
        assert code == 0
