"""
rss_parser.py
=============
Feature : Lecture d'un flux RSS 2.0 en liste de dicts bruts.

Description :
    Parse le XML avec la bibliothèque standard (xml.etree) et retourne pour
    chaque <item> : title, link, pubDate, description, source (éditeur).

Cas d'usage :
    - Utilisé par google_news.py et bing_news.py

Entrée  : bytes (XML RSS)
Sortie  : list[dict] (items bruts)
"""

import xml.etree.ElementTree as ET


def parse_rss(xml_bytes: bytes) -> list:
    """
    Parse un flux RSS.

    Args:
        xml_bytes (bytes): Contenu XML.

    Returns:
        list[dict]: Items avec les clés title, link, pubDate, description, source.
    """
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []
    items = []
    for item in root.iter("item"):
        get = lambda tag: (item.findtext(tag) or "").strip()  # noqa: E731
        # Google : <source> ; Bing : <News:Source> (espace de noms variable)
        source = get("source") or next(
            ((c.text or "").strip() for c in item if c.tag.lower().endswith("}source")), "")
        items.append({
            "title": get("title"),
            "link": get("link"),
            "pubDate": get("pubDate"),
            "description": get("description"),
            "source": source,
        })
    return items
