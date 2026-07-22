"""
geo_fun_facts
=============
Module réutilisable : fun facts géolocalisés autour d'une adresse ou de coordonnées GPS.

Usage :
    from geo_fun_facts import get_fun_facts

    facts = get_fun_facts("Paris, France", radius_km=50, limit=5, source="mock")
"""

from geo_fun_facts.engine import get_fun_facts
from geo_fun_facts.providers.base_provider import FactProvider
from geo_fun_facts.providers.mock_provider import MockFactProvider
from geo_fun_facts.providers.wikipedia_provider import WikipediaFactProvider

__all__ = [
    "get_fun_facts",
    "FactProvider",
    "MockFactProvider",
    "WikipediaFactProvider",
]
