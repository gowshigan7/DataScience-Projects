"""
hacker_news.py
==============
Feature : Source Hacker News (API Algolia, gratuite, sans clé).

Description :
    Recherche les « stories » mentionnant le sujet sur Hacker News, utile pour
    les sujets tech (entreprises, outils, technologies).

Cas d'usage :
    - Repérer les discussions de la communauté tech

Entrée  : Sujet (dict), fenêtre en jours, nombre max d'articles
Sortie  : list[dict] (articles standardisés)
"""

import json
import time

from veille.config import HACKER_NEWS_ITEM_URL, HACKER_NEWS_SEARCH_URL, SECONDS_PER_DAY
from veille.sources import base_source
from veille.sources.base_source import BaseSource, parse_date


class HackerNewsSource(BaseSource):
    """Recherche de discussions via l'API Algolia de Hacker News."""

    name = "hacker_news"

    def fetch(self, topic: dict, since_days: int, max_results: int) -> list:
        """
        Récupère les stories Hacker News pour un sujet.

        Args:
            topic (dict): Sujet.
            since_days (int): Fenêtre temporelle en jours.
            max_results (int): Nombre max de stories.

        Returns:
            list[dict]: Articles standardisés (langue "en").
        """
        since_ts = int(time.time()) - since_days * SECONDS_PER_DAY
        params = {
            "query": f'"{topic["name"]}"',
            "tags": "story",
            "numericFilters": f"created_at_i>{since_ts}",
            "hitsPerPage": max_results,
        }
        data = json.loads(base_source.http_get(HACKER_NEWS_SEARCH_URL, params))
        articles = []
        for hit in data.get("hits", []):
            discussion = f"{HACKER_NEWS_ITEM_URL}{hit.get('objectID', '')}"
            articles.append(self.make_article(
                hit.get("title") or "", hit.get("url") or discussion, "Hacker News",
                parse_date(hit.get("created_at", "")),
                f"{hit.get('points', 0)} points · {hit.get('num_comments', 0)} commentaires",
                "en"))
        return articles
