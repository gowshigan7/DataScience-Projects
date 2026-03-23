"""
filter_cuisine.py
=================
Feature : Filtrage des restaurants par type de cuisine.

Description :
    Ce module filtre une liste de restaurants et ne conserve que ceux
    correspondant aux types de cuisine demandés par l'utilisateur.

    La comparaison est insensible à la casse. Un restaurant est conservé s'il
    correspond à AU MOINS UN des types de cuisine spécifiés.

    Les restaurants sans information de cuisine (cuisine = None) sont exclus
    lorsqu'un filtre est actif.

Cas d'usage :
    - L'utilisateur veut uniquement des restaurants italiens ou japonais
    - L'utilisateur ne spécifie pas de cuisine → aucun filtre appliqué (retourne tout)
    - Filtrage multi-cuisine : --cuisine italian japanese

Entrée  : List[dict] (restaurants), List[str] (cuisines à inclure)
Sortie  : List[dict] — sous-liste des restaurants dont la cuisine est dans la liste
"""


def filter_by_cuisine(restaurants: list[dict], cuisines: list[str] | None) -> list[dict]:
    """
    Filtre les restaurants selon les types de cuisine acceptés.

    Args:
        restaurants (list[dict]): Liste de dictionnaires représentant les restaurants.
        cuisines (list[str] | None): Liste des types de cuisine acceptés (ex: ["italian", "japanese"]).
                                     Si None ou liste vide, aucun filtre appliqué.

    Returns:
        list[dict]: Sous-liste des restaurants dont la cuisine figure dans la liste.
    """
    if not cuisines:
        return restaurants

    cuisines_lower = [c.lower().strip() for c in cuisines]

    return [
        r for r in restaurants
        if r.get("cuisine") is not None
        and r["cuisine"].lower().strip() in cuisines_lower
    ]
