"""
digest_pipeline.py
==================
Feature : Traitement du digest IA (flux fixes, sans sujet).

Description :
    1. Filtre par date
    2. Dédoublonnage (même lien ou même titre repris par plusieurs flux)
    3. Tri du plus récent au plus ancien (sans date en dernier)
    Pas de score de pertinence : les flux sont déjà choisis ; la catégorie
    est le groupe fixé par chaque source.

Cas d'usage :
    - main.py digest

Entrée  : list[dict] articles bruts, fenêtre en jours
Sortie  : list[dict] articles traités
"""

from datetime import datetime, timezone

from veille.config import DEFAULT_CATEGORY
from veille.processing.date_filter import filter_by_date
from veille.processing.dedup import deduplicate

_OLDEST = datetime.min.replace(tzinfo=timezone.utc)


def process_digest(articles: list, since_days: int, now: datetime = None) -> list:
    """
    Nettoie et trie les articles du digest.

    Args:
        articles (list[dict]): Articles bruts (avec "category").
        since_days (int): Fenêtre en jours.
        now (datetime | None): Date de référence (tests).

    Returns:
        list[dict]: Articles uniques, triés par date décroissante.
    """
    unique = deduplicate(filter_by_date(articles, since_days, now))
    for a in unique:
        a["category"] = a.get("category") or DEFAULT_CATEGORY
    unique.sort(key=lambda a: a["published"] or _OLDEST, reverse=True)
    return unique
