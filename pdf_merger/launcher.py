"""
launcher.py
===========
Script d'entrée utilisé par PyInstaller pour produire PDFMerger.exe.

Description :
    PyInstaller a besoin d'un script (pas d'un paquet) : celui-ci appelle cli.main().

Cas d'usage :
    - pyinstaller ... pdf_merger/launcher.py

Entrée  : arguments de la ligne de commande
Sortie  : code de sortie du programme
"""

import sys

from pdf_merger.cli import main

if __name__ == "__main__":
    sys.exit(main())
