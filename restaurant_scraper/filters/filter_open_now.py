"""
filter_open_now.py
==================
Feature : Filtrage des restaurants ouverts en ce moment.

Description :
    Ce module filtre une liste de restaurants et ne conserve que ceux
    qui sont actuellement ouverts (is_open_now = True).

    Note importante : le champ `is_open_now` dépend de la source de données.
    - Google Places : information disponible et fiable si l'API la retourne
    - OpenStreetMap (Overpass) : information non disponible (None)

    Les restaurants dont le statut d'ouverture est inconnu (None) sont exclus
    lorsque le filtre est actif, par sécurité.

Cas d'usage :
    - L'utilisateur veut uniquement des restaurants ouverts maintenant : --open-now
    - Sans ce flag → aucun filtre appliqué, tous les restaurants sont retournés
    - Restaurant avec statut inconnu → exclu si filtre actif

Entrée  : List[dict] (restaurants), bool (activer le filtre)
Sortie  : List[dict] — sous-liste des restaurants dont is_open_now = True
"""


def filter_by_open_now(restaurants: list[dict], open_now: bool) -> list[dict]:
    """
    Filtre les restaurants pour ne garder que ceux ouverts actuellement.

    Args:
        restaurants (list[dict]): Liste de dictionnaires représentant les restaurants.
        open_now (bool): Si True, ne conserve que les restaurants ouverts. Si False, aucun filtre.

    Returns:
        list[dict]: Sous-liste des restaurants avec is_open_now = True (si filtre actif).
    """
    if not open_now:
        return restaurants

    return [r for r in restaurants if r.get("is_open_now") is True]
