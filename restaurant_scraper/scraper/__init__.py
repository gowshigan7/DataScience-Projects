"""
scraper/__init__.py
===================
Package de scraping pour restaurant_scraper.

Expose les classes principales des scrapers disponibles.
"""

from .base_scraper import BaseScraper
from .google_places import GooglePlacesScraper
from .overpass_osm import OverpassOSMScraper

__all__ = ["BaseScraper", "GooglePlacesScraper", "OverpassOSMScraper"]
