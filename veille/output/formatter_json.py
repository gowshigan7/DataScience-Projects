"""
formatter_json.py
=================
Feature : Rapport de veille au format JSON.

Description :
    Sérialise les résultats (dates en ISO 8601) pour réutilisation dans
    d'autres outils (tableur, notebook, base de données).

Cas d'usage :
    - Analyse ultérieure dans pandas / un notebook

Entrée  : list[dict] résultats, str date de génération
Sortie  : str (JSON)
"""

import json


def format_json(results: list, generated_at: str) -> str:
    """
    Construit le rapport JSON.

    Args:
        results (list[dict]): Un dict par sujet : topic, articles, errors.
        generated_at (str): Date de génération.

    Returns:
        str: JSON indenté (UTF-8 lisible).
    """
    def _default(obj):
        return obj.isoformat() if hasattr(obj, "isoformat") else str(obj)

    return json.dumps({"generated_at": generated_at, "topics": results},
                      ensure_ascii=False, indent=2, default=_default)
