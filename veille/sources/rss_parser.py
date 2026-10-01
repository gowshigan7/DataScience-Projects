"""
rss_parser.py
=============
Feature : Lecture d'un flux RSS 2.0 ou Atom en liste de dicts bruts.

Description :
    Parse le XML avec la bibliothèque standard (xml.etree) et retourne pour
    chaque <item> (RSS) ou <entry> (Atom) : title, link, pubDate, description,
    source (éditeur / auteur).

Cas d'usage :
    - google_news.py, bing_news.py (RSS)
    - feed_rss.py : blogs des labs (RSS), releases GitHub et Reddit (Atom)

Entrée  : bytes (XML RSS ou Atom)
Sortie  : list[dict] (items bruts)
"""

import xml.etree.ElementTree as ET

from veille.config import ATOM_NS


def parse_rss(xml_bytes: bytes) -> list:
    """
    Parse un flux RSS 2.0 ou Atom.

    Args:
        xml_bytes (bytes): Contenu XML.

    Returns:
        list[dict]: Items avec les clés title, link, pubDate, description, source.
    """
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError:
        return []
    if root.tag == f"{{{ATOM_NS}}}feed":
        return [_parse_atom_entry(e) for e in root.iter(f"{{{ATOM_NS}}}entry")]
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


def _parse_atom_entry(entry) -> dict:
    """
    Convertit une <entry> Atom au même format qu'un item RSS.

    Args:
        entry (xml.etree.ElementTree.Element): Élément <entry>.

    Returns:
        dict: Clés title, link, pubDate, description, source.
    """
    get = lambda tag: (entry.findtext(f"{{{ATOM_NS}}}{tag}") or "").strip()  # noqa: E731
    links = entry.findall(f"{{{ATOM_NS}}}link")
    alternate = [l for l in links if l.get("rel", "alternate") == "alternate"] or links
    return {
        "title": get("title"),
        "link": alternate[0].get("href", "") if alternate else "",
        "pubDate": get("published") or get("updated"),
        "description": get("summary") or get("content"),
        "source": (entry.findtext(f"{{{ATOM_NS}}}author/{{{ATOM_NS}}}name") or "").strip(),
    }
