"""
base_provider.py
=================
Feature : Classe abstraite commune à tous les fournisseurs de fun facts.

Description :
    Ce module définit l'interface (classe abstraite) que tous les fournisseurs
    de fun facts doivent implémenter. Il garantit un contrat uniforme pour la
    récupération des données, peu importe la source (mock, Wikipedia, etc.).

    Le modèle de données "fun fact" est également défini ici sous forme de
    dictionnaire typé pour assurer la cohérence entre les sources.

Cas d'usage :
    - Permet de passer facilement d'une source à l'autre sans modifier le code appelant
    - Facilite l'ajout de nouvelles sources (scraping, autres APIs, etc.)
    - Garantit que chaque fournisseur retourne des données dans le même format

Entrée  : Coordonnées GPS (lat, lng), rayon (km), nombre maximum de résultats
Sortie  : List[dict] représentant des fun facts avec les champs standardisés

Format Fun Fact (dict) :
    {
        "id": str,            # Identifiant unique (issu de la source)
        "title": str,         # Titre / nom du lieu ou du sujet
        "fact": str,          # Le fun fact lui-même
        "category": str,      # Catégorie (voir config.FACT_CATEGORIES), None si inconnue
        "latitude": float,    # Latitude GPS du fait
        "longitude": float,   # Longitude GPS du fait
        "distance_km": float, # Distance en km depuis le point de recherche
        "url": str,           # Lien pour en savoir plus, None si inconnu
        "source": str,        # Source des données ("mock" ou "wikipedia")
    }
"""

from abc import ABC, abstractmethod


class FactProvider(ABC):
    """
    Classe abstraite définissant l'interface commune à tous les fournisseurs de fun facts.

    Tous les fournisseurs concrets doivent hériter de cette classe et implémenter
    la méthode `get_facts`.
    """

    @abstractmethod
    def get_facts(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int,
    ) -> list[dict]:
        """
        Récupère la liste des fun facts proches d'un point GPS.

        Args:
            latitude (float): Latitude du point de recherche.
            longitude (float): Longitude du point de recherche.
            radius_km (float): Rayon de recherche en kilomètres.
            limit (int): Nombre maximum de résultats à retourner.

        Returns:
            list[dict]: Liste de fun facts au format standardisé (voir module docstring),
                        triée par distance croissante.
        """
        ...

    @staticmethod
    def make_fact(
        id: str,
        title: str,
        fact: str,
        latitude: float,
        longitude: float,
        distance_km: float,
        category: str | None = None,
        url: str | None = None,
        source: str = "unknown",
    ) -> dict:
        """
        Crée un dictionnaire fun fact au format standardisé.

        Args:
            id (str): Identifiant unique issu de la source.
            title (str): Titre / nom du lieu ou du sujet.
            fact (str): Le fun fact lui-même.
            latitude (float): Latitude GPS du fait.
            longitude (float): Longitude GPS du fait.
            distance_km (float): Distance depuis le point de recherche (kilomètres).
            category (str | None): Catégorie du fun fact.
            url (str | None): Lien pour en savoir plus.
            source (str): Nom de la source de données.

        Returns:
            dict: Fun fact au format standardisé.
        """
        return {
            "id": id,
            "title": title,
            "fact": fact,
            "category": category,
            "latitude": latitude,
            "longitude": longitude,
            "distance_km": distance_km,
            "url": url,
            "source": source,
        }
