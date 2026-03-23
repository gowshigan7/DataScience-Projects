"""
filter_distance.py
==================
Feature : Filtrage des restaurants par distance maximale.

Description :
    Ce module filtre une liste de restaurants et ne conserve que ceux
    situés à une distance inférieure ou égale au rayon spécifié par l'utilisateur.

    Ce filtre est notamment utile pour affiner les résultats lorsque la source de
    données (ex: Google Places) peut retourner des résultats légèrement hors du rayon
    demandé, ou pour combiner plusieurs sources avec des rayons différents.

    La distance utilisée est le champ `distance_m` du restaurant, calculé lors
    du scraping via la formule haversine.

Cas d'usage :
    - L'utilisateur veut uniquement des restaurants dans 500m : --radius 0.5
    - Sans rayon précis → aucun filtre de distance appliqué (retourne tout)
    - Distance inconnue (None) → exclu si filtre actif

Entrée  : List[dict] (restaurants), float (rayon_max en km)
Sortie  : List[dict] — sous-liste des restaurants dans le rayon donné
"""

from restaurant_scraper.config import METERS_PER_KM


def filter_by_distance(restaurants: list[dict], max_radius_km: float | None) -> list[dict]:
    """
    Filtre les restaurants selon une distance maximale depuis le point de recherche.

    Args:
        restaurants (list[dict]): Liste de dictionnaires représentant les restaurants.
        max_radius_km (float | None): Rayon maximum en kilomètres (ex: 1.5).
                                       Si None ou 0, aucun filtre appliqué.

    Returns:
        list[dict]: Sous-liste des restaurants dans le rayon spécifié.
    """
    if max_radius_km is None or max_radius_km <= 0:
        return restaurants

    max_radius_m = max_radius_km * METERS_PER_KM

    return [
        r for r in restaurants
        if r.get("distance_m") is not None and r["distance_m"] <= max_radius_m
    ]
