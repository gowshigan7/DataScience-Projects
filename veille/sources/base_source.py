"""
base_source.py
==============
Feature : Interface commune à toutes les sources + format standard d'un article.

Description :
    Chaque source étend BaseSource et implémente fetch(topic, since_days).
    Elle retourne une list[dict] construite avec BaseSource.make_article() :
        {"title", "url", "source", "publisher", "published" (datetime UTC | None),
         "summary", "language"}
    Les fonctions HTTP (http_get) sont centralisées ici pour que les tests
    puissent les remplacer facilement.

Cas d'usage :
    - Ajouter une nouvelle source = créer un fichier qui étend BaseSource

Entrée  : Sujet (dict), fenêtre temporelle (jours)
Sortie  : list[dict] (articles au format standard)
"""

import html
import re
import urllib.parse
import urllib.request
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from veille.config import HTTP_TIMEOUT_SECONDS, HTTP_USER_AGENT

_TAG_RE = re.compile(r"<[^>]+>")


def http_get(url: str, params: dict = None) -> bytes:
    """
    Effectue une requête HTTP GET.

    Args:
        url (str): URL de base.
        params (dict | None): Paramètres de requête.

    Returns:
        bytes: Corps de la réponse.
    """
    if params:
        url = f"{url}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": HTTP_USER_AGENT})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
        return resp.read()


def clean_text(text: str) -> str:
    """
    Retire les balises HTML et décode les entités.

    Args:
        text (str): Texte brut (éventuellement HTML).

    Returns:
        str: Texte propre sur une ligne.
    """
    return " ".join(html.unescape(_TAG_RE.sub(" ", text or "")).split())


def parse_date(value: str):
    """
    Parse une date RFC 822 (RSS) ou ISO 8601 (API JSON) en datetime UTC.

    Args:
        value (str): Date textuelle.

    Returns:
        datetime | None: Date en UTC, ou None si non parsable.
    """
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class BaseSource(ABC):
    """Interface commune des sources d'information."""

    name = "base"

    @abstractmethod
    def fetch(self, topic: dict, since_days: int, max_results: int) -> list:
        """
        Récupère les articles pour un sujet.

        Args:
            topic (dict): Sujet (voir topics.make_topic).
            since_days (int): Fenêtre temporelle en jours.
            max_results (int): Nombre max d'articles par langue.

        Returns:
            list[dict]: Articles au format standard.
        """

    @staticmethod
    def build_query(topic: dict) -> str:
        """
        Construit une requête « nom exact » OU alias.

        Args:
            topic (dict): Sujet.

        Returns:
            str: Requête, ex. '"Shift Technology" OR "Shift Tech"'.
        """
        terms = [topic["name"]] + topic.get("aliases", [])
        return " OR ".join(f'"{t}"' for t in terms)

    def make_article(self, title, url, publisher="", published=None, summary="", language=""):
        """
        Construit un article au format standard.

        Args:
            title (str): Titre.
            url (str): Lien.
            publisher (str): Média éditeur.
            published (datetime | None): Date de publication UTC.
            summary (str): Résumé / extrait.
            language (str): Code langue.

        Returns:
            dict: Article standardisé.
        """
        return {
            "title": clean_text(title),
            "url": url.strip(),
            "source": self.name,
            "publisher": clean_text(publisher),
            "published": published,
            "summary": clean_text(summary),
            "language": language,
        }
