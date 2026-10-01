"""
feed_rss.py
===========
Feature : Source générique « flux RSS / Atom fixe » (blogs des labs, arXiv, releases GitHub).

Description :
    Lit un flux configuré dans config.DIGEST_FEEDS (ou construit pour un dépôt
    GitHub) et retourne ses derniers items, rangés dans le groupe du flux.
    Filtre optionnel par mots-clés (ex. blog NVIDIA → seulement l'IA).

Cas d'usage :
    - OpenAI, DeepMind, Microsoft, NVIDIA, Hugging Face, presse via Google News, arXiv
    - Releases GitHub (claude-code, codex, gemini-cli…)

Entrée  : dict flux {"name", "group", "url", "keywords"?, "max"?}
Sortie  : list[dict] (articles standardisés)
"""

from veille.config import (
    DIGEST_MAX_PER_FEED,
    FEED_SUMMARY_MAX_CHARS,
    GITHUB_RELEASES_MAX,
    GITHUB_RELEASES_URL,
    GROUP_RELEASES,
)
from veille.sources import base_source
from veille.sources.base_source import BaseSource, matches_keywords, parse_date, truncate
from veille.sources.google_news import split_title
from veille.sources.rss_parser import parse_rss


class FeedSource(BaseSource):
    """Un flux RSS/Atom fixe."""

    def __init__(self, feed: dict):
        """
        Args:
            feed (dict): Description du flux (name, group, url, keywords?, max?).

        Returns:
            None
        """
        self.feed = feed
        self.name = feed["name"]

    def fetch(self, topic, since_days: int, max_results: int = None) -> list:
        """
        Récupère les derniers items du flux.

        Args:
            topic (dict | None): Ignoré (flux fixe).
            since_days (int): Ignoré ici (filtrage de date fait par le pipeline).
            max_results (int | None): Max d'items ; défaut feed["max"] ou DIGEST_MAX_PER_FEED.

        Returns:
            list[dict]: Articles standardisés, catégorie = groupe du flux.
        """
        limit = max_results or self.feed.get("max", DIGEST_MAX_PER_FEED)
        articles = []
        for item in parse_rss(base_source.http_get(self.feed["url"])):
            title, publisher = item["title"], item["source"]
            if "news.google.com" in self.feed["url"]:
                title, publisher = split_title(title, publisher)
            text = f"{title} {item['description']}"
            if not matches_keywords(text, self.feed.get("keywords")):
                continue
            articles.append(self.make_article(
                title, item["link"], publisher or self.name, parse_date(item["pubDate"]),
                item["description"], "en", self.feed["group"]))
            if len(articles) >= limit:
                break
        return [{**a, "summary": truncate(a["summary"], FEED_SUMMARY_MAX_CHARS)} for a in articles]


def github_feed(repo: str) -> dict:
    """
    Construit la description du flux de releases d'un dépôt GitHub.

    Args:
        repo (str): "owner/name".

    Returns:
        dict: Flux pour FeedSource.
    """
    return {"name": repo, "group": GROUP_RELEASES, "max": GITHUB_RELEASES_MAX,
            "url": GITHUB_RELEASES_URL.format(repo=repo)}
