"""
formatter_terminal.py
=====================
Feature : Affichage des restaurants en tableau formaté dans le terminal.

Description :
    Ce module formate et affiche une liste de restaurants sous forme de tableau
    ASCII dans le terminal, avec des colonnes alignées et des indicateurs visuels
    (étoiles pour la note, symboles pour l'ouverture).

    L'affichage inclut un en-tête récapitulatif (nombre de résultats, filtres appliqués)
    et un tableau avec les colonnes : Nom, Cuisine, Note, Prix, Distance, Ouvert.

Cas d'usage :
    - Affichage interactif pour l'utilisateur en ligne de commande
    - Mode dry-run : même affichage, avec le bandeau [DRY-RUN] en en-tête
    - Liste vide → message explicite "Aucun restaurant trouvé"

Entrée  : List[dict] (restaurants), int (total avant filtrage), bool (dry_run)
Sortie  : None (affichage direct dans stdout)
"""

from restaurant_scraper.config import PRICE_LEVELS, TERMINAL_TABLE_MAX_NAME_WIDTH


def _truncate(text: str, max_len: int) -> str:
    """
    Tronque une chaîne à la longueur maximale donnée, avec ellipse.

    Args:
        text (str): Chaîne à tronquer.
        max_len (int): Longueur maximale.

    Returns:
        str: Chaîne tronquée avec "..." si nécessaire.
    """
    if not text:
        return ""
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _format_rating(rating: float | None) -> str:
    """
    Formate la note d'un restaurant avec un symbole étoile.

    Args:
        rating (float | None): Note du restaurant (0.0 - 5.0).

    Returns:
        str: Note formatée (ex: "* 4.5") ou "N/A" si inconnue.
    """
    if rating is None:
        return "N/A"
    return f"* {rating:.1f}"


def _format_price(price_level: int | None) -> str:
    """
    Formate le niveau de prix en symboles euros.

    Args:
        price_level (int | None): Niveau de prix (1-4).

    Returns:
        str: Symbole prix (ex: "€€") ou "N/A" si inconnu.
    """
    if price_level is None:
        return "N/A"
    return PRICE_LEVELS.get(price_level, "N/A")


def _format_distance(distance_m: float | None) -> str:
    """
    Formate la distance en mètres ou kilomètres selon la valeur.

    Args:
        distance_m (float | None): Distance en mètres.

    Returns:
        str: Distance formatée (ex: "320m" ou "1.2km") ou "N/A".
    """
    if distance_m is None:
        return "N/A"
    if distance_m < 1000:
        return f"{int(distance_m)}m"
    return f"{distance_m / 1000:.1f}km"


def _format_open(is_open: bool | None) -> str:
    """
    Formate le statut d'ouverture d'un restaurant.

    Args:
        is_open (bool | None): True si ouvert, False si fermé, None si inconnu.

    Returns:
        str: Statut lisible ("Oui", "Non", ou "?").
    """
    if is_open is True:
        return "Oui"
    if is_open is False:
        return "Non"
    return "?"


def format_terminal(
    restaurants: list[dict],
    total_before_filter: int = 0,
    dry_run: bool = False,
) -> None:
    """
    Affiche les restaurants dans un tableau formaté dans le terminal.

    Args:
        restaurants (list[dict]): Liste de restaurants à afficher.
        total_before_filter (int): Nombre de restaurants avant filtrage (pour le récapitulatif).
        dry_run (bool): Si True, affiche le bandeau [DRY-RUN] en en-tête.

    Returns:
        None
    """
    count = len(restaurants)
    print(f"\nRestaurants trouves : {count} / {total_before_filter} (filtres appliques)\n")

    if not restaurants:
        print("Aucun restaurant ne correspond aux criteres de filtrage.")
        return

    # Largeurs des colonnes
    col_name = min(
        max((len(r.get("name", "") or "") for r in restaurants), default=10),
        TERMINAL_TABLE_MAX_NAME_WIDTH,
    )
    col_name = max(col_name, 4)
    col_cuisine = 12
    col_rating = 8
    col_price = 6
    col_distance = 10
    col_open = 8

    def row_sep(char="-", cross="+"):
        return (
            cross
            + (char * (col_name + 2))
            + cross
            + (char * (col_cuisine + 2))
            + cross
            + (char * (col_rating + 2))
            + cross
            + (char * (col_price + 2))
            + cross
            + (char * (col_distance + 2))
            + cross
            + (char * (col_open + 2))
            + cross
        )

    def row_data(name, cuisine, rating, price, distance, open_status):
        return (
            f"| {name:<{col_name}} "
            f"| {cuisine:<{col_cuisine}} "
            f"| {rating:<{col_rating}} "
            f"| {price:<{col_price}} "
            f"| {distance:<{col_distance}} "
            f"| {open_status:<{col_open}} |"
        )

    print(row_sep("="))
    print(row_data("Nom", "Cuisine", "Note", "Prix", "Distance", "Ouvert"))
    print(row_sep("="))

    for r in restaurants:
        name = _truncate(r.get("name") or "", col_name)
        cuisine = _truncate((r.get("cuisine") or "N/A").capitalize(), col_cuisine)
        rating = _format_rating(r.get("rating"))
        price = _format_price(r.get("price_level"))
        distance = _format_distance(r.get("distance_m"))
        open_status = _format_open(r.get("is_open_now"))

        print(row_data(name, cuisine, rating, price, distance, open_status))
        print(row_sep())

    print()
