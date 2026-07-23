"""
base_source.py
==============
Feature : Classe abstraite commune à toutes les sources de fun facts.

Description :
    Ce module définit l'interface (classe abstraite) que toutes les sources de
    fun facts doivent implémenter. Il garantit un contrat uniforme pour la
    récupération des données, peu importe la source (Wikipedia, etc.).

    Le modèle de données « fait » est également défini ici sous forme de
    dictionnaire standardisé pour assurer la cohérence entre les sources.

Cas d'usage :
    - Permet de passer facilement d'une source à l'autre sans modifier le code appelant
    - Facilite l'ajout de nouvelles sources de fun facts
    - Garantit que chaque source retourne des données dans le même format

Entrée  : Coordonnées GPS (lat, lng), rayon (mètres), paramètres optionnels
Sortie  : List[dict] représentant des fun facts avec les champs standardisés

Format Fait (dict) :
    {
        "id": str,           # Identifiant unique (issu de la source)
        "title": str,        # Titre du lieu / de l'article
        "fact": str,         # Texte du fun fact (extrait résumé)
        "latitude": float,   # Latitude GPS du lieu
        "longitude": float,  # Longitude GPS du lieu
        "distance_m": float, # Distance en mètres depuis le point de recherche, None si inconnue
        "category": str,     # Catégorie / thème du fait, None si inconnu
        "url": str,          # URL de la source (ex: article Wikipedia), None si inconnue
        "source": str,       # Nom de la source ("wikipedia")
    }
"""

from abc import ABC, abstractmethod


class BaseFactSource(ABC):
    """
    Classe abstraite définissant l'interface commune à toutes les sources de fun facts.

    Toutes les sources concrètes doivent hériter de cette classe et implémenter
    la méthode `fetch_facts`.
    """

    def __init__(self, api_key: str = "", dry_run: bool = False):
        """
        Initialise la source de base.

        Args:
            api_key (str): Clé API pour les services nécessitant une authentification.
            dry_run (bool): Si True, n'effectue aucun appel réseau réel.
        """
        self.api_key = api_key
        self.dry_run = dry_run

    @abstractmethod
    def fetch_facts(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
        **kwargs,
    ) -> list[dict]:
        """
        Récupère la liste des fun facts proches d'un point GPS.

        Args:
            latitude (float): Latitude du point de recherche.
            longitude (float): Longitude du point de recherche.
            radius_m (int): Rayon de recherche en mètres.
            limit (int): Nombre maximum de faits à retourner.
            **kwargs: Paramètres supplémentaires propres à chaque implémentation.

        Returns:
            list[dict]: Liste de faits au format standardisé (voir module docstring).
        """
        ...

    @staticmethod
    def make_fact(
        id: str,
        title: str,
        fact: str,
        latitude: float,
        longitude: float,
        distance_m: float | None = None,
        category: str | None = None,
        url: str | None = None,
        source: str = "unknown",
    ) -> dict:
        """
        Crée un dictionnaire fun fact au format standardisé.

        Args:
            id (str): Identifiant unique issu de la source.
            title (str): Titre du lieu / de l'article.
            fact (str): Texte du fun fact (extrait résumé).
            latitude (float): Latitude GPS du lieu.
            longitude (float): Longitude GPS du lieu.
            distance_m (float | None): Distance depuis le point de recherche (mètres).
            category (str | None): Catégorie / thème du fait.
            url (str | None): URL de la source.
            source (str): Nom de la source de données.

        Returns:
            dict: Fun fact au format standardisé.
        """
        return {
            "id": id,
            "title": title,
            "fact": fact,
            "latitude": latitude,
            "longitude": longitude,
            "distance_m": distance_m,
            "category": category,
            "url": url,
            "source": source,
        }

    def __repr__(self) -> str:
        """Représentation textuelle de la source."""
        return f"{self.__class__.__name__}(dry_run={self.dry_run})"
