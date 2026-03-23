"""
filters/__init__.py
===================
Package de filtrage pour restaurant_scraper.

Expose le moteur de filtrage principal et tous les filtres individuels.
"""

from .filter_engine import FilterEngine
from .filter_rating import filter_by_rating
from .filter_cuisine import filter_by_cuisine
from .filter_price import filter_by_price
from .filter_open_now import filter_by_open_now
from .filter_distance import filter_by_distance

__all__ = [
    "FilterEngine",
    "filter_by_rating",
    "filter_by_cuisine",
    "filter_by_price",
    "filter_by_open_now",
    "filter_by_distance",
]
