"""
report_writer.py
================
Feature : Choix du formateur et écriture du rapport sur disque.

Description :
    Associe chaque format (config.OUTPUT_FORMATS) à son formateur, puis écrit
    le fichier dans le dossier demandé (sauf "terminal", simplement retourné).

Cas d'usage :
    - main.py run --output html

Entrée  : résultats, format, dossier de sortie
Sortie  : (str contenu, str | None chemin du fichier écrit)
"""

import os

from veille.config import REPORT_FILE_EXTENSIONS
from veille.output.formatter_html import format_html
from veille.output.formatter_json import format_json
from veille.output.formatter_markdown import format_markdown
from veille.output.formatter_terminal import format_terminal


def render(results: list, fmt: str, generated_at: str) -> str:
    """
    Produit le rapport dans le format demandé.

    Args:
        results (list[dict]): Résultats par sujet.
        fmt (str): "terminal", "markdown", "html" ou "json".
        generated_at (str): Date de génération.

    Returns:
        str: Contenu du rapport.
    """
    if fmt == "terminal":
        return format_terminal(results)
    formatter = {"markdown": format_markdown, "html": format_html, "json": format_json}[fmt]
    return formatter(results, generated_at)


def write_report(content: str, fmt: str, out_dir: str, stem: str) -> str:
    """
    Écrit le rapport dans un fichier.

    Args:
        content (str): Contenu du rapport.
        fmt (str): Format (détermine l'extension).
        out_dir (str): Dossier de sortie (créé si besoin).
        stem (str): Nom de fichier sans extension.

    Returns:
        str: Chemin du fichier écrit.
    """
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{stem}.{REPORT_FILE_EXTENSIONS[fmt]}")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path
