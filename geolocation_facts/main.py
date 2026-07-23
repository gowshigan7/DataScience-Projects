"""
main.py
=======
Point d'entrée principal de l'application geolocation_facts.

Description :
    Ce module orchestre l'ensemble du pipeline :
    1. Parsing des arguments CLI (argparse)
    2. Résolution de la localisation en coordonnées GPS
    3. En mode dry-run, chargement des faits mockés depuis tests/mock_data.py
    4. Sinon, récupération des faits via la source Wikipedia geosearch
    5. Application des filtres via le moteur de filtrage
    6. Formatage et affichage/export des résultats

Cas d'usage :
    # Pousser 5 fun facts autour d'une adresse
    python -m geolocation_facts.main --location "Paris, France" --radius 2.0

    # Coordonnees GPS directes, en anglais, avec un mot-cle
    python -m geolocation_facts.main --location "48.8584,2.2945" \\
        --lang en --keyword tower --limit 3

    # Mode test sans reseau
    python -m geolocation_facts.main --location "Paris" --dry-run

Entrée  : Arguments CLI
Sortie  : Cartes terminal ou fichier JSON selon --output
"""

import argparse
import sys

from geolocation_facts.config import (
    DEFAULT_RADIUS_METERS,
    DEFAULT_MAX_RESULTS,
    DEFAULT_LANGUAGE,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_JSON_OUTPUT_PATH,
    SUPPORTED_LANGUAGES,
    OUTPUT_FORMATS,
    METERS_PER_KM,
)
from geolocation_facts.geo.geolocation import resolve_location
from geolocation_facts.source.wikipedia_geo import WikipediaGeoSource
from geolocation_facts.filters.filter_engine import apply_filters
from geolocation_facts.output.formatter_terminal import format_terminal
from geolocation_facts.output.formatter_json import save_json


def build_parser() -> argparse.ArgumentParser:
    """
    Construit et retourne le parser d'arguments CLI.

    Returns:
        argparse.ArgumentParser: Parser configuré avec tous les arguments disponibles.
    """
    parser = argparse.ArgumentParser(
        prog="geolocation_facts",
        description="Pousse des fun facts sur les lieux proches d'une localisation (Wikipedia).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python -m geolocation_facts.main --location "Paris, France" --radius 2.0
  python -m geolocation_facts.main --location "48.8584,2.2945" --lang en --keyword tower
  python -m geolocation_facts.main --location "Lyon" --output json --limit 10
        """,
    )

    parser.add_argument(
        "--location",
        type=str,
        required=True,
        help='Localisation : adresse (ex: "Paris, France") ou coordonnées GPS (ex: "48.8584,2.2945")',
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=DEFAULT_RADIUS_METERS / METERS_PER_KM,
        help=f"Rayon de recherche en kilomètres, max 10 (défaut : {DEFAULT_RADIUS_METERS / METERS_PER_KM}km)",
    )
    parser.add_argument(
        "--lang",
        type=str,
        choices=SUPPORTED_LANGUAGES,
        default=DEFAULT_LANGUAGE,
        help=f"Langue Wikipedia : {', '.join(SUPPORTED_LANGUAGES)} (défaut : {DEFAULT_LANGUAGE})",
    )
    parser.add_argument(
        "--keyword",
        type=str,
        default=None,
        help="Ne garder que les faits contenant ce mot-clé (titre ou texte).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_MAX_RESULTS,
        help=f"Nombre maximum de fun facts (défaut : {DEFAULT_MAX_RESULTS})",
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=OUTPUT_FORMATS,
        default=DEFAULT_OUTPUT_FORMAT,
        help=f"Format de sortie : {', '.join(OUTPUT_FORMATS)} (défaut : {DEFAULT_OUTPUT_FORMAT})",
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=None,
        help="Chemin du fichier de sortie pour --output json.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Mode test : utilise les faits mockés, aucun appel API réel.",
    )

    return parser


def load_mock_data() -> list[dict]:
    """
    Charge les faits mockés depuis tests/mock_data.py pour le mode dry-run.

    Returns:
        list[dict]: Liste de fun facts mockés.
    """
    from geolocation_facts.tests.mock_data import MOCK_FACTS
    return MOCK_FACTS


def run(args: argparse.Namespace) -> int:
    """
    Exécute le pipeline complet : résolution, récupération, filtrage, affichage.

    Args:
        args (argparse.Namespace): Arguments CLI parsés.

    Returns:
        int: Code de retour (0 = succès, 1 = erreur).
    """
    # 1. Résolution de la localisation
    try:
        lat, lng = resolve_location(args.location)
    except ValueError as e:
        print(f"[ERREUR] {e}", file=sys.stderr)
        return 1

    radius_m = int(args.radius * METERS_PER_KM)

    # 2. Récupération des faits (ou chargement des données mockées)
    if args.dry_run:
        facts = load_mock_data()
    else:
        source = WikipediaGeoSource(dry_run=False)
        try:
            facts = source.fetch_facts(
                latitude=lat,
                longitude=lng,
                radius_m=radius_m,
                limit=args.limit * 3,  # Récupère plus pour laisser de la matière aux filtres
                language=args.lang,
            )
        except (ValueError, RuntimeError) as e:
            print(f"[ERREUR] Recuperation des faits echouee : {e}", file=sys.stderr)
            return 1

    # 3. Application des filtres
    filtered, total_before = apply_filters(
        facts=facts,
        keyword=args.keyword,
        max_radius_km=args.radius,
        limit=args.limit,
    )

    # 4. Formatage et sortie
    if args.output == "terminal":
        format_terminal(filtered, total_before_filter=total_before, dry_run=args.dry_run)
    elif args.output == "json":
        filepath = args.output_file or DEFAULT_JSON_OUTPUT_PATH
        save_json(filtered, filepath, dry_run=args.dry_run)

    return 0


def main() -> None:
    """
    Point d'entrée principal — parse les arguments et lance le pipeline.
    """
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
