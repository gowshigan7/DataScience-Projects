"""
reddit.py
=========
Feature : Source Reddit (top du jour des subreddits IA).

Description :
    Lit https://www.reddit.com/r/<sub>/top.json?t=day et garde les posts ayant
    au moins REDDIT_MIN_SCORE votes. Si Reddit refuse le JSON (fréquent sans
    compte), repli sur le flux Atom /top/.rss (sans score).

Cas d'usage :
    - r/LocalLLaMA, r/MachineLearning, r/OpenAI, r/ClaudeAI, r/singularity

Entrée  : Nom du subreddit
Sortie  : list[dict] (articles standardisés, groupe Communauté)
"""

import json
import urllib.error
from datetime import datetime, timezone

from veille.config import (
    GROUP_COMMUNITY,
    REDDIT_BASE_URL,
    REDDIT_MAX_PER_SUB,
    REDDIT_MIN_SCORE,
    REDDIT_PERIOD_DAY,
    REDDIT_PERIOD_WEEK,
    REDDIT_TOP_JSON_URL,
    REDDIT_TOP_RSS_URL,
)
from veille.sources import base_source
from veille.sources.base_source import BaseSource, parse_date
from veille.sources.rss_parser import parse_rss


class RedditSource(BaseSource):
    """Top des posts d'un subreddit."""

    def __init__(self, subreddit: str):
        """
        Args:
            subreddit (str): Nom du subreddit (sans r/).

        Returns:
            None
        """
        self.subreddit = subreddit
        self.name = f"r/{subreddit}"

    def fetch(self, topic, since_days: int, max_results: int = REDDIT_MAX_PER_SUB) -> list:
        """
        Récupère les posts populaires du subreddit.

        Args:
            topic (dict | None): Ignoré.
            since_days (int): 1 → top du jour, sinon top de la semaine.
            max_results (int): Nombre max de posts.

        Returns:
            list[dict]: Articles standardisés.
        """
        period = REDDIT_PERIOD_DAY if since_days <= 1 else REDDIT_PERIOD_WEEK
        params = {"t": period, "limit": max_results}
        try:
            raw = base_source.http_get(REDDIT_TOP_JSON_URL.format(sub=self.subreddit), params)
            return self._from_json(json.loads(raw))
        except (urllib.error.HTTPError, json.JSONDecodeError):
            raw = base_source.http_get(REDDIT_TOP_RSS_URL.format(sub=self.subreddit), {"t": period})
            return [self.make_article(i["title"], i["link"], self.name, parse_date(i["pubDate"]),
                                      "", "en", GROUP_COMMUNITY)
                    for i in parse_rss(raw)[:max_results]]

    def _from_json(self, data: dict) -> list:
        """
        Convertit la réponse JSON de Reddit.

        Args:
            data (dict): Réponse de /top.json.

        Returns:
            list[dict]: Articles standardisés (score >= REDDIT_MIN_SCORE).
        """
        articles = []
        for child in data.get("data", {}).get("children", []):
            d = child.get("data", {})
            if d.get("score", 0) < REDDIT_MIN_SCORE:
                continue
            created = datetime.fromtimestamp(d.get("created_utc", 0), tz=timezone.utc)
            articles.append(self.make_article(
                d.get("title", ""), f"{REDDIT_BASE_URL}{d.get('permalink', '')}", self.name,
                created, f"▲ {d.get('score', 0)} · {d.get('num_comments', 0)} commentaires",
                "en", GROUP_COMMUNITY))
        return articles
