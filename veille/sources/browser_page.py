"""
browser_page.py
===============
Feature : Bot navigateur (Playwright) — lit les liens d'articles d'une page web.

Description :
    Pour les sites sans flux RSS ou qui refusent les requêtes simples
    (pages rendues en JavaScript, protections anti-bot légères) :
    1. ouvre la page dans Chromium headless
    2. récupère tous les liens <a> (URL absolue, texte, date <time> proche)
    3. garde ceux dont l'URL correspond à link_pattern et dont le texte
       ressemble à un titre (longueur minimale), sans doublon

    Playwright est optionnel : `pip install playwright` (puis
    `playwright install chromium` si aucun Chromium n'est présent).

Cas d'usage :
    - Anthropic, xAI, Meta AI, Mistral, Qwen, changelog Cursor
    - Secours quand un flux RSS ou Reddit échoue (voir fallback.py)

Entrée  : dict page {"name", "group", "url", "link_pattern"}
Sortie  : list[dict] (articles standardisés)
"""

import re

from veille.config import (
    BROWSER_EXECUTABLE_PATH,
    BROWSER_MAX_TITLE_CHARS,
    BROWSER_MIN_TITLE_CHARS,
    BROWSER_PREFERRED_TITLE_CHARS,
    BROWSER_SETTLE_MS,
    BROWSER_TIMEOUT_MS,
    BROWSER_USER_AGENT,
    DIGEST_MAX_PER_FEED,
)
from veille.sources.base_source import BaseSource, clean_text, parse_date, truncate

# Script exécuté dans la page : liens + date d'un <time> dans le lien ou sa « carte » parente.
_COLLECT_LINKS_JS = """
() => Array.from(document.querySelectorAll('a[href]')).map(a => {
  let node = a, time = a.querySelector('time');
  for (let i = 0; i < 3 && !time && node.parentElement; i++) {
    node = node.parentElement; time = node.querySelector('time');
  }
  return {href: a.href, text: a.innerText || a.textContent || '',
          date: time ? (time.getAttribute('datetime') || time.textContent) : ''};
})
"""


def playwright_available() -> bool:
    """
    Indique si Playwright est installé.

    Returns:
        bool: True si `playwright` est importable.
    """
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        return False
    return True


def render_links(url: str) -> list:
    """
    Ouvre une page dans Chromium headless et retourne ses liens.

    Args:
        url (str): Page à ouvrir.

    Returns:
        list[dict]: Liens {"href", "text", "date"}.
    """
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=BROWSER_EXECUTABLE_PATH)
        try:
            page = browser.new_page(user_agent=BROWSER_USER_AGENT)
            page.goto(url, timeout=BROWSER_TIMEOUT_MS, wait_until="domcontentloaded")
            page.wait_for_timeout(BROWSER_SETTLE_MS)
            return page.evaluate(_COLLECT_LINKS_JS)
        finally:
            browser.close()


def select_article_links(links: list, link_pattern: str) -> list:
    """
    Garde les liens qui ressemblent à des articles.

    Args:
        links (list[dict]): Liens {"href", "text", "date"}.
        link_pattern (str): Regex que l'URL doit vérifier.

    Returns:
        list[dict]: Liens retenus, sans doublon d'URL. Titre = première ligne d'au moins
        BROWSER_PREFERRED_TITLE_CHARS caractères (sinon la plus longue) ; le reste = résumé.
    """
    regex = re.compile(link_pattern)
    kept, seen = [], set()
    for link in links:
        href = link.get("href", "").split("#")[0]
        if not regex.search(href) or href in seen:
            continue
        lines = [clean_text(l) for l in link.get("text", "").splitlines() if clean_text(l)]
        titles = [l for l in lines if len(l) >= BROWSER_MIN_TITLE_CHARS]
        if not titles:
            continue
        seen.add(href)
        long_enough = [t for t in titles if len(t) >= BROWSER_PREFERRED_TITLE_CHARS]
        title = long_enough[0] if long_enough else max(titles, key=len)
        rest = " ".join(l for l in lines if l != title)
        kept.append({"href": href, "title": truncate(title, BROWSER_MAX_TITLE_CHARS),
                     "summary": rest, "date": clean_text(link.get("date", ""))})
    return kept


class BrowserPageSource(BaseSource):
    """Page web lue par un navigateur headless."""

    def __init__(self, page: dict, renderer=render_links):
        """
        Args:
            page (dict): {"name", "group", "url", "link_pattern"}.
            renderer (callable): url -> liens (remplaçable en test).

        Returns:
            None
        """
        self.page, self.renderer = page, renderer
        self.name = f"{page['name']} (navigateur)"

    def is_configured(self) -> bool:
        """
        Indique si le bot peut tourner (Playwright installé ou renderer injecté).

        Returns:
            bool: True si utilisable.
        """
        return self.renderer is not render_links or playwright_available()

    def fetch(self, topic, since_days: int, max_results: int = DIGEST_MAX_PER_FEED) -> list:
        """
        Lit la page et retourne ses articles.

        Args:
            topic (dict | None): Ignoré.
            since_days (int): Ignoré (filtrage par le pipeline ; sans date, l'article est gardé
                puis l'historique n'affiche 🆕 qu'à sa première apparition).
            max_results (int): Nombre max d'articles.

        Returns:
            list[dict]: Articles standardisés.
        """
        links = select_article_links(self.renderer(self.page["url"]), self.page["link_pattern"])
        return [self.make_article(l["title"], l["href"], self.page["name"], parse_date(l["date"]),
                                  l["summary"], "en", self.page["group"])
                for l in links[:max_results or DIGEST_MAX_PER_FEED]]
