"""
pdf_merger
==========
Petit logiciel Windows (Tkinter + pypdf) pour rassembler plusieurs PDF en un seul.

Description :
    Expose le moteur de fusion pour un usage en bibliothèque.

Cas d'usage :
    - from pdf_merger import merge_pdfs, MergeItem

Entrée  : Aucune
Sortie  : API publique du paquet
"""

from pdf_merger.merger import MergeError, MergeItem, count_pages, merge_pdfs
from pdf_merger.page_range import parse_page_range

__all__ = ["MergeError", "MergeItem", "count_pages", "merge_pdfs", "parse_page_range"]
