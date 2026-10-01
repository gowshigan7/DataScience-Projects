"""
grok_x.py
=========
Feature : Source « X via Grok » — posts récents des comptes suivis (labs, chercheurs).

Description :
    Appelle l'API Responses de xAI avec l'outil serveur x_search, limité aux
    comptes config.X_HANDLES (par paquets de 20, limite de l'outil) et à la
    fenêtre de dates. Grok répond en JSON (handle, date, text, url) ; si la
    réponse n'est pas du JSON valide, on se rabat sur les citations (URLs de posts).

    Nécessite XAI_API_KEY (payant à l'usage). Modèle : VEILLE_GROK_MODEL.

Cas d'usage :
    - Suivre OpenAI, DeepMind, xAI, Anthropic, Meta, Mistral, DeepSeek, Qwen,
      Karpathy, LeCun, Mollick… sans scraper X

Entrée  : Comptes X, fenêtre en jours
Sortie  : list[dict] (articles standardisés, groupe X)
"""

import json
import re
from datetime import datetime, timedelta, timezone

from veille.config import (
    GROK_MAX_HANDLES_PER_CALL,
    GROK_MAX_POSTS_PER_CALL,
    GROK_MODEL,
    GROK_PROMPT,
    GROK_TIMEOUT_SECONDS,
    GROUP_X,
    ISO_DATE_FORMAT,
    X_HANDLES,
    X_TITLE_CHARS,
    XAI_API_KEY,
    XAI_RESPONSES_URL,
)
from veille.sources import base_source
from veille.sources.base_source import BaseSource, parse_date, truncate

_JSON_ARRAY_RE = re.compile(r"\[.*\]", re.S)
_X_STATUS_RE = re.compile(r"https?://(?:www\.)?(?:x|twitter)\.com/([^/]+)/status/\d+")



def extract_output(response: dict) -> tuple:
    """
    Extrait le texte et les URLs citées d'une réponse de l'API Responses.

    Args:
        response (dict): Réponse JSON de /v1/responses.

    Returns:
        tuple[str, list[str]]: (texte concaténé, URLs citées sans doublon)
    """
    texts, urls = [], list(response.get("citations") or [])
    for item in response.get("output", []):
        for part in item.get("content") or []:
            if part.get("type") == "output_text":
                texts.append(part.get("text", ""))
                urls += [a.get("url") for a in part.get("annotations") or [] if a.get("url")]
    return "\n".join(texts), list(dict.fromkeys(urls))


def parse_posts(text: str) -> list:
    """
    Parse le tableau JSON renvoyé par Grok (tolère un bloc ```json).

    Args:
        text (str): Texte de la réponse.

    Returns:
        list[dict]: Posts {handle, date, text, url} ; [] si illisible.
    """
    match = _JSON_ARRAY_RE.search(text or "")
    if not match:
        return []
    try:
        posts = json.loads(match.group(0))
    except json.JSONDecodeError:
        return []
    return [p for p in posts if isinstance(p, dict) and p.get("url")]


class GrokXSource(BaseSource):
    """Posts X récents des comptes suivis, via Grok (xAI)."""

    name = "grok_x"

    def __init__(self, api_key=XAI_API_KEY, handles=None, model=GROK_MODEL):
        """
        Args:
            api_key (str): Clé xAI.
            handles (list[str] | None): Comptes X (défaut X_HANDLES).
            model (str): Modèle Grok.

        Returns:
            None
        """
        self.api_key, self.model = api_key, model
        self.handles = X_HANDLES if handles is None else handles

    def is_configured(self) -> bool:
        """
        Indique si la clé API est renseignée.

        Returns:
            bool: True si XAI_API_KEY est défini.
        """
        return bool(self.api_key)

    def fetch(self, topic, since_days: int, max_results: int = GROK_MAX_POSTS_PER_CALL) -> list:
        """
        Interroge Grok par paquets de comptes.

        Args:
            topic (dict | None): Ignoré.
            since_days (int): Fenêtre en jours.
            max_results (int): Posts max par appel.

        Returns:
            list[dict]: Articles standardisés.
        """
        from_date = (datetime.now(timezone.utc) - timedelta(days=since_days)).strftime(ISO_DATE_FORMAT)
        articles = []
        for i in range(0, len(self.handles), GROK_MAX_HANDLES_PER_CALL):
            chunk = self.handles[i:i + GROK_MAX_HANDLES_PER_CALL]
            payload = {
                "model": self.model,
                "input": [{"role": "user", "content": GROK_PROMPT.format(
                    from_date=from_date, max_posts=max_results)}],
                "tools": [{"type": "x_search", "allowed_x_handles": chunk, "from_date": from_date}],
            }
            response = base_source.http_post_json(
                XAI_RESPONSES_URL, payload, {"Authorization": f"Bearer {self.api_key}"},
                GROK_TIMEOUT_SECONDS)
            text, urls = extract_output(response)
            posts = parse_posts(text) or [{"url": u} for u in urls if _X_STATUS_RE.match(u)]
            articles += [self._to_article(p) for p in posts]
        return articles

    def _to_article(self, post: dict) -> dict:
        """
        Convertit un post renvoyé par Grok en article.

        Args:
            post (dict): {handle?, date?, text?, url}.

        Returns:
            dict: Article standardisé.
        """
        handle = (post.get("handle") or "").lstrip("@")
        if not handle:
            m = _X_STATUS_RE.match(post["url"])
            handle = m.group(1) if m else "X"
        text = post.get("text") or post["url"]
        return self.make_article(f"@{handle} : {truncate(text, X_TITLE_CHARS)}", post["url"],
                                 f"X · @{handle}", parse_date(post.get("date", "")),
                                 text if len(text) > X_TITLE_CHARS else "", "", GROUP_X)
