"""
filter_rating.py
================
Feature : Filtrage des restaurants par note minimale.

Description :
    Ce module filtre une liste de restaurants et ne conserve que ceux
    dont la note moyenne est supérieure ou égale au seuil défini par l'utilisateur.

    Les restaurants dont la note est None (inconnue) sont exclus lorsqu'un filtre
    est actif, car on ne peut pas garantir qu'ils respectent le seuil minimum.

Cas d'usage :
    - L'utilisateur veut uniquement des restaurants notés 4+ étoiles
    - L'utilisateur ne spécifie pas de note → aucun filtre appliqué (retourne tout)
    - Restaurant sans note → exclu si filtre actif, inclus sinon

Entrée  : List[dict] (restaurants), float (min_rating)
Sortie  : List[dict] — sous-liste des restaurants dont la note >= min_rating
"""


def filter_by_rating(restaurants: list[dict], min_rating: float | None) -> list[dict]:
    """
    Filtre les restaurants selon une note minimale.

    Args:
        restaurants (list[dict]): Liste de dictionnaires représentant les restaurants.
        min_rating (float | None): Note minimale (ex: 4.0). Si None ou 0, aucun filtre appliqué.

    Returns:
        list[dict]: Sous-liste des restaurants dont la note >= min_rating.
    """
    if min_rating is None or min_rating <= 0:
        return restaurants

    return [
        r for r in restaurants
        if r.get("rating") is not None and r["rating"] >= min_rating
    ]
