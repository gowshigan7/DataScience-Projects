"""
topics.py
=========
Feature : Gestion des sujets de veille (ajout, liste, suppression).

Description :
    Un sujet est un dict :
        {"name": str, "aliases": [str], "exclude": [str], "languages": [str]}
    - name      : nom recherché (ex. "Shift Technology")
    - aliases   : autres formulations utiles (ex. "Shift Tech", "Jeremy Jawish")
    - exclude   : termes qui disqualifient un article (homonymes, ex. "Shift Technologies")
    - languages : langues interrogées (ex. ["fr", "en"])
    Les sujets sont stockés en JSON dans config.TOPICS_FILE.

Cas d'usage :
    - main.py add / list / remove
    - Lecture des sujets avant chaque collecte

Entrée  : Chemin du fichier JSON, paramètres du sujet
Sortie  : list[dict] (sujets)
"""

import json
import os

from veille.config import DEFAULT_LANGUAGES, TOPICS_FILE


def make_topic(name: str, aliases=None, exclude=None, languages=None) -> dict:
    """
    Construit un sujet au format standard.

    Args:
        name (str): Nom du sujet.
        aliases (list[str] | None): Formulations alternatives.
        exclude (list[str] | None): Termes d'exclusion.
        languages (list[str] | None): Langues ; DEFAULT_LANGUAGES si None.

    Returns:
        dict: Sujet normalisé.
    """
    return {
        "name": name.strip(),
        "aliases": [a.strip() for a in (aliases or []) if a.strip()],
        "exclude": [e.strip() for e in (exclude or []) if e.strip()],
        "languages": list(languages or DEFAULT_LANGUAGES),
    }


def load_topics(path: str = TOPICS_FILE) -> list:
    """
    Charge les sujets depuis le fichier JSON.

    Args:
        path (str): Chemin du fichier.

    Returns:
        list[dict]: Sujets (liste vide si le fichier n'existe pas).
    """
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_topics(topics: list, path: str = TOPICS_FILE) -> None:
    """
    Enregistre les sujets dans le fichier JSON.

    Args:
        topics (list[dict]): Sujets à enregistrer.
        path (str): Chemin du fichier.

    Returns:
        None
    """
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(topics, f, ensure_ascii=False, indent=2)


def find_topic(topics: list, name: str):
    """
    Cherche un sujet par nom (insensible à la casse).

    Args:
        topics (list[dict]): Sujets existants.
        name (str): Nom recherché.

    Returns:
        dict | None: Le sujet trouvé, ou None.
    """
    key = name.strip().lower()
    return next((t for t in topics if t["name"].lower() == key), None)


def upsert_topic(topics: list, topic: dict) -> list:
    """
    Ajoute un sujet, ou remplace celui qui porte le même nom.

    Args:
        topics (list[dict]): Sujets existants.
        topic (dict): Sujet à ajouter.

    Returns:
        list[dict]: Nouvelle liste de sujets.
    """
    others = [t for t in topics if t["name"].lower() != topic["name"].lower()]
    return others + [topic]


def remove_topic(topics: list, name: str) -> list:
    """
    Retire un sujet par nom.

    Args:
        topics (list[dict]): Sujets existants.
        name (str): Nom du sujet à retirer.

    Returns:
        list[dict]: Nouvelle liste de sujets.
    """
    return [t for t in topics if t["name"].lower() != name.strip().lower()]
