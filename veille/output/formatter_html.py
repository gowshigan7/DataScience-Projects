"""
formatter_html.py
=================
Feature : Rapport de veille au format HTML autonome (un seul fichier, sans dépendance).

Description :
    Page lisible dans un navigateur : un bloc par sujet, compteurs par
    catégorie, cartes d'articles (badge « Nouveau », média, date, extrait,
    reprises), champ de recherche pour filtrer, thème clair/sombre automatique.

Cas d'usage :
    - Ouvrir le rapport du jour dans le navigateur, le partager par e-mail

Entrée  : list[dict] résultats, str date de génération
Sortie  : str (HTML)
"""

from html import escape

from veille.output.grouping import format_date, group_by_category

_CSS = """
:root{--bg:#f7f7f5;--card:#fff;--text:#1d1d1b;--muted:#6b6b66;--line:#e4e4df;--accent:#2f5bd3;--new:#0f7b4b}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--card:#20201f;--text:#ececea;--muted:#a3a39e;--line:#33332f;--accent:#8aa8ff;--new:#4fd197}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,sans-serif}
main{max-width:860px;margin:0 auto;padding:24px 16px 64px}h1{font-size:1.6rem;margin:0 0 4px}
.sub{color:var(--muted);margin:0 0 20px}input{width:100%;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--text);font:inherit;margin-bottom:24px}
section.topic{margin-bottom:40px}h2{font-size:1.3rem;margin:0 0 8px}.chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:16px}
.chip{border:1px solid var(--line);border-radius:999px;padding:2px 10px;font-size:.85rem;color:var(--muted)}
h3{font-size:1rem;margin:20px 0 8px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}
article{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin-bottom:8px}
article a{color:var(--accent);font-weight:600;text-decoration:none}article a:hover{text-decoration:underline}
.meta{color:var(--muted);font-size:.85rem;margin-top:2px}.sum{margin:6px 0 0;font-size:.92rem}
.new{color:var(--new);font-weight:700;font-size:.75rem;margin-right:6px}.err{color:#c0392b;font-size:.9rem}
"""

_JS = """
document.getElementById('q').addEventListener('input',e=>{const q=e.target.value.toLowerCase();
document.querySelectorAll('article').forEach(a=>{a.style.display=a.textContent.toLowerCase().includes(q)?'':'none'})});
"""


def _article_html(a: dict) -> str:
    """
    Construit la carte HTML d'un article.

    Args:
        a (dict): Article traité.

    Returns:
        str: Fragment HTML.
    """
    badge = '<span class="new">NOUVEAU</span>' if a.get("is_new") else ""
    meta = f"{escape(a['publisher'] or a['source'])} · {format_date(a)}"
    if a.get("also_in"):
        meta += f" · repris par {escape(', '.join(a['also_in']))}"
    summary = f'<p class="sum">{escape(a["summary"])}</p>' if a.get("summary") else ""
    return (f'<article>{badge}<a href="{escape(a["url"])}" target="_blank" rel="noopener">'
            f'{escape(a["title"])}</a><div class="meta">{meta}</div>{summary}</article>')


def format_html(results: list, generated_at: str) -> str:
    """
    Construit le rapport HTML complet.

    Args:
        results (list[dict]): Un dict par sujet : topic, articles, errors.
        generated_at (str): Date de génération affichée.

    Returns:
        str: Document HTML autonome.
    """
    body = []
    for res in results:
        arts = res["articles"]
        n_new = sum(a.get("is_new", False) for a in arts)
        groups = group_by_category(arts)
        chips = "".join(f'<span class="chip">{escape(c)} · {len(i)}</span>' for c, i in groups)
        body.append(f'<section class="topic"><h2>{escape(res["topic"]["name"])}</h2>'
                    f'<p class="sub">{len(arts)} articles · {n_new} nouveaux</p>'
                    f'<div class="chips">{chips}</div>')
        for category, items in groups:
            body.append(f"<h3>{escape(category)}</h3>" + "".join(_article_html(a) for a in items))
        body += [f'<p class="err">⚠ Source indisponible : {escape(e)}</p>' for e in res.get("errors", [])]
        body.append("</section>")
    names = ", ".join(r["topic"]["name"] for r in results)
    return (f'<!doctype html><html lang="fr"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>Veille — {escape(names)}</title><style>{_CSS}</style></head><body><main>'
            f'<h1>Rapport de veille</h1><p class="sub">Généré le {escape(generated_at)}</p>'
            f'<input id="q" placeholder="Filtrer les articles…" aria-label="Filtrer">'
            f'{"".join(body)}</main><script>{_JS}</script></body></html>')
