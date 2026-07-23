"""
filters
=======
Sous-module de filtrage des fun facts.

Chaque `filter_*.py` expose une unique fonction pure qui retourne la liste
complète inchangée lorsque son paramètre est `None` ou falsy.
"""

from geolocation_facts.filters.filter_distance import filter_by_distance
from geolocation_facts.filters.filter_keyword import filter_by_keyword
from geolocation_facts.filters.filter_engine import apply_filters

__all__ = ["filter_by_distance", "filter_by_keyword", "apply_filters"]
