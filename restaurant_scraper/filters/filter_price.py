"""
filter_price.py
===============
Feature : Filtrage des restaurants par niveau de prix.

Description :
    Ce module filtre une liste de restaurants selon les niveaux de prix acceptés
    par l'utilisateur. Les niveaux de prix correspondent à :
        1 → €     (économique)
        2 → €€    (abordable)
        3 → €€€   (intermédiaire)
        4 → €€€€  (haut de gamme)

    Un restaurant est conservé s'il correspond à AU MOINS UN des niveaux de prix
    spécifiés. Les restaurants sans information de prix (price_level = None) sont
    exclus lorsqu'un filtre est actif.

Cas d'usage :
    - L'utilisateur veut des restaurants bon marché : --price 1 2
    - L'utilisateur ne spécifie pas de prix → aucun filtre appliqué (retourne tout)
    - Niveau de prix inconnu → exclu si filtre actif

Entrée  : List[dict] (restaurants), List[int] (niveaux de prix acceptés, 1-4)
Sortie  : List[dict] — sous-liste des restaurants dont le prix est dans la liste
"""


def filter_by_price(restaurants: list[dict], price_levels: list[int] | None) -> list[dict]:
    """
    Filtre les restaurants selon les niveaux de prix acceptés.

    Args:
        restaurants (list[dict]): Liste de dictionnaires représentant les restaurants.
        price_levels (list[int] | None): Niveaux de prix acceptés (ex: [1, 2]).
                                         Si None ou liste vide, aucun filtre appliqué.

    Returns:
        list[dict]: Sous-liste des restaurants dont le niveau de prix figure dans la liste.
    """
    if not price_levels:
        return restaurants

    valid_levels = [int(p) for p in price_levels if 1 <= int(p) <= 4]
    if not valid_levels:
        return restaurants

    return [
        r for r in restaurants
        if r.get("price_level") is not None and r["price_level"] in valid_levels
    ]
