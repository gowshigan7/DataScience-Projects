"""
main.py
=======
Point d'entrée principal de l'application restaurant_scraper.

Description :
    Ce module orchestre l'ensemble du pipeline de scraping :
    1. Parsing des arguments CLI (argparse)
    2. Résolution de la localisation en coordonnées GPS
    3. Sélection du scraper approprié (Google Places ou Overpass OSM)
    4. En mode dry-run, chargement des données mockées depuis tests/mock_data.py
    5. Application des filtres via le moteur de filtrage
    6. Formatage et affichage/export des résultats

Cas d'usage :
    # Recherche de restaurants italiens ou japonais, notés 4+, dans 1km
    python main.py --location "48.8566,2.3522" --radius 1.0 \\
        --cuisine italian japanese --min-rating 4.0 --open-now --output terminal

    # Mode test sans API
    python main.py --location "Paris" --radius 1.0 --dry-run

    # Export CSV avec limite
    python main.py --location "Lyon, France" --radius 2.0 --output csv --limit 20

Entrée  : Arguments CLI
Sortie  : Tableau terminal, fichier JSON ou CSV selon --output
"""

import argparse
import sys

from restaurant_scraper.config import (
    DEFAULT_RADIUS_METERS,
    DEFAULT_MIN_RATING,
    DEFAULT_MAX_RESULTS,
    DEFAULT_OUTPUT_FORMAT,
    GOOGLE_PLACES_API_KEY,
    DEFAULT_JSON_OUTPUT_PATH,
    DEFAULT_CSV_OUTPUT_PATH,
    SUPPORTED_CUISINES,
    OUTPUT_FORMATS,
    METERS_PER_KM,
)
from restaurant_scraper.geo.geolocation import resolve_location
from restaurant_scraper.scraper.google_places import GooglePlacesScraper
from restaurant_scraper.scraper.overpass_osm import OverpassOSMScraper
from restaurant_scraper.filters.filter_engine import apply_filters
from restaurant_scraper.output.formatter_terminal import format_terminal
from restaurant_scraper.output.formatter_json import save_json
from restaurant_scraper.output.formatter_csv import save_csv


def build_parser() -> argparse.ArgumentParser:
    """
    Construit et retourne le parser d'arguments CLI.

    Returns:
        argparse.ArgumentParser: Parser configuré avec tous les arguments disponibles.
    """
    parser = argparse.ArgumentParser(
        prog="restaurant_scraper",
        description="Outil de scraping de restaurants à proximité d'une localisation.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python main.py --location "Paris, France" --radius 1.0 --dry-run
  python main.py --location "48.8566,2.3522" --cuisine italian japanese --min-rating 4.0
  python main.py --location "Lyon" --output csv --limit 20 --price 1 2
        """,
    )

    parser.add_argument(
        "--location",
        type=str,
        required=True,
        help='Localisation : adresse (ex: "Paris, France") ou coordonnées GPS (ex: "48.8566,2.3522")',
    )
    parser.add_argument(
        "--radius",
        type=float,
        default=DEFAULT_RADIUS_METERS / METERS_PER_KM,
        help=f"Rayon de recherche en kilomètres (défaut : {DEFAULT_RADIUS_METERS / METERS_PER_KM}km)",
    )
    parser.add_argument(
        "--min-rating",
        type=float,
        default=None,
        help="Note minimale acceptable (ex: 4.0). Sans valeur = aucun filtre.",
    )
    parser.add_argument(
        "--cuisine",
        type=str,
        nargs="+",
        default=None,
        help=f"Type(s) de cuisine acceptés (ex: italian japanese). Disponibles : {', '.join(SUPPORTED_CUISINES)}",
    )
    parser.add_argument(
        "--price",
        type=int,
        nargs="+",
        choices=[1, 2, 3, 4],
        default=None,
        help="Niveau(x) de prix acceptés : 1=€ 2=€€ 3=€€€ 4=€€€€ (ex: --price 1 2)",
    )
    parser.add_argument(
        "--open-now",
        action="store_true",
        default=False,
        help="Ne retourner que les restaurants ouverts en ce moment.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_MAX_RESULTS,
        help=f"Nombre maximum de résultats (défaut : {DEFAULT_MAX_RESULTS})",
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
        help="Chemin du fichier de sortie pour --output json ou csv.",
    )
    parser.add_argument(
        "--source",
        type=str,
        choices=["google", "osm", "auto"],
        default="auto",
        help='Source de données : "google" (Google Places), "osm" (OpenStreetMap), "auto" (défaut)',
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Mode test : utilise les données mockées, aucun appel API réel.",
    )

    return parser


def select_scraper(source: str, dry_run: bool):
    """
    Sélectionne le scraper approprié selon la source demandée et la disponibilité de l'API key.

    Args:
        source (str): Source demandée ("google", "osm", ou "auto").
        dry_run (bool): Si True, instancie le scraper en mode dry-run.

    Returns:
        BaseScraper: Instance du scraper sélectionné.
    """
    if source == "google" or (source == "auto" and GOOGLE_PLACES_API_KEY):
        return GooglePlacesScraper(dry_run=dry_run)
    return OverpassOSMScraper(dry_run=dry_run)


def load_mock_data() -> list[dict]:
    """
    Charge les données mockées depuis tests/mock_data.py pour le mode dry-run.

    Returns:
        list[dict]: Liste de restaurants mockés.
    """
    from restaurant_scraper.tests.mock_data import MOCK_RESTAURANTS
    return MOCK_RESTAURANTS


def run(args: argparse.Namespace) -> int:
    """
    Exécute le pipeline complet de scraping, filtrage et affichage.

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

    # 2. Scraping (ou chargement des données mockées)
    if args.dry_run:
        print("[DRY-RUN] Utilisation des donnees mockees")
        restaurants = load_mock_data()
    else:
        scraper = select_scraper(args.source, dry_run=False)
        try:
            restaurants = scraper.fetch_restaurants(
                latitude=lat,
                longitude=lng,
                radius_m=radius_m,
                limit=args.limit * 3,  # Récupère plus pour que les filtres aient de la matière
            )
        except (ValueError, RuntimeError) as e:
            print(f"[ERREUR] Scraping echoue : {e}", file=sys.stderr)
            return 1

    # 3. Application des filtres
    filtered, total_before = apply_filters(
        restaurants=restaurants,
        min_rating=args.min_rating,
        cuisines=args.cuisine,
        price_levels=args.price,
        open_now=args.open_now,
        max_radius_km=args.radius,
        limit=args.limit,
    )

    # 4. Formatage et sortie
    if args.output == "terminal":
        format_terminal(filtered, total_before_filter=total_before, dry_run=args.dry_run)

    elif args.output == "json":
        filepath = args.output_file or DEFAULT_JSON_OUTPUT_PATH
        save_json(filtered, filepath, dry_run=args.dry_run)

    elif args.output == "csv":
        filepath = args.output_file or DEFAULT_CSV_OUTPUT_PATH
        save_csv(filtered, filepath, dry_run=args.dry_run)

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
