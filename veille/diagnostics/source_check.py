"""
source_check.py
===============
Feature : Diagnostic des sources du digest (commande « check »).

Description :
    Interroge chaque source une par une et mesure : statut (OK / VIDE / ERREUR /
    NON CONFIGURÉ), nombre d'items, durée, méthode réellement utilisée
    (flux ou secours navigateur) et un exemple de titre. Permet de savoir,
    sur sa propre machine, quelles sources passent par la méthode la plus
    simple et lesquelles ont besoin du bot navigateur.

Cas d'usage :
    - python -m veille.main check
    - python -m veille.main check --only reddit anthropic

Entrée  : list[BaseSource], list[str] sources non configurées
Sortie  : list[dict] lignes de diagnostic / str tableau texte
"""

import time

from veille.config import (
    CHECK_ERROR_CHARS,
    CHECK_SAMPLE_CHARS,
    CHECK_STATUS_EMPTY,
    CHECK_STATUS_ERROR,
    CHECK_STATUS_OK,
    CHECK_STATUS_SKIPPED,
)
from veille.sources.base_source import truncate


def check_source(source, since_days: int, max_results: int) -> dict:
    """
    Teste une source.

    Args:
        source (BaseSource): Source à tester.
        since_days (int): Fenêtre en jours.
        max_results (int): Items max.

    Returns:
        dict: name, status, count, seconds, via, sample, error.
    """
    start = time.perf_counter()
    row = {"name": source.name, "count": 0, "via": "", "sample": "", "error": ""}
    try:
        articles = source.fetch(None, since_days, max_results)
        row["count"] = len(articles)
        row["status"] = CHECK_STATUS_OK if articles else CHECK_STATUS_EMPTY
        row["sample"] = truncate(articles[0]["title"], CHECK_SAMPLE_CHARS) if articles else ""
    except Exception as exc:  # le diagnostic doit continuer
        first_line = str(exc).strip().splitlines()[0] if str(exc).strip() else ""
        row["status"] = CHECK_STATUS_ERROR
        row["error"] = truncate(f"{type(exc).__name__}: {first_line}", CHECK_ERROR_CHARS)
    row["seconds"] = round(time.perf_counter() - start, 1)
    if getattr(source, "last_used", None):
        row["via"] = source.last_used
        if getattr(source, "primary_error", None):
            row["error"] = f"flux KO ({type(source.primary_error).__name__}) → secours"
    return row


def check_sources(sources: list, skipped: list, since_days: int, max_results: int,
                  progress=None) -> list:
    """
    Teste toutes les sources.

    Args:
        sources (list[BaseSource]): Sources actives.
        skipped (list[str]): Messages des sources non configurées.
        since_days (int): Fenêtre en jours.
        max_results (int): Items max par source.
        progress (callable | None): Appelé avec le nom de chaque source testée.

    Returns:
        list[dict]: Une ligne par source (+ une par source non configurée).
    """
    rows = []
    for source in sources:
        if progress:
            progress(source.name)
        rows.append(check_source(source, since_days, max_results))
    rows += [{"name": s.split(" : ")[0], "status": CHECK_STATUS_SKIPPED, "count": 0,
              "seconds": 0, "via": "", "sample": "", "error": s.split(" : ", 1)[-1]}
             for s in skipped]
    return rows


def format_check(rows: list) -> str:
    """
    Met en forme le diagnostic en tableau texte + résumé.

    Args:
        rows (list[dict]): Lignes de check_sources().

    Returns:
        str: Tableau prêt à imprimer.
    """
    width = max([len(r["name"]) for r in rows] + [6])
    out = [f"{'SOURCE':<{width}}  {'STATUT':<13} {'ITEMS':>5} {'SEC':>5}  DÉTAIL"]
    for r in rows:
        detail = r["error"] or r["sample"]
        if r["via"] and r["via"] != r["name"]:
            detail = f"[via {r['via']}] {detail}"
        out.append(f"{r['name']:<{width}}  {r['status']:<13} {r['count']:>5} {r['seconds']:>5}  {detail}")
    counts = {s: sum(r["status"] == s for r in rows) for s in
              (CHECK_STATUS_OK, CHECK_STATUS_EMPTY, CHECK_STATUS_ERROR, CHECK_STATUS_SKIPPED)}
    out.append("\n" + " · ".join(f"{s} : {n}" for s, n in counts.items()))
    return "\n".join(out)
