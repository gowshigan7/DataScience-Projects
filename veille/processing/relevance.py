"""
relevance.py
============
Feature : Score de pertinence d'un article pour un sujet + exclusion des homonymes.

Description :
    Score = points si le nom exact apparaît dans le titre / le résumé,
    + points par alias trouvé. Un article contenant un terme d'exclusion
    (ex. « Shift Technologies » pour éviter le site de voitures d'occasion)
    obtient un score de 0.

Cas d'usage :
    - Éliminer le bruit des moteurs de recherche
    - Trier les articles par pertinence

Entrée  : Article (dict), sujet (dict)
Sortie  : int (score) / list[dict] filtrée
"""

from veille.config import (
    MIN_RELEVANCE_SCORE,
    SCORE_ALIAS_MATCH,
    SCORE_EXACT_IN_SUMMARY,
    SCORE_EXACT_IN_TITLE,
)


def score_article(article: dict, topic: dict) -> int:
    """
    Calcule le score de pertinence d'un article.

    Args:
        article (dict): Article standardisé.
        topic (dict): Sujet.

    Returns:
        int: Score (0 = non pertinent ou exclu).
    """
    title = article.get("title", "").lower()
    summary = article.get("summary", "").lower()
    text = f"{title} {summary}"
    if any(ex.lower() in text for ex in topic.get("exclude", [])):
        return 0
    name = topic["name"].lower()
    score = 0
    if name in title:
        score += SCORE_EXACT_IN_TITLE
    if name in summary:
        score += SCORE_EXACT_IN_SUMMARY
    score += SCORE_ALIAS_MATCH * sum(a.lower() in text for a in topic.get("aliases", []))
    return score


def filter_relevant(articles: list, topic: dict, min_score: int = MIN_RELEVANCE_SCORE) -> list:
    """
    Ajoute la clé "score" et garde les articles assez pertinents.

    Args:
        articles (list[dict]): Articles.
        topic (dict): Sujet.
        min_score (int): Score minimal ; si falsy, aucun filtrage (score ajouté quand même).

    Returns:
        list[dict]: Articles retenus (copies avec la clé "score").
    """
    scored = [{**a, "score": score_article(a, topic)} for a in articles]
    if not min_score:
        return scored
    return [a for a in scored if a["score"] >= min_score]
