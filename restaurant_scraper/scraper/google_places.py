"""
google_places.py
================
Feature : Scraping de restaurants via l'API Google Places.

Description :
    Ce module implémente le scraper utilisant l'API Google Places Nearby Search.
    Il récupère les restaurants à proximité d'un point GPS, avec leurs métadonnées
    (note, prix, type de cuisine, horaires d'ouverture, etc.).

    L'API Google Places requiert une clé API valide (GOOGLE_PLACES_API_KEY dans config.py
    ou variable d'environnement). En mode dry-run, aucun appel réseau n'est effectué.

Cas d'usage :
    - Recherche avec clé API disponible : données riches (notes, prix, photos, horaires)
    - Mode dry-run : retourne une liste vide, les données viennent de mock_data.py
    - Erreur réseau ou clé invalide : lève une exception explicite

Entrée  : float (lat), float (lng), int (radius_m), int (limit), str (api_key)
Sortie  : List[dict] — restaurants au format standardisé BaseScraper
"""

import urllib.request
import urllib.parse
import json

from restaurant_scraper.scraper.base_scraper import BaseScraper
from restaurant_scraper.geo.geolocation import calculate_distance
from restaurant_scraper.config import (
    GOOGLE_PLACES_API_KEY,
    GOOGLE_PLACES_NEARBY_URL,
    REQUEST_TIMEOUT_SECONDS,
    USER_AGENT,
)


class GooglePlacesScraper(BaseScraper):
    """
    Scraper utilisant l'API Google Places Nearby Search.

    Nécessite une clé API Google Places valide pour fonctionner en mode réel.
    Supporte le mode dry-run pour les tests sans consommation d'API.
    """

    SOURCE_NAME = "google_places"

    def __init__(self, api_key: str = "", dry_run: bool = False):
        """
        Initialise le scraper Google Places.

        Args:
            api_key (str): Clé API Google Places. Si vide, utilise GOOGLE_PLACES_API_KEY.
            dry_run (bool): Si True, n'effectue aucun appel réseau.
        """
        super().__init__(api_key=api_key or GOOGLE_PLACES_API_KEY, dry_run=dry_run)

    def fetch_restaurants(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
        **kwargs,
    ) -> list[dict]:
        """
        Récupère les restaurants via Google Places Nearby Search.

        Args:
            latitude (float): Latitude du point de recherche.
            longitude (float): Longitude du point de recherche.
            radius_m (int): Rayon de recherche en mètres (max 50 000 pour Google).
            limit (int): Nombre maximum de résultats souhaités.
            **kwargs: Paramètres supplémentaires (non utilisés ici).

        Returns:
            list[dict]: Liste de restaurants au format standardisé.

        Raises:
            ValueError: Si aucune clé API n'est configurée (mode non dry-run).
            RuntimeError: Si l'API retourne une erreur.
        """
        if self.dry_run:
            print("[DRY-RUN] GooglePlacesScraper : aucun appel API effectué.")
            return []

        if not self.api_key:
            raise ValueError(
                "Clé API Google Places manquante. "
                "Définissez GOOGLE_PLACES_API_KEY dans config.py ou en variable d'environnement. "
                "Utilisez --dry-run pour tester sans clé API."
            )

        restaurants = []
        next_page_token = None

        while len(restaurants) < limit:
            batch = self._fetch_page(latitude, longitude, radius_m, next_page_token)
            raw_results = batch.get("results", [])
            next_page_token = batch.get("next_page_token")

            for place in raw_results:
                if len(restaurants) >= limit:
                    break
                restaurant = self._parse_place(place, latitude, longitude)
                restaurants.append(restaurant)

            if not next_page_token:
                break

        return restaurants

    def _fetch_page(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        page_token: str | None = None,
    ) -> dict:
        """
        Effectue une requête paginée à l'API Google Places.

        Args:
            latitude (float): Latitude du point de recherche.
            longitude (float): Longitude du point de recherche.
            radius_m (int): Rayon de recherche en mètres.
            page_token (str | None): Token de pagination pour la page suivante.

        Returns:
            dict: Réponse brute de l'API Google Places.

        Raises:
            RuntimeError: Si le statut de la réponse indique une erreur.
        """
        params: dict = {
            "location": f"{latitude},{longitude}",
            "radius": radius_m,
            "type": "restaurant",
            "key": self.api_key,
        }
        if page_token:
            params["pagetoken"] = page_token

        url = f"{GOOGLE_PLACES_NEARBY_URL}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})

        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode())

        status = data.get("status", "UNKNOWN")
        if status not in ("OK", "ZERO_RESULTS"):
            raise RuntimeError(
                f"Erreur API Google Places : {status} — {data.get('error_message', '')}"
            )

        return data

    def _parse_place(
        self, place: dict, ref_lat: float, ref_lng: float
    ) -> dict:
        """
        Convertit un résultat brut Google Places en dictionnaire standardisé.

        Args:
            place (dict): Résultat brut de l'API Google Places.
            ref_lat (float): Latitude du point de référence (pour calcul distance).
            ref_lng (float): Longitude du point de référence.

        Returns:
            dict: Restaurant au format standardisé.
        """
        loc = place.get("geometry", {}).get("location", {})
        lat = loc.get("lat", 0.0)
        lng = loc.get("lng", 0.0)

        distance = calculate_distance(ref_lat, ref_lng, lat, lng)

        # Extraction du type de cuisine depuis les types Google
        cuisine = self._extract_cuisine(place.get("types", []))

        # Statut d'ouverture
        opening_hours = place.get("opening_hours", {})
        is_open_now = opening_hours.get("open_now") if opening_hours else None

        return self.make_restaurant(
            id=place.get("place_id", ""),
            name=place.get("name", "Inconnu"),
            address=place.get("vicinity", ""),
            latitude=lat,
            longitude=lng,
            rating=place.get("rating"),
            price_level=place.get("price_level"),
            cuisine=cuisine,
            is_open_now=is_open_now,
            distance_m=round(distance, 1),
            source=self.SOURCE_NAME,
        )

    @staticmethod
    def _extract_cuisine(types: list[str]) -> str | None:
        """
        Tente d'extraire un type de cuisine depuis les types Google Places.

        Args:
            types (list[str]): Liste des types Google (ex: ["restaurant", "food"]).

        Returns:
            str | None: Type de cuisine normalisé, ou None si non trouvé.
        """
        cuisine_mapping = {
            "italian_restaurant": "italian",
            "japanese_restaurant": "japanese",
            "french_restaurant": "french",
            "chinese_restaurant": "chinese",
            "indian_restaurant": "indian",
            "mexican_restaurant": "mexican",
            "thai_restaurant": "thai",
            "american_restaurant": "american",
            "mediterranean_restaurant": "mediterranean",
            "sushi_restaurant": "sushi",
            "pizza_restaurant": "pizza",
            "hamburger_restaurant": "burger",
            "seafood_restaurant": "seafood",
            "vegan_restaurant": "vegan",
        }
        for t in types:
            if t in cuisine_mapping:
                return cuisine_mapping[t]
        return None
