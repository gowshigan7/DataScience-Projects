"""
hf_papers.py
============
Feature : Source Hugging Face Daily Papers (papiers du jour sélectionnés par la communauté).

Description :
    Lit l'API JSON https://huggingface.co/api/daily_papers et garde les papiers
    ayant au moins HF_PAPERS_MIN_UPVOTES votes, triés par votes.

Cas d'usage :
    - Repérer les papiers arXiv qui font parler d'eux

Entrée  : Aucune (flux fixe)
Sortie  : list[dict] (articles standardisés, groupe Recherche)
"""

import json

from veille.config import (
    FEED_SUMMARY_MAX_CHARS,
    GROUP_RESEARCH,
    HF_DAILY_PAPERS_URL,
    HF_PAPER_URL,
    HF_PAPERS_MIN_UPVOTES,
)
from veille.sources import base_source
from veille.sources.base_source import BaseSource, parse_date, truncate


class HFPapersSource(BaseSource):
    """Papiers du jour Hugging Face."""

    name = "hf_papers"

    def fetch(self, topic, since_days: int, max_results: int) -> list:
        """
        Récupère les papiers du jour les plus votés.

        Args:
            topic (dict | None): Ignoré.
            since_days (int): Ignoré (filtrage par le pipeline).
            max_results (int): Nombre max de papiers.

        Returns:
            list[dict]: Articles standardisés.
        """
        entries = json.loads(base_source.http_get(HF_DAILY_PAPERS_URL))
        papers = []
        for e in entries:
            p = e.get("paper", {})
            votes = p.get("upvotes", 0)
            if votes < HF_PAPERS_MIN_UPVOTES:
                continue
            papers.append((votes, self.make_article(
                p.get("title") or e.get("title", ""), f"{HF_PAPER_URL}{p.get('id', '')}",
                "HF Daily Papers", parse_date(e.get("publishedAt") or p.get("publishedAt", "")),
                f"▲ {votes} · {truncate(p.get('summary', ''), FEED_SUMMARY_MAX_CHARS)}",
                "en", GROUP_RESEARCH)))
        papers.sort(key=lambda x: x[0], reverse=True)
        return [a for _, a in papers[:max_results]]
