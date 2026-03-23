"""
base_scraper.py
===============
Feature : Classe abstraite commune à tous les scrapers de restaurants.

Description :
    Ce module définit l'interface (classe abstraite) que tous les scrapers
    doivent implémenter. Il garantit un contrat uniforme pour la récupération
    des données, peu importe la source (Google Places, Overpass OSM, etc.).

    Le modèle de données restaurant est également défini ici sous forme de
    dictionnaire typé pour assurer la cohérence entre les sources.

Cas d'usage :
    - Permet de passer facilement d'un scraper à l'autre sans modifier le code appelant
    - Facilite l'ajout de nouvelles sources de données
    - Garantit que chaque scraper retourne des données dans le même format

Entrée  : Coordonnées GPS (lat, lng), rayon (mètres), paramètres optionnels
Sortie  : List[dict] représentant des restaurants avec les champs standardisés

Format Restaurant (dict) :
    {
        "id": str,           # Identifiant unique (issu de la source)
        "name": str,         # Nom du restaurant
        "address": str,      # Adresse complète
        "latitude": float,   # Latitude GPS
        "longitude": float,  # Longitude GPS
        "rating": float,     # Note moyenne (0.0 - 5.0), None si inconnue
        "price_level": int,  # Niveau de prix (1-4), None si inconnu
        "cuisine": str,      # Type de cuisine principal, None si inconnu
        "is_open_now": bool, # True si ouvert en ce moment, None si inconnu
        "distance_m": float, # Distance en mètres depuis le point de recherche
        "phone": str,        # Numéro de téléphone, None si inconnu
        "website": str,      # URL du site web, None si inconnu
        "source": str,       # Source des données ("google_places" ou "overpass_osm")
    }
"""

from abc import ABC, abstractmethod


class BaseScraper(ABC):
    """
    Classe abstraite définissant l'interface commune à tous les scrapers.

    Tous les scrapers concrets doivent hériter de cette classe et implémenter
    la méthode `fetch_restaurants`.
    """

    def __init__(self, api_key: str = "", dry_run: bool = False):
        """
        Initialise le scraper de base.

        Args:
            api_key (str): Clé API pour les services nécessitant une authentification.
            dry_run (bool): Si True, n'effectue aucun appel réseau réel.
        """
        self.api_key = api_key
        self.dry_run = dry_run

    @abstractmethod
    def fetch_restaurants(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
        **kwargs,
    ) -> list[dict]:
        """
        Récupère la liste des restaurants proches d'un point GPS.

        Args:
            latitude (float): Latitude du point de recherche.
            longitude (float): Longitude du point de recherche.
            radius_m (int): Rayon de recherche en mètres.
            limit (int): Nombre maximum de résultats à retourner.
            **kwargs: Paramètres supplémentaires propres à chaque implémentation.

        Returns:
            list[dict]: Liste de restaurants au format standardisé (voir module docstring).
        """
        ...

    @staticmethod
    def make_restaurant(
        id: str,
        name: str,
        address: str,
        latitude: float,
        longitude: float,
        rating: float | None = None,
        price_level: int | None = None,
        cuisine: str | None = None,
        is_open_now: bool | None = None,
        distance_m: float | None = None,
        phone: str | None = None,
        website: str | None = None,
        source: str = "unknown",
    ) -> dict:
        """
        Crée un dictionnaire restaurant au format standardisé.

        Args:
            id (str): Identifiant unique issu de la source.
            name (str): Nom du restaurant.
            address (str): Adresse complète.
            latitude (float): Latitude GPS.
            longitude (float): Longitude GPS.
            rating (float | None): Note moyenne (0.0 - 5.0).
            price_level (int | None): Niveau de prix (1-4).
            cuisine (str | None): Type de cuisine principal.
            is_open_now (bool | None): True si ouvert en ce moment.
            distance_m (float | None): Distance depuis le point de recherche (mètres).
            phone (str | None): Numéro de téléphone.
            website (str | None): URL du site web.
            source (str): Nom de la source de données.

        Returns:
            dict: Restaurant au format standardisé.
        """
        return {
            "id": id,
            "name": name,
            "address": address,
            "latitude": latitude,
            "longitude": longitude,
            "rating": rating,
            "price_level": price_level,
            "cuisine": cuisine,
            "is_open_now": is_open_now,
            "distance_m": distance_m,
            "phone": phone,
            "website": website,
            "source": source,
        }

    def __repr__(self) -> str:
        """Représentation textuelle du scraper."""
        return f"{self.__class__.__name__}(dry_run={self.dry_run})"
