"""
grouping.py
===========
Feature : Regroupement des articles par catégorie et formatage commun.

Description :
    Fonctions partagées par tous les formateurs : regroupement dans l'ordre
    de config.CATEGORY_KEYWORDS (puis DEFAULT_CATEGORY), format de date.

Cas d'usage :
    - formatter_terminal / formatter_markdown / formatter_html

Entrée  : list[dict] (articles traités)
Sortie  : list[tuple[str, list[dict]]] (catégorie, articles)
"""

from veille.config import CATEGORY_KEYWORDS, DATE_DISPLAY_FORMAT, DEFAULT_CATEGORY


def group_by_category(articles: list) -> list:
    """
    Regroupe les articles par catégorie, dans l'ordre de configuration.

    Args:
        articles (list[dict]): Articles avec la clé "category".

    Returns:
        list[tuple[str, list[dict]]]: Catégories non vides avec leurs articles.
    """
    order = list(CATEGORY_KEYWORDS) + [DEFAULT_CATEGORY]
    groups = {c: [] for c in order}
    for a in articles:
        groups.setdefault(a.get("category", DEFAULT_CATEGORY), []).append(a)
    return [(c, items) for c, items in groups.items() if items]


def format_date(article: dict) -> str:
    """
    Formate la date de publication d'un article.

    Args:
        article (dict): Article.

    Returns:
        str: Date au format DATE_DISPLAY_FORMAT, ou "date inconnue".
    """
    dt = article.get("published")
    return dt.strftime(DATE_DISPLAY_FORMAT) if dt else "date inconnue"
