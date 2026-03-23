"""
geo/__init__.py
===============
Package de géolocalisation pour restaurant_scraper.

Expose les fonctions principales du module geolocation.
"""

from .geolocation import resolve_location, parse_coordinates, calculate_distance

__all__ = ["resolve_location", "parse_coordinates", "calculate_distance"]
