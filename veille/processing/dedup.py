"""
dedup.py
========
Feature : Dédoublonnage des articles (même URL ou même titre normalisé).

Description :
    Un même communiqué est souvent repris par plusieurs médias / sources.
    On garde la première occurrence et on liste les autres médias dans
    "also_in" pour montrer l'ampleur de la reprise.

Cas d'usage :
    - Fusionner Google News + Bing News + Hacker News

Entrée  : list[dict] (articles)
Sortie  : list[dict] (articles uniques, avec "also_in")
"""

import re
import unicodedata

_NON_ALNUM = re.compile(r"[^a-z0-9 ]+")


def normalize_title(title: str) -> str:
    """
    Normalise un titre pour comparaison (minuscules, sans accents ni ponctuation).

    Args:
        title (str): Titre.

    Returns:
        str: Titre normalisé.
    """
    t = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower()
    return " ".join(_NON_ALNUM.sub(" ", t).split())


def deduplicate(articles: list) -> list:
    """
    Supprime les doublons (URL identique ou titre normalisé identique).

    Args:
        articles (list[dict]): Articles.

    Returns:
        list[dict]: Articles uniques ; "also_in" liste les médias des doublons,
        et le résumé / la date manquants sont complétés depuis les doublons.
    """
    unique, by_key = [], {}
    for art in articles:
        keys = (art["url"], normalize_title(art["title"]))
        existing = next((by_key[k] for k in keys if k in by_key), None)
        if existing is None:
            kept = {**art, "also_in": []}
            unique.append(kept)
            for k in keys:
                by_key[k] = kept
            continue
        if not existing.get("summary") and art.get("summary"):
            existing["summary"] = art["summary"]
        if not existing.get("published") and art.get("published"):
            existing["published"] = art["published"]
        pub = art.get("publisher")
        if pub and pub != existing.get("publisher") and pub not in existing["also_in"]:
            existing["also_in"].append(pub)
    return unique
