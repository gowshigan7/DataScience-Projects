"""
mailbox.py
==========
Feature : Source « boîte mail » — newsletters des expéditeurs choisis (IMAP).

Description :
    Se connecte en IMAP (SSL) avec un mot de passe d'application, lit en
    lecture seule (les e-mails ne sont PAS marqués comme lus) les messages
    reçus depuis N jours, ne garde que les expéditeurs de
    config.NEWSLETTER_SENDERS et produit un article par newsletter.

    Variables d'environnement : VEILLE_IMAP_HOST, VEILLE_IMAP_USER,
    VEILLE_IMAP_PASSWORD, VEILLE_IMAP_FOLDER, VEILLE_NEWSLETTER_SENDERS.

Cas d'usage :
    - Gmail : activer la validation en 2 étapes puis créer un « mot de passe d'application »

Entrée  : Identifiants IMAP, fenêtre en jours
Sortie  : list[dict] (articles standardisés, groupe Newsletters)
"""

import email
import imaplib
from datetime import datetime, timedelta, timezone
from email import policy

from veille.config import (
    GROUP_NEWSLETTERS,
    IMAP_DATE_FORMAT,
    IMAP_FOLDER,
    IMAP_HOST,
    IMAP_OK_STATUS,
    IMAP_PASSWORD,
    IMAP_USER,
    NEWSLETTER_SENDERS,
)
from veille.sources.base_source import BaseSource
from veille.sources.newsletter_parser import newsletter_to_fields, sender_matches



class MailboxSource(BaseSource):
    """Newsletters lues dans une boîte mail IMAP."""

    name = "mailbox"

    def __init__(self, host=IMAP_HOST, user=IMAP_USER, password=IMAP_PASSWORD,
                 folder=IMAP_FOLDER, senders=None, imap_factory=imaplib.IMAP4_SSL):
        """
        Args:
            host (str): Serveur IMAP.
            user (str): Identifiant.
            password (str): Mot de passe d'application.
            folder (str): Dossier à lire.
            senders (list[str] | None): Expéditeurs retenus (défaut NEWSLETTER_SENDERS).
            imap_factory (callable): Constructeur IMAP (remplaçable en test).

        Returns:
            None
        """
        self.host, self.user, self.password, self.folder = host, user, password, folder
        self.senders = NEWSLETTER_SENDERS if senders is None else senders
        self.imap_factory = imap_factory

    def is_configured(self) -> bool:
        """
        Indique si les identifiants IMAP sont renseignés.

        Returns:
            bool: True si utilisateur et mot de passe sont définis.
        """
        return bool(self.user and self.password)

    def fetch(self, topic, since_days: int, max_results: int = None) -> list:
        """
        Récupère les newsletters reçues depuis since_days jours.

        Args:
            topic (dict | None): Ignoré.
            since_days (int): Fenêtre en jours.
            max_results (int | None): Nombre max de newsletters (None = toutes).

        Returns:
            list[dict]: Articles standardisés (plus récentes d'abord).
        """
        since = (datetime.now(timezone.utc) - timedelta(days=since_days)).strftime(IMAP_DATE_FORMAT)
        conn = self.imap_factory(self.host)
        try:
            conn.login(self.user, self.password)
            conn.select(self.folder, readonly=True)
            status, data = conn.search(None, "SINCE", since)
            ids = data[0].split() if status == IMAP_OK_STATUS and data and data[0] else []
            articles = []
            for msg_id in reversed(ids):
                status, parts = conn.fetch(msg_id, "(BODY.PEEK[])")
                if status != IMAP_OK_STATUS or not parts or not isinstance(parts[0], tuple):
                    continue
                msg = email.message_from_bytes(parts[0][1], policy=policy.default)
                if not sender_matches(str(msg.get("From", "")), self.senders):
                    continue
                f = newsletter_to_fields(msg)
                articles.append(self.make_article(f["title"], f["url"], f["publisher"],
                                                  f["published"], f["summary"], "",
                                                  GROUP_NEWSLETTERS))
                if max_results and len(articles) >= max_results:
                    break
            return articles
        finally:
            try:
                conn.logout()
            except imaplib.IMAP4.error:
                pass
