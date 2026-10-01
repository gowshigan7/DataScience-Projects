"""
newsletter_parser.py
====================
Feature : Transformation d'un e-mail de newsletter en article.

Description :
    Fonctions pures (sans réseau) :
    - extraction du texte et des liens (HTML ou texte brut)
    - choix du lien principal : « voir en ligne » si présent, sinon le premier
      lien utile (hors désinscription, préférences, mailto…)
    - filtre des expéditeurs retenus (config.NEWSLETTER_SENDERS)

Cas d'usage :
    - mailbox.py pour chaque e-mail récupéré en IMAP
    - tests unitaires sur des e-mails construits en mémoire

Entrée  : email.message.EmailMessage
Sortie  : dict (champs d'article) | None
"""

import re
from email.utils import parseaddr, parsedate_to_datetime
from html import unescape

from veille.config import (
    NEWSLETTER_SKIP_LINK_WORDS,
    NEWSLETTER_SUMMARY_CHARS,
    NEWSLETTER_WEB_VERSION_WORDS,
)
from veille.sources.base_source import clean_text, truncate

_LINK_RE = re.compile(r'<a\s[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.I | re.S)
_URL_RE = re.compile(r"https?://[^\s<>\")\]]+")
_HIDDEN_RE = re.compile(r"<(style|script|head)[^>]*>.*?</\1>", re.I | re.S)


def sender_matches(from_header: str, senders: list) -> bool:
    """
    Teste si l'expéditeur fait partie des newsletters retenues.

    Args:
        from_header (str): En-tête From.
        senders (list[str]): Sous-chaînes d'adresse/domaine ; si vide, tout est accepté.

    Returns:
        bool: True si l'expéditeur est retenu.
    """
    if not senders:
        return True
    low = from_header.lower()
    return any(s.lower() in low for s in senders)


def extract_body(msg) -> tuple:
    """
    Extrait le texte lisible et les liens d'un e-mail.

    Args:
        msg (email.message.EmailMessage): Message (policy=default).

    Returns:
        tuple[str, list[tuple[str, str]]]: (texte, [(url, texte du lien)])
    """
    html_part = msg.get_body(preferencelist=("html",))
    if html_part is not None:
        raw = _HIDDEN_RE.sub(" ", html_part.get_content())
        links = [(unescape(u), clean_text(t)) for u, t in _LINK_RE.findall(raw)]
        return clean_text(raw), links
    text_part = msg.get_body(preferencelist=("plain",))
    text = text_part.get_content() if text_part is not None else ""
    return " ".join(text.split()), [(u, "") for u in _URL_RE.findall(text)]


def pick_main_link(links: list) -> str:
    """
    Choisit le lien principal d'une newsletter.

    Args:
        links (list[tuple[str, str]]): (url, texte du lien).

    Returns:
        str: Lien « voir en ligne », sinon premier lien utile, sinon "".
    """
    useful = [(u, t) for u, t in links if u.startswith("http")
              and not any(w in f"{u} {t}".lower() for w in NEWSLETTER_SKIP_LINK_WORDS)]
    for u, t in useful:
        if any(w in t.lower() for w in NEWSLETTER_WEB_VERSION_WORDS):
            return u
    return useful[0][0] if useful else ""


def newsletter_to_fields(msg) -> dict:
    """
    Convertit un e-mail en champs d'article.

    Args:
        msg (email.message.EmailMessage): Message.

    Returns:
        dict: title, url, publisher, published (datetime | None), summary.
    """
    name, addr = parseaddr(str(msg.get("From", "")))
    text, links = extract_body(msg)
    try:
        published = parsedate_to_datetime(str(msg.get("Date", "")))
    except (TypeError, ValueError):
        published = None
    return {
        "title": str(msg.get("Subject", "")),
        "url": pick_main_link(links) or f"mailto:{addr}",
        "publisher": name or addr,
        "published": published,
        "summary": truncate(text, NEWSLETTER_SUMMARY_CHARS),
    }
