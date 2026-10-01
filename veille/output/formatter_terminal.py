"""
formatter_terminal.py
=====================
Feature : Affichage du rapport de veille dans le terminal.

Description :
    Pour chaque sujet : nombre d'articles (dont nouveaux), puis les articles
    groupés par catégorie avec date, média, titre et lien.

Cas d'usage :
    - Consultation rapide : python -m veille.main run

Entrée  : list[dict] résultats {"topic", "articles", "errors"}
Sortie  : str (texte à afficher)
"""

from veille.config import NEW_BADGE, TERMINAL_TITLE_WIDTH
from veille.output.grouping import format_date, group_by_category


def format_terminal(results: list) -> str:
    """
    Construit le rapport texte.

    Args:
        results (list[dict]): Un dict par sujet : topic, articles, errors.

    Returns:
        str: Rapport prêt à imprimer.
    """
    lines = []
    for res in results:
        arts = res["articles"]
        n_new = sum(a.get("is_new", False) for a in arts)
        lines += ["=" * TERMINAL_TITLE_WIDTH,
                  f"  VEILLE : {res['topic']['name']}  —  {len(arts)} articles ({n_new} nouveaux)",
                  "=" * TERMINAL_TITLE_WIDTH]
        if res.get("links"):
            lines.append("\n▶ À ouvrir à la main")
            lines += [f"  {l['label']} : {l['url']}" for l in res["links"]]
        for category, items in group_by_category(arts):
            lines.append(f"\n▶ {category} ({len(items)})")
            for a in items:
                badge = f"{NEW_BADGE} " if a.get("is_new") else ""
                title = a["title"][:TERMINAL_TITLE_WIDTH]
                lines.append(f"  {badge}[{format_date(a)}] {a['publisher'] or a['source']} — {title}")
                lines.append(f"      {a['url']}")
        for err in res.get("errors", []):
            lines.append(f"\n  ⚠ Source indisponible : {err}")
        for note in res.get("skipped", []):
            lines.append(f"  ℹ Source ignorée — {note}")
        lines.append("")
    return "\n".join(lines)
