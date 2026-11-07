"""
__main__.py
===========
Permet de lancer le paquet avec « python -m pdf_merger ».

Description :
    Délègue à cli.main().

Cas d'usage :
    - python -m pdf_merger

Entrée  : arguments de la ligne de commande
Sortie  : code de sortie du programme
"""

import sys

from pdf_merger.cli import main

sys.exit(main())
