"""
categorize.py
=============
Feature : Classement des articles par catégorie (finance, partenariat, RH...).

Description :
    Recherche les mots-clés de config.CATEGORY_KEYWORDS dans le titre puis le
    résumé ; la première catégorie trouvée (ordre du dict) l'emporte.

Cas d'usage :
    - Regrouper le rapport par type d'information

Entrée  : Article (dict)
Sortie  : str (catégorie) / list[dict] avec la clé "category"
"""

import re

from veille.config import CATEGORY_KEYWORDS, DEFAULT_CATEGORY


def _contains_word(text: str, keyword: str) -> bool:
    """
    Teste si le mot-clé apparaît au début d'un mot (évite « cto » dans « director »).

    Args:
        text (str): Texte en minuscules.
        keyword (str): Mot-clé en minuscules.

    Returns:
        bool: True si le mot-clé apparaît au début d'un mot.
    """
    return re.search(rf"(?<!\w){re.escape(keyword)}", text) is not None


def categorize_article(article: dict) -> str:
    """
    Détermine la catégorie d'un article.

    Args:
        article (dict): Article standardisé.

    Returns:
        str: Nom de catégorie (DEFAULT_CATEGORY si aucun mot-clé).
    """
    for field in ("title", "summary"):
        text = article.get(field, "").lower()
        for category, keywords in CATEGORY_KEYWORDS.items():
            if any(_contains_word(text, k) for k in keywords):
                return category
    return DEFAULT_CATEGORY


def categorize(articles: list) -> list:
    """
    Ajoute la clé "category" à chaque article.

    Args:
        articles (list[dict]): Articles.

    Returns:
        list[dict]: Copies des articles avec "category".
    """
    return [{**a, "category": categorize_article(a)} for a in articles]
