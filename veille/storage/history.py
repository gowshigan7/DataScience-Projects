"""
history.py
==========
Feature : Historique des articles déjà vus (SQLite) pour signaler les nouveautés.

Description :
    Table seen(topic, url, title, first_seen). À chaque veille, les articles
    absents de l'historique reçoivent "is_new": True, puis sont enregistrés.

Cas d'usage :
    - Afficher 🆕 sur les articles apparus depuis la dernière veille
    - Lancer la veille chaque jour (cron) sans relire les mêmes infos

Entrée  : Chemin de la base, sujet, articles
Sortie  : list[dict] (articles avec "is_new")
"""

import os
import sqlite3
from datetime import datetime, timezone

_SCHEMA = """CREATE TABLE IF NOT EXISTS seen (
    topic TEXT NOT NULL, url TEXT NOT NULL, title TEXT, first_seen TEXT,
    PRIMARY KEY (topic, url))"""


def connect(path: str) -> sqlite3.Connection:
    """
    Ouvre (et initialise si besoin) la base d'historique.

    Args:
        path (str): Chemin du fichier SQLite (":memory:" accepté).

    Returns:
        sqlite3.Connection: Connexion ouverte.
    """
    if path != ":memory:":
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute(_SCHEMA)
    return conn


def mark_new(conn: sqlite3.Connection, topic_name: str, articles: list) -> list:
    """
    Marque les articles jamais vus et les enregistre dans l'historique.

    Args:
        conn (sqlite3.Connection): Connexion à l'historique.
        topic_name (str): Nom du sujet.
        articles (list[dict]): Articles traités.

    Returns:
        list[dict]: Copies des articles avec la clé "is_new".
    """
    seen = {row[0] for row in conn.execute("SELECT url FROM seen WHERE topic = ?", (topic_name,))}
    now = datetime.now(timezone.utc).isoformat()
    result = [{**a, "is_new": a["url"] not in seen} for a in articles]
    conn.executemany(
        "INSERT OR IGNORE INTO seen (topic, url, title, first_seen) VALUES (?, ?, ?, ?)",
        [(topic_name, a["url"], a["title"], now) for a in result if a["is_new"]])
    conn.commit()
    return result
