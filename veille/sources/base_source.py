"""
base_source.py
==============
Feature : Interface commune à toutes les sources + format standard d'un article.

Description :
    Chaque source étend BaseSource et implémente fetch(topic, since_days).
    Elle retourne une list[dict] construite avec BaseSource.make_article() :
        {"title", "url", "source", "publisher", "published" (datetime UTC | None),
         "summary", "language", "category" (str | None, fixé par les sources du digest)}
    Les fonctions HTTP (http_get) sont centralisées ici pour que les tests
    puissent les remplacer facilement.

Cas d'usage :
    - Ajouter une nouvelle source = créer un fichier qui étend BaseSource

Entrée  : Sujet (dict), fenêtre temporelle (jours)
Sortie  : list[dict] (articles au format standard)
"""

import html
import json
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


def http_post_json(url: str, payload: dict, headers: dict, timeout: int) -> dict:
    """
    Effectue une requête HTTP POST JSON et décode la réponse JSON.

    Args:
        url (str): URL.
        payload (dict): Corps de la requête.
        headers (dict): En-têtes supplémentaires (ex. Authorization).
        timeout (int): Délai max en secondes.

    Returns:
        dict: Réponse décodée.
    """
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type": "application/json", "User-Agent": HTTP_USER_AGENT, **headers})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read())


def matches_keywords(text: str, keywords: list) -> bool:
    """
    Teste si un texte contient au moins un mot-clé (mot entier, insensible à la casse).

    Args:
        text (str): Texte.
        keywords (list[str] | None): Mots-clés ; si vide/None, retourne True.

    Returns:
        bool: True si aucun mot-clé n'est exigé ou si l'un d'eux est présent.
    """
    if not keywords:
        return True
    low = text.lower()
    return any(re.search(rf"(?<!\w){re.escape(k.lower())}(?!\w)", low) for k in keywords)


def clean_text(text: str) -> str:
    """
    Retire les balises HTML et décode les entités.

    Args:
        text (str): Texte brut (éventuellement HTML).

    Returns:
        str: Texte propre sur une ligne.
    """
    return " ".join(html.unescape(_TAG_RE.sub(" ", text or "")).split())


def truncate(text: str, max_chars: int) -> str:
    """
    Tronque un texte sur une frontière de mot.

    Args:
        text (str): Texte.
        max_chars (int): Longueur maximale.

    Returns:
        str: Texte tronqué (suffixe « … ») ou inchangé.
    """
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "…"


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

    def make_article(self, title, url, publisher="", published=None, summary="", language="",
                     category=None):
        """
        Construit un article au format standard.

        Args:
            title (str): Titre.
            url (str): Lien.
            publisher (str): Média éditeur.
            published (datetime | None): Date de publication UTC.
            summary (str): Résumé / extrait.
            language (str): Code langue.
            category (str | None): Groupe d'affichage (digest) ; None = calculé plus tard.

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
            "category": category,
        }
