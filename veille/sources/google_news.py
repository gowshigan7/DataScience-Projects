"""
google_news.py
==============
Feature : Source Google News (flux RSS de recherche, gratuit, sans clé).

Description :
    Interroge https://news.google.com/rss/search pour chaque langue du sujet,
    avec l'opérateur « when:Nd » pour limiter la fenêtre temporelle.
    Les titres Google sont au format « Titre - Média » : le média est extrait.

Cas d'usage :
    - Source principale de presse généraliste et spécialisée

Entrée  : Sujet (dict), fenêtre en jours, nombre max d'articles
Sortie  : list[dict] (articles standardisés)
"""

from veille.config import GOOGLE_NEWS_LOCALES, GOOGLE_NEWS_RSS_URL
from veille.sources import base_source
from veille.sources.base_source import BaseSource, parse_date
from veille.sources.rss_parser import parse_rss


class GoogleNewsSource(BaseSource):
    """Recherche d'actualités via le flux RSS Google News."""

    name = "google_news"

    def fetch(self, topic: dict, since_days: int, max_results: int) -> list:
        """
        Récupère les actualités Google News pour un sujet.

        Args:
            topic (dict): Sujet.
            since_days (int): Fenêtre temporelle en jours.
            max_results (int): Nombre max d'articles par langue.

        Returns:
            list[dict]: Articles standardisés.
        """
        articles = []
        for lang in topic.get("languages", []):
            locale = GOOGLE_NEWS_LOCALES.get(lang)
            if not locale:
                continue
            params = {"q": f"{self.build_query(topic)} when:{since_days}d", **locale}
            raw = base_source.http_get(GOOGLE_NEWS_RSS_URL, params)
            for item in parse_rss(raw)[:max_results]:
                title, publisher = split_title(item["title"], item["source"])
                articles.append(self.make_article(
                    title, item["link"], publisher, parse_date(item["pubDate"]),
                    "", lang))
        return articles


def split_title(title: str, publisher: str):
    """
    Sépare « Titre - Média » en (titre, média).

    Args:
        title (str): Titre brut Google News.
        publisher (str): Média fourni par la balise <source> (peut être vide).

    Returns:
        tuple[str, str]: (titre nettoyé, média)
    """
    if " - " in title:
        head, tail = title.rsplit(" - ", 1)
        if not publisher or tail.strip() == publisher.strip():
            return head.strip(), tail.strip()
    return title.strip(), publisher
