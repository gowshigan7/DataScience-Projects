"""
source
======
Sous-module des sources de fun facts géolocalisés.

Chaque source concrète étend `BaseFactSource` et retourne une liste de faits
au format standardisé défini dans `base_source.py`.
"""

from geolocation_facts.source.base_source import BaseFactSource
from geolocation_facts.source.wikipedia_geo import WikipediaGeoSource

__all__ = ["BaseFactSource", "WikipediaGeoSource"]
