"""
cli.py
======
Point d'entrée : interface graphique par défaut, ligne de commande avec -o.

Description :
    Sans option -o, ouvre la fenêtre (avec les fichiers passés en argument
    déjà chargés : pratique pour glisser des PDF sur l'icône de l'exe).
    Avec -o, fusionne directement sans fenêtre.

Cas d'usage :
    - python -m pdf_merger                          → fenêtre
    - python -m pdf_merger a.pdf b.pdf -o out.pdf   → fusion directe
    - python -m pdf_merger a.pdf:1-3 b.pdf -o out.pdf  → pages 1 à 3 de a.pdf

Entrée  : arguments de la ligne de commande
Sortie  : PDF fusionné, ou fenêtre graphique
"""

import argparse
import os
import sys

from pdf_merger import config
from pdf_merger.merger import MergeError, MergeItem, merge_pdfs


def build_parser():
    """
    Construit l'analyseur d'arguments.

    Returns:
        argparse.ArgumentParser: analyseur configuré.
    """
    parser = argparse.ArgumentParser(prog="pdf_merger", description="Rassemble plusieurs PDF en un seul.")
    parser.add_argument("files", nargs="*", help="PDF à fusionner, éventuellement suivis de :PAGES (ex. doc.pdf:1-3,5)")
    parser.add_argument("-o", "--output", help="fichier de sortie (sans cette option, la fenêtre s'ouvre)")
    parser.add_argument("--no-bookmarks", action="store_true", help="ne pas ajouter de signet par fichier")
    parser.add_argument("--version", action="version", version=f"{config.APP_NAME} {config.APP_VERSION}")
    return parser


def parse_item(arg):
    """
    Sépare « chemin:plage » en MergeItem, en respectant les lettres de lecteur (C:\\).

    Args:
        arg (str): argument tel que saisi, ex. "C:\\docs\\a.pdf:1-3".

    Returns:
        MergeItem: chemin + plage (None si absente).
    """
    if os.path.exists(arg):
        return MergeItem(arg)
    path, sep, pages = arg.rpartition(":")
    if sep and path.lower().endswith(config.PDF_EXTENSION):
        return MergeItem(path, pages or None)
    return MergeItem(arg)


def main(argv=None):
    """
    Exécute le programme.

    Args:
        argv (list[str] | None): arguments (None = sys.argv[1:]).

    Returns:
        int: code de sortie (0 = succès).
    """
    args = build_parser().parse_args(argv)
    if not args.output:
        from pdf_merger.gui import run_gui  # import tardif : la CLI marche sans Tkinter

        run_gui(args.files)
        return 0
    try:
        pages = merge_pdfs([parse_item(a) for a in args.files], args.output, not args.no_bookmarks)
    except MergeError as exc:
        print(f"{config.MSG_ERROR_TITLE} : {exc}", file=sys.stderr)
        return 1
    print(config.MSG_DONE.format(pages=pages, path=args.output))
    return 0
