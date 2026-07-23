"""
formatter_terminal.py
=====================
Feature : Affichage des fun facts sous forme de cartes dans le terminal.

Description :
    Ce module formate et affiche une liste de fun facts dans le terminal, sous
    forme de « cartes » lisibles : titre, distance, texte du fait et lien source.

    L'affichage inclut un en-tête récapitulatif (nombre de faits, total avant
    filtrage) et, en mode dry-run, un bandeau [DRY-RUN].

Cas d'usage :
    - Affichage interactif pour l'utilisateur en ligne de commande
    - Mode dry-run : même affichage, avec le bandeau [DRY-RUN] en en-tête
    - Liste vide → message explicite "Aucun fun fact trouvé"

Entrée  : List[dict] (faits), int (total avant filtrage), bool (dry_run)
Sortie  : None (affichage direct dans stdout)
"""

from geolocation_facts.config import TERMINAL_DIVIDER_WIDTH


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


def format_terminal(
    facts: list[dict],
    total_before_filter: int = 0,
    dry_run: bool = False,
) -> None:
    """
    Affiche les fun facts sous forme de cartes dans le terminal.

    Args:
        facts (list[dict]): Liste de fun facts à afficher.
        total_before_filter (int): Nombre de faits avant filtrage (pour le récapitulatif).
        dry_run (bool): Si True, affiche le bandeau [DRY-RUN] en en-tête.

    Returns:
        None
    """
    divider = "=" * TERMINAL_DIVIDER_WIDTH
    thin = "-" * TERMINAL_DIVIDER_WIDTH

    if dry_run:
        print("\n[DRY-RUN] Fun facts issus des donnees mockees\n")

    count = len(facts)
    print(divider)
    print(f"  Fun facts a proximite : {count} / {total_before_filter} (filtres appliques)")
    print(divider)

    if not facts:
        print("\nAucun fun fact ne correspond aux criteres.\n")
        return

    for index, fact in enumerate(facts, start=1):
        title = fact.get("title") or "(sans titre)"
        distance = _format_distance(fact.get("distance_m"))
        text = fact.get("fact") or ""
        url = fact.get("url")

        print()
        print(f"  {index}. {title}  ({distance})")
        print(thin)
        print(f"  {text}")
        if url:
            print(f"  -> {url}")

    print()
