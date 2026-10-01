"""
mock_digest.py
==============
Feature : Données de démonstration du digest IA (--dry-run et tests).

Description :
    Articles FICTIFS, marqués « [Démo] », un ou deux par groupe, pour montrer la
    mise en forme du rapport sans réseau. Les liens pointent vers les pages
    d'accueil réelles des sources. Contient un doublon et un article trop ancien.

Cas d'usage :
    - python -m veille.main digest --dry-run
    - tests unitaires

Entrée  : Aucune
Sortie  : MOCK_DIGEST_ARTICLES (list[dict]), MOCK_DIGEST_NOW (datetime)
"""

from datetime import datetime, timedelta, timezone

from veille.config import (
    GROUP_COMMUNITY,
    GROUP_LABS,
    GROUP_NEWSLETTERS,
    GROUP_PRESS,
    GROUP_RELEASES,
    GROUP_RESEARCH,
    GROUP_X,
)

MOCK_DIGEST_NOW = datetime(2026, 10, 1, 8, tzinfo=timezone.utc)


def _a(title, url, source, publisher, hours_ago, category, summary=""):
    """
    Construit un article de démo.

    Args:
        title (str): Titre.
        url (str): Lien.
        source (str): Nom de la source.
        publisher (str): Média / auteur.
        hours_ago (int | None): Ancienneté en heures (None = date inconnue).
        category (str): Groupe du digest.
        summary (str): Extrait.

    Returns:
        dict: Article standardisé.
    """
    published = None if hours_ago is None else MOCK_DIGEST_NOW - timedelta(hours=hours_ago)
    return {"title": title, "url": url, "source": source, "publisher": publisher,
            "published": published, "summary": summary, "language": "en", "category": category}


MOCK_DIGEST_ARTICLES = [
    _a("[Démo] Billet du blog OpenAI", "https://openai.com/news/", "OpenAI", "OpenAI", 3, GROUP_LABS),
    _a("[Démo] Billet du blog Google DeepMind", "https://deepmind.google/discover/blog/",
       "Google DeepMind", "Google DeepMind", 6, GROUP_LABS),
    _a("[Démo] Article de presse sur Anthropic", "https://www.anthropic.com/news",
       "Anthropic (presse)", "Exemple Média", 5, GROUP_PRESS),
    _a("@karpathy : [Démo] post X résumé par Grok", "https://x.com/karpathy",
       "grok_x", "X · @karpathy", 2, GROUP_X),
    _a("[Démo] Newsletter du matin", "https://example.com/newsletter/web-version",
       "mailbox", "Exemple Newsletter", 1, GROUP_NEWSLETTERS,
       "Le résumé reprend les premières lignes de la newsletter…"),
    _a("[Démo] Papier du jour", "https://huggingface.co/papers", "hf_papers",
       "HF Daily Papers", 10, GROUP_RESEARCH, "▲ 120 · Abstract tronqué…"),
    _a("[Démo] anthropics/claude-code vX.Y.Z", "https://github.com/anthropics/claude-code/releases",
       "anthropics/claude-code", "anthropics/claude-code", 8, GROUP_RELEASES),
    _a("[Démo] Discussion populaire sur Hacker News", "https://news.ycombinator.com/",
       "hacker_news_top", "Hacker News", 7, GROUP_COMMUNITY, "▲ 450 · 210 commentaires"),
    _a("[Démo] Post populaire r/LocalLLaMA", "https://www.reddit.com/r/LocalLLaMA/",
       "r/LocalLLaMA", "r/LocalLLaMA", 9, GROUP_COMMUNITY, "▲ 800 · 150 commentaires"),
    # Doublon (même lien que le billet OpenAI, repris par un autre flux)
    _a("[Démo] Billet du blog OpenAI", "https://openai.com/news/", "Anthropic (presse)",
       "Autre Média", 4, GROUP_PRESS),
    # Trop ancien pour une fenêtre d'un jour
    _a("[Démo] Vieille annonce", "https://example.com/old", "OpenAI", "OpenAI", 72, GROUP_LABS),
]
