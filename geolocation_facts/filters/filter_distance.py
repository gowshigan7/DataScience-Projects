"""
filter_distance.py
==================
Feature : Filtrage des fun facts par distance maximale.

Description :
    Ce module filtre une liste de fun facts et ne conserve que ceux situés à une
    distance inférieure ou égale au rayon spécifié par l'utilisateur.

    Ce filtre affine les résultats lorsque la source renvoie des lieux légèrement
    hors du rayon demandé. La distance utilisée est le champ `distance_m` du fait,
    calculé lors de la récupération via la formule haversine.

Cas d'usage :
    - L'utilisateur veut uniquement les faits dans 2 km : --radius 2.0
    - Sans rayon précis → aucun filtre de distance appliqué (retourne tout)
    - Distance inconnue (None) → exclu si filtre actif

Entrée  : List[dict] (faits), float (rayon_max en km)
Sortie  : List[dict] — sous-liste des faits dans le rayon donné
"""

from geolocation_facts.config import METERS_PER_KM


def filter_by_distance(facts: list[dict], max_radius_km: float | None) -> list[dict]:
    """
    Filtre les fun facts selon une distance maximale depuis le point de recherche.

    Args:
        facts (list[dict]): Liste de dictionnaires représentant les fun facts.
        max_radius_km (float | None): Rayon maximum en kilomètres (ex: 2.0).
                                       Si None ou 0, aucun filtre appliqué.

    Returns:
        list[dict]: Sous-liste des faits dans le rayon spécifié.
    """
    if max_radius_km is None or max_radius_km <= 0:
        return facts

    max_radius_m = max_radius_km * METERS_PER_KM

    return [
        f for f in facts
        if f.get("distance_m") is not None and f["distance_m"] <= max_radius_m
    ]
