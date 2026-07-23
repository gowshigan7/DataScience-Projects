"""
filter_engine.py
================
Feature : Moteur de filtrage principal — orchestration de tous les filtres.

Description :
    Ce module fournit le moteur central de filtrage qui applique séquentiellement
    tous les filtres disponibles sur une liste de fun facts.

    Chaque filtre est indépendant et optionnel. Si un critère de filtre n'est pas
    spécifié (None ou valeur par défaut), le filtre correspondant est ignoré.

    L'ordre d'application est optimisé pour réduire la liste le plus tôt possible :
    1. Distance (filtre le plus structurel)
    2. Mot-clé

    Les faits sont ensuite triés par distance croissante et la limite finale est
    appliquée.

Cas d'usage :
    - Applique tous les filtres configurés en une seule passe
    - Retourne les résultats filtrés et un rapport de réduction
    - Utilisé par main.py après la récupération des faits

Entrée  : List[dict] (faits), dict (paramètres de filtrage)
Sortie  : List[dict] — liste filtrée, int — nombre de résultats avant filtrage
"""

from geolocation_facts.filters.filter_distance import filter_by_distance
from geolocation_facts.filters.filter_keyword import filter_by_keyword


def apply_filters(
    facts: list[dict],
    keyword: str | None = None,
    max_radius_km: float | None = None,
    limit: int | None = None,
) -> tuple[list[dict], int]:
    """
    Applique séquentiellement tous les filtres configurés sur une liste de fun facts.

    Args:
        facts (list[dict]): Liste brute de faits récupérés par la source.
        keyword (str | None): Mot-clé à rechercher dans le titre/texte. None = pas de filtre.
        max_radius_km (float | None): Rayon maximum en km. None ou 0 = pas de filtre.
        limit (int | None): Nombre maximum de résultats finaux. None = pas de limite.

    Returns:
        tuple[list[dict], int]: (liste filtrée, nombre de résultats avant filtrage)
    """
    total_before = len(facts)

    result = filter_by_distance(facts, max_radius_km)
    result = filter_by_keyword(result, keyword)

    # Tri par distance croissante (faits les plus proches en premier)
    result = sorted(result, key=lambda f: f.get("distance_m") or float("inf"))

    if limit is not None and limit > 0:
        result = result[:limit]

    return result, total_before
