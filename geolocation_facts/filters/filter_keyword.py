"""
filter_keyword.py
=================
Feature : Filtrage des fun facts par mot-clé.

Description :
    Ce module filtre une liste de fun facts et ne conserve que ceux dont le titre
    ou le texte du fait contient le mot-clé recherché (recherche insensible à la
    casse). Utile pour ne pousser que des faits liés à un thème précis
    (ex: "église", "musée", "guerre").

Cas d'usage :
    - L'utilisateur veut uniquement les faits mentionnant "musée" : --keyword musée
    - Sans mot-clé → aucun filtre appliqué (retourne tout)
    - Mot-clé vide ou None → retourne la liste inchangée

Entrée  : List[dict] (faits), str (mot-clé)
Sortie  : List[dict] — sous-liste des faits contenant le mot-clé
"""


def filter_by_keyword(facts: list[dict], keyword: str | None) -> list[dict]:
    """
    Filtre les fun facts selon la présence d'un mot-clé dans le titre ou le texte.

    Args:
        facts (list[dict]): Liste de dictionnaires représentant les fun facts.
        keyword (str | None): Mot-clé à rechercher (insensible à la casse).
                              Si None ou vide, aucun filtre appliqué.

    Returns:
        list[dict]: Sous-liste des faits contenant le mot-clé.
    """
    if not keyword:
        return facts

    needle = keyword.strip().lower()
    if not needle:
        return facts

    return [
        f for f in facts
        if needle in (f.get("title") or "").lower()
        or needle in (f.get("fact") or "").lower()
    ]
