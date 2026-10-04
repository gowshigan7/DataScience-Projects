"""
digest_registry.py
==================
Feature : Construction de la liste des sources du digest IA.

Description :
    Assemble, selon les familles demandées (config.DIGEST_SOURCE_KINDS) :
    flux RSS/Atom, releases GitHub, HF Daily Papers, Hacker News, Reddit,
    pages lues par le bot navigateur (si Playwright est installé), boîte mail
    (si IMAP configuré) et Grok/X (si XAI_API_KEY défini).
    Les flux de FEED_BROWSER_FALLBACKS et Reddit reçoivent un secours navigateur.
    Les sources non configurées sont listées dans « skipped » au lieu d'échouer.

Cas d'usage :
    - main.py digest [--skip mail grok]

Entrée  : list[str] familles à ignorer
Sortie  : (list[BaseSource], list[str] sources ignorées)
"""

from veille.config import (
    BROWSER_PAGES,
    DIGEST_FEEDS,
    DIGEST_SOURCE_KINDS,
    FEED_BROWSER_FALLBACKS,
    GITHUB_REPOS,
    GROUP_COMMUNITY,
    REDDIT_BROWSER_LINK_PATTERN,
    REDDIT_BROWSER_URL,
    REDDIT_PERIOD_DAY,
    REDDIT_SUBREDDITS,
)
from veille.sources.browser_page import BrowserPageSource, playwright_available
from veille.sources.fallback import FallbackSource
from veille.sources.feed_rss import FeedSource, github_feed
from veille.sources.grok_x import GrokXSource
from veille.sources.hf_papers import HFPapersSource
from veille.sources.hn_top import HackerNewsTopSource
from veille.sources.mailbox import MailboxSource
from veille.sources.reddit import RedditSource


def build_digest_sources(skip=None) -> tuple:
    """
    Instancie les sources du digest.

    Args:
        skip (list[str] | None): Familles à ignorer (ex. ["mail", "grok"]).

    Returns:
        tuple[list[BaseSource], list[str]]: (sources actives, messages « non configuré »)
    """
    kinds = [k for k in DIGEST_SOURCE_KINDS if k not in (skip or [])]
    use_browser = "browser" in kinds and playwright_available()
    sources, skipped = [], []
    if "feeds" in kinds:
        sources += [with_browser_fallback(FeedSource(f), f, use_browser) for f in DIGEST_FEEDS]
    if "github" in kinds:
        sources += [FeedSource(github_feed(r)) for r in GITHUB_REPOS]
    if "hf_papers" in kinds:
        sources.append(HFPapersSource())
    if "hacker_news" in kinds:
        sources.append(HackerNewsTopSource())
    if "reddit" in kinds:
        sources += [with_browser_fallback(RedditSource(s), reddit_page(s), use_browser)
                    for s in REDDIT_SUBREDDITS]
    if "browser" in kinds:
        if use_browser:
            sources += [BrowserPageSource(p) for p in BROWSER_PAGES]
        else:
            skipped.append("bot navigateur : Playwright non installé (pip install playwright)")
    for kind, source, hint in (
            ("mail", MailboxSource(), "VEILLE_IMAP_USER / VEILLE_IMAP_PASSWORD"),
            ("grok", GrokXSource(), "XAI_API_KEY")):
        if kind not in kinds:
            continue
        if source.is_configured():
            sources.append(source)
        else:
            skipped.append(f"{source.name} : non configuré ({hint})")
    return sources, skipped


def reddit_page(subreddit: str) -> dict:
    """
    Construit la page old.reddit.com lue par le navigateur en secours.

    Args:
        subreddit (str): Nom du subreddit.

    Returns:
        dict: Page pour BrowserPageSource.
    """
    return {"name": f"r/{subreddit}", "group": GROUP_COMMUNITY,
            "url": REDDIT_BROWSER_URL.format(sub=subreddit, period=REDDIT_PERIOD_DAY),
            "link_pattern": REDDIT_BROWSER_LINK_PATTERN.format(sub=subreddit)}


def with_browser_fallback(source, feed: dict, use_browser: bool):
    """
    Ajoute un secours navigateur à une source si une page de repli existe.

    Args:
        source (BaseSource): Source principale.
        feed (dict): Flux (name, group) ou page complète (avec "url" et "link_pattern").
        use_browser (bool): False → source renvoyée telle quelle.

    Returns:
        BaseSource: La source, ou un FallbackSource (principale → navigateur).
    """
    page = feed if "link_pattern" in feed else FEED_BROWSER_FALLBACKS.get(feed.get("name"))
    if not use_browser or not page:
        return source
    page = {"name": feed["name"], "group": feed["group"], **page}
    return FallbackSource(source, BrowserPageSource(page))
