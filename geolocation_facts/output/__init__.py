"""
output
======
Sous-module de formatage et d'export des fun facts : affichage terminal et
export JSON.
"""

from geolocation_facts.output.formatter_terminal import format_terminal
from geolocation_facts.output.formatter_json import save_json

__all__ = ["format_terminal", "save_json"]
