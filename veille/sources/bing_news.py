"""
bing_news.py
============
Feature : Source Bing News (flux RSS, gratuit, sans clé).

Description :
    Interroge https://www.bing.com/news/search?format=rss pour chaque langue.
    Complète Google News avec d'autres médias et un résumé (description).
    Le filtrage par date est fait ensuite par le pipeline.

Cas d'usage :
    - Seconde source de presse, avec extrait d'article

Entrée  : Sujet (dict), fenêtre en jours, nombre max d'articles
Sortie  : list[dict] (articles standardisés)
"""

from veille.config import BING_NEWS_MARKETS, BING_NEWS_RSS_URL
from veille.sources import base_source
from veille.sources.base_source import BaseSource, parse_date
from veille.sources.rss_parser import parse_rss


class BingNewsSource(BaseSource):
    """Recherche d'actualités via le flux RSS Bing News."""

    name = "bing_news"

    def fetch(self, topic: dict, since_days: int, max_results: int) -> list:
        """
        Récupère les actualités Bing News pour un sujet.

        Args:
            topic (dict): Sujet.
            since_days (int): Fenêtre temporelle (appliquée en aval).
            max_results (int): Nombre max d'articles par langue.

        Returns:
            list[dict]: Articles standardisés.
        """
        articles = []
        for lang in topic.get("languages", []):
            market = BING_NEWS_MARKETS.get(lang)
            if not market:
                continue
            params = {"q": self.build_query(topic), "format": "rss", "mkt": market}
            raw = base_source.http_get(BING_NEWS_RSS_URL, params)
            for item in parse_rss(raw)[:max_results]:
                articles.append(self.make_article(
                    item["title"], item["link"], item["source"],
                    parse_date(item["pubDate"]), item["description"], lang))
        return articles
