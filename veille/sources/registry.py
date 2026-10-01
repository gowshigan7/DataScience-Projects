"""
registry.py
===========
Feature : Registre des sources disponibles (nom → classe).

Description :
    Associe chaque nom de source (config.SOURCE_NAMES) à sa classe.
    Ajouter une source = l'importer ici et ajouter son nom dans config.py.

Cas d'usage :
    - main.py instancie les sources demandées via get_sources()

Entrée  : list[str] (noms de sources)
Sortie  : list[BaseSource]
"""

from veille.sources.bing_news import BingNewsSource
from veille.sources.google_news import GoogleNewsSource
from veille.sources.hacker_news import HackerNewsSource

SOURCES = {cls.name: cls for cls in (GoogleNewsSource, BingNewsSource, HackerNewsSource)}


def get_sources(names: list) -> list:
    """
    Instancie les sources demandées.

    Args:
        names (list[str]): Noms de sources (inconnus ignorés).

    Returns:
        list[BaseSource]: Instances de sources.
    """
    return [SOURCES[n]() for n in names if n in SOURCES]
