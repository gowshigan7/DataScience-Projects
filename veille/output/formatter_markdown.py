"""
formatter_markdown.py
=====================
Feature : Rapport de veille au format Markdown.

Description :
    Un titre par sujet, une section par catégorie, une puce par article
    (date, média, lien, extrait, reprises par d'autres médias).

Cas d'usage :
    - Coller le rapport dans Notion, un wiki ou un e-mail

Entrée  : list[dict] résultats, str date de génération
Sortie  : str (Markdown)
"""

from veille.config import NEW_BADGE
from veille.output.grouping import format_date, group_by_category


def format_markdown(results: list, generated_at: str) -> str:
    """
    Construit le rapport Markdown.

    Args:
        results (list[dict]): Un dict par sujet : topic, articles, errors.
        generated_at (str): Date de génération affichée.

    Returns:
        str: Rapport Markdown.
    """
    out = [f"# Rapport de veille — {generated_at}", ""]
    for res in results:
        arts = res["articles"]
        n_new = sum(a.get("is_new", False) for a in arts)
        out += [f"## {res['topic']['name']}", "",
                f"*{len(arts)} articles, dont {n_new} nouveaux.*", ""]
        for category, items in group_by_category(arts):
            out += [f"### {category}", ""]
            for a in items:
                badge = f"{NEW_BADGE} " if a.get("is_new") else ""
                out.append(f"- {badge}**[{a['title']}]({a['url']})** — "
                           f"{a['publisher'] or a['source']}, {format_date(a)}")
                if a.get("summary"):
                    out.append(f"  > {a['summary']}")
                if a.get("also_in"):
                    out.append(f"  *Repris aussi par : {', '.join(a['also_in'])}*")
            out.append("")
        for err in res.get("errors", []):
            out.append(f"> ⚠ Source indisponible : {err}")
    return "\n".join(out).rstrip() + "\n"
