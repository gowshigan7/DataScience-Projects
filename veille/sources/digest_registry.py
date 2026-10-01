"""
digest_registry.py
==================
Feature : Construction de la liste des sources du digest IA.

Description :
    Assemble, selon les familles demandées (config.DIGEST_SOURCE_KINDS) :
    flux RSS/Atom, releases GitHub, HF Daily Papers, Hacker News, Reddit,
    boîte mail (si IMAP configuré) et Grok/X (si XAI_API_KEY défini).
    Les sources non configurées sont listées dans « skipped » au lieu d'échouer.

Cas d'usage :
    - main.py digest [--skip mail grok]

Entrée  : list[str] familles à ignorer
Sortie  : (list[BaseSource], list[str] sources ignorées)
"""

from veille.config import DIGEST_FEEDS, DIGEST_SOURCE_KINDS, GITHUB_REPOS, REDDIT_SUBREDDITS
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
    sources, skipped = [], []
    if "feeds" in kinds:
        sources += [FeedSource(f) for f in DIGEST_FEEDS]
    if "github" in kinds:
        sources += [FeedSource(github_feed(r)) for r in GITHUB_REPOS]
    if "hf_papers" in kinds:
        sources.append(HFPapersSource())
    if "hacker_news" in kinds:
        sources.append(HackerNewsTopSource())
    if "reddit" in kinds:
        sources += [RedditSource(s) for s in REDDIT_SUBREDDITS]
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
