"""
fallback.py
===========
Feature : Source « avec secours » — essaie une source, puis une autre si elle échoue.

Description :
    Enveloppe deux sources : la principale (RSS / API, rapide) et le secours
    (souvent le bot navigateur). Le secours est utilisé si la principale lève
    une erreur OU ne renvoie rien. L'attribut last_used indique laquelle a servi
    (utile pour la commande « check »).

Cas d'usage :
    - Flux RSS OpenAI cassé → lecture de la page openai.com/news
    - Reddit refuse JSON et RSS → lecture de old.reddit.com dans le navigateur

Entrée  : BaseSource principale, BaseSource de secours
Sortie  : list[dict] (articles standardisés)
"""

from veille.sources.base_source import BaseSource


class FallbackSource(BaseSource):
    """Source principale avec repli automatique."""

    def __init__(self, primary: BaseSource, secondary: BaseSource):
        """
        Args:
            primary (BaseSource): Source essayée en premier.
            secondary (BaseSource): Source de secours.

        Returns:
            None
        """
        self.primary, self.secondary = primary, secondary
        self.name = primary.name
        self.last_used = None
        self.primary_error = None

    def fetch(self, topic, since_days: int, max_results: int = None) -> list:
        """
        Essaie la source principale puis, si besoin, le secours.

        Args:
            topic (dict | None): Transmis aux sources.
            since_days (int): Fenêtre en jours.
            max_results (int | None): Nombre max d'articles.

        Returns:
            list[dict]: Articles de la première source qui en renvoie.

        Raises:
            Exception: L'erreur du secours si les deux échouent.
        """
        self.primary_error = None
        try:
            articles = self.primary.fetch(topic, since_days, max_results)
            if articles:
                self.last_used = self.primary.name
                return articles
        except Exception as exc:  # on tente le secours
            self.primary_error = exc
        usable = getattr(self.secondary, "is_configured", lambda: True)()
        if not usable:
            if self.primary_error:
                raise self.primary_error
            self.last_used = self.primary.name
            return []
        self.last_used = self.secondary.name
        return self.secondary.fetch(topic, since_days, max_results)
