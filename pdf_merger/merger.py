"""
merger.py
=========
Moteur de fusion de PDF (sans interface).

Description :
    Rassemble plusieurs fichiers PDF, dans l'ordre donné, en un seul fichier.
    Chaque fichier peut être limité à une plage de pages et recevoir un signet
    (bookmark) portant son nom dans le PDF final.

Cas d'usage :
    - Fusionner des factures, des scans ou des chapitres
    - Extraire quelques pages de plusieurs documents dans un même PDF
    - Utilisé par l'interface graphique (gui.py) et la ligne de commande (cli.py)

Entrée  : liste de MergeItem (chemin + plage optionnelle), chemin de sortie
Sortie  : fichier PDF écrit sur disque, nombre de pages écrites
"""

import os
from dataclasses import dataclass

from pypdf import PdfReader, PdfWriter
from pypdf.errors import PdfReadError

from pdf_merger import config
from pdf_merger.page_range import parse_page_range


class MergeError(Exception):
    """Erreur lisible par l'utilisateur, levée pendant la fusion."""


@dataclass
class MergeItem:
    """
    Un fichier à fusionner.

    Args:
        path (str): chemin du PDF.
        pages (str | None): plage de pages à garder (ex. "1-3, 5"), None = toutes.
    """

    path: str
    pages: str | None = None


def open_pdf(path):
    """
    Ouvre un PDF en lecture, en déverrouillant les PDF chiffrés sans mot de passe.

    Args:
        path (str): chemin du PDF.

    Returns:
        PdfReader: lecteur pypdf prêt à l'emploi.

    Raises:
        MergeError: fichier absent, illisible ou protégé par mot de passe.
    """
    if not os.path.isfile(path):
        raise MergeError(config.ERR_NOT_FOUND.format(path=path))
    try:
        reader = PdfReader(path)
        if reader.is_encrypted and not reader.decrypt(""):
            raise MergeError(config.ERR_ENCRYPTED.format(path=path))
        len(reader.pages)  # force la lecture de l'arbre des pages
    except MergeError:
        raise
    except (PdfReadError, OSError, ValueError, KeyError):
        raise MergeError(config.ERR_NOT_PDF.format(path=path)) from None
    return reader


def count_pages(path):
    """
    Compte les pages d'un PDF.

    Args:
        path (str): chemin du PDF.

    Returns:
        int: nombre de pages.

    Raises:
        MergeError: si le fichier ne peut pas être lu.
    """
    return len(open_pdf(path).pages)


def merge_pdfs(items, output_path, add_bookmarks=True):
    """
    Fusionne les PDF dans l'ordre de la liste et écrit le résultat.

    Args:
        items (list[MergeItem | str]): fichiers à fusionner (un chemin seul = toutes les pages).
        output_path (str): chemin du PDF à créer (écrasé s'il existe).
        add_bookmarks (bool): ajoute un signet par fichier source.

    Returns:
        int: nombre total de pages écrites.

    Raises:
        MergeError: entrée vide, fichier illisible, plage invalide ou sortie impossible.
    """
    items = [MergeItem(i) if isinstance(i, str) else i for i in items]
    if not items:
        raise MergeError(config.ERR_NO_INPUT)

    out_abs = os.path.normcase(os.path.abspath(output_path))
    for item in items:
        if os.path.normcase(os.path.abspath(item.path)) == out_abs:
            raise MergeError(config.ERR_OUTPUT_IS_INPUT.format(path=output_path))

    writer = PdfWriter()
    for item in items:
        reader = open_pdf(item.path)
        try:
            indices = parse_page_range(item.pages, len(reader.pages))
        except ValueError as exc:
            raise MergeError(f"{os.path.basename(item.path)} : {exc}") from None
        if not indices:
            continue
        first_page = len(writer.pages)
        for index in indices:
            writer.add_page(reader.pages[index])
        if add_bookmarks:
            title = os.path.splitext(os.path.basename(item.path))[0]
            writer.add_outline_item(title, first_page)

    total = len(writer.pages)
    if total == 0:
        raise MergeError(config.ERR_EMPTY_RESULT)

    try:
        with open(output_path, "wb") as handle:
            writer.write(handle)
    except OSError as exc:
        raise MergeError(str(exc)) from None
    return total
