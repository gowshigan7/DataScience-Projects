"""
hn_top.py
=========
Feature : Source Hacker News « stories IA populaires » (pour le digest).

Description :
    Interroge l'API Algolia pour les stories récentes ayant au moins
    HACKER_NEWS_MIN_POINTS points, puis garde celles qui parlent d'IA
    (config.AI_KEYWORDS). Lien = article ; le résumé donne points et commentaires.

Cas d'usage :
    - Ce que la communauté tech discute sur l'IA

Entrée  : Fenêtre en jours
Sortie  : list[dict] (articles standardisés, groupe Communauté)
"""

import json
import time

from veille.config import (
    AI_KEYWORDS,
    GROUP_COMMUNITY,
    HACKER_NEWS_DIGEST_HITS,
    HACKER_NEWS_DIGEST_URL,
    HACKER_NEWS_ITEM_URL,
    HACKER_NEWS_MIN_POINTS,
    SECONDS_PER_DAY,
)
from veille.sources import base_source
from veille.sources.base_source import BaseSource, matches_keywords, parse_date


class HackerNewsTopSource(BaseSource):
    """Stories Hacker News populaires liées à l'IA."""

    name = "hacker_news_top"

    def fetch(self, topic, since_days: int, max_results: int) -> list:
        """
        Récupère les stories IA populaires.

        Args:
            topic (dict | None): Ignoré.
            since_days (int): Fenêtre en jours.
            max_results (int): Nombre max de stories.

        Returns:
            list[dict]: Articles standardisés, triés par points.
        """
        since_ts = int(time.time()) - since_days * SECONDS_PER_DAY
        params = {"tags": "story", "hitsPerPage": HACKER_NEWS_DIGEST_HITS,
                  "numericFilters": f"created_at_i>{since_ts},points>={HACKER_NEWS_MIN_POINTS}"}
        hits = json.loads(base_source.http_get(HACKER_NEWS_DIGEST_URL, params)).get("hits", [])
        hits = [h for h in hits if matches_keywords(h.get("title") or "", AI_KEYWORDS)]
        hits.sort(key=lambda h: h.get("points", 0), reverse=True)
        return [self.make_article(
            h.get("title") or "", h.get("url") or f"{HACKER_NEWS_ITEM_URL}{h.get('objectID')}",
            "Hacker News", parse_date(h.get("created_at", "")),
            f"▲ {h.get('points', 0)} · {h.get('num_comments', 0)} commentaires · "
            f"{HACKER_NEWS_ITEM_URL}{h.get('objectID')}", "en", GROUP_COMMUNITY)
            for h in hits[:max_results]]
