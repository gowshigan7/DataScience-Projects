"""
date_filter.py
==============
Feature : Filtre des articles par fenêtre temporelle.

Description :
    Garde les articles publiés depuis moins de N jours. Les articles sans date
    sont conservés (on ne peut pas prouver qu'ils sont anciens).

Cas d'usage :
    - Bing News ne filtre pas par date côté serveur

Entrée  : list[dict] (articles), int (jours), datetime (maintenant)
Sortie  : list[dict] (articles récents)
"""

from datetime import datetime, timedelta, timezone


def filter_by_date(articles: list, since_days: int, now: datetime = None) -> list:
    """
    Garde les articles récents.

    Args:
        articles (list[dict]): Articles.
        since_days (int): Fenêtre en jours ; si falsy, aucun filtrage.
        now (datetime | None): Date de référence (UTC) ; maintenant si None.

    Returns:
        list[dict]: Articles publiés dans la fenêtre (ou sans date).
    """
    if not since_days:
        return articles
    limit = (now or datetime.now(timezone.utc)) - timedelta(days=since_days)
    return [a for a in articles if a.get("published") is None or a["published"] >= limit]
