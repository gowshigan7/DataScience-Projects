"""
pipeline.py
===========
Feature : Orchestration collecte → nettoyage pour un sujet.

Description :
    1. Interroge chaque source (une source en erreur n'arrête pas les autres)
    2. Filtre par date
    3. Dédoublonnage (fusionne résumés / médias des reprises)
    4. Score de pertinence + exclusion des homonymes
    5. Catégorisation
    6. Tri : score décroissant puis date décroissante

Cas d'usage :
    - main.py run (sources réelles) ou --dry-run (articles mockés)

Entrée  : Sujet (dict), sources ou articles bruts, fenêtre en jours
Sortie  : (list[dict] articles traités, list[str] erreurs)
"""

from datetime import datetime, timezone

from veille.processing.categorize import categorize
from veille.processing.date_filter import filter_by_date
from veille.processing.dedup import deduplicate
from veille.processing.relevance import filter_relevant

_OLDEST = datetime.min.replace(tzinfo=timezone.utc)


def collect(topic: dict, sources: list, since_days: int, max_results: int):
    """
    Interroge toutes les sources pour un sujet.

    Args:
        topic (dict): Sujet.
        sources (list[BaseSource]): Sources à interroger.
        since_days (int): Fenêtre en jours.
        max_results (int): Nombre max d'articles par source et par langue.

    Returns:
        tuple[list[dict], list[str]]: (articles bruts, messages d'erreur par source)
    """
    articles, errors = [], []
    for source in sources:
        try:
            articles.extend(source.fetch(topic, since_days, max_results))
        except Exception as exc:  # une source KO ne doit pas bloquer la veille
            errors.append(f"{source.name} : {exc}")
    return articles, errors


def process(articles: list, topic: dict, since_days: int, now: datetime = None) -> list:
    """
    Nettoie, enrichit et trie des articles bruts.

    Args:
        articles (list[dict]): Articles bruts.
        topic (dict): Sujet.
        since_days (int): Fenêtre en jours.
        now (datetime | None): Date de référence (tests).

    Returns:
        list[dict]: Articles traités (clés ajoutées : score, also_in, category).
    """
    recent = filter_by_date(articles, since_days, now)
    unique = categorize(filter_relevant(deduplicate(recent), topic))
    unique.sort(key=lambda a: a["published"] or _OLDEST, reverse=True)
    unique.sort(key=lambda a: a["score"], reverse=True)
    return unique
