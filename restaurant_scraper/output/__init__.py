"""
output/__init__.py
==================
Package de formatage et d'export pour restaurant_scraper.

Expose les formateurs disponibles : terminal, JSON, CSV.
"""

from .formatter_terminal import format_terminal
from .formatter_json import format_json, save_json
from .formatter_csv import format_csv, save_csv

__all__ = [
    "format_terminal",
    "format_json",
    "save_json",
    "format_csv",
    "save_csv",
]
