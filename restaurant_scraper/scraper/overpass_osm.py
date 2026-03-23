"""
overpass_osm.py
===============
Feature : Scraping de restaurants via l'API Overpass (OpenStreetMap).

Description :
    Ce module implémente le scraper utilisant l'API Overpass d'OpenStreetMap.
    Il s'agit du backend GRATUIT et sans clé API, utilisé comme fallback lorsque
    Google Places n'est pas disponible.

    L'API Overpass permet de requêter la base OSM avec un langage de requête dédié (QL).
    Les données OSM sont moins complètes (pas de notes, prix approximatifs) mais
    couvrent la majorité des établissements dans le monde.

Cas d'usage :
    - Recherche sans clé API Google : fallback automatique vers OSM
    - Mode dry-run : retourne une liste vide, données viennent de mock_data.py
    - Utile pour des recherches rapides dans des zones bien couvertes par OSM

Entrée  : float (lat), float (lng), int (radius_m), int (limit)
Sortie  : List[dict] — restaurants au format standardisé BaseScraper

Note :
    Les données OSM ne fournissent pas de notes ni de niveaux de prix standardisés.
    Ces champs seront None dans les résultats OSM.
"""

import urllib.request
import urllib.parse
import json

from restaurant_scraper.scraper.base_scraper import BaseScraper
from restaurant_scraper.geo.geolocation import calculate_distance
from restaurant_scraper.config import (
    OVERPASS_API_URL,
    REQUEST_TIMEOUT_SECONDS,
    USER_AGENT,
)


class OverpassOSMScraper(BaseScraper):
    """
    Scraper utilisant l'API Overpass d'OpenStreetMap.

    Aucune clé API requise. Les données sont moins riches que Google Places
    mais l'outil est entièrement gratuit et open source.
    """

    SOURCE_NAME = "overpass_osm"

    def fetch_restaurants(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
        **kwargs,
    ) -> list[dict]:
        """
        Récupère les restaurants via l'API Overpass (OSM).

        Args:
            latitude (float): Latitude du point de recherche.
            longitude (float): Longitude du point de recherche.
            radius_m (int): Rayon de recherche en mètres.
            limit (int): Nombre maximum de résultats à retourner.
            **kwargs: Paramètres supplémentaires (non utilisés ici).

        Returns:
            list[dict]: Liste de restaurants au format standardisé.

        Raises:
            RuntimeError: Si la requête Overpass échoue.
        """
        if self.dry_run:
            print("[DRY-RUN] OverpassOSMScraper : aucun appel API effectué.")
            return []

        query = self._build_query(latitude, longitude, radius_m, limit)
        raw_elements = self._execute_query(query)

        restaurants = []
        for element in raw_elements:
            if len(restaurants) >= limit:
                break
            restaurant = self._parse_element(element, latitude, longitude)
            if restaurant:
                restaurants.append(restaurant)

        return restaurants

    def _build_query(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
    ) -> str:
        """
        Construit la requête Overpass QL pour trouver les restaurants.

        Args:
            latitude (float): Latitude du centre de recherche.
            longitude (float): Longitude du centre de recherche.
            radius_m (int): Rayon de recherche en mètres.
            limit (int): Nombre maximum de résultats.

        Returns:
            str: Requête Overpass QL prête à l'envoi.
        """
        return f"""
[out:json][timeout:25];
(
  node["amenity"="restaurant"](around:{radius_m},{latitude},{longitude});
  way["amenity"="restaurant"](around:{radius_m},{latitude},{longitude});
);
out center {limit};
""".strip()

    def _execute_query(self, query: str) -> list[dict]:
        """
        Exécute une requête Overpass QL et retourne les éléments bruts.

        Args:
            query (str): Requête Overpass QL.

        Returns:
            list[dict]: Liste des éléments OSM bruts.

        Raises:
            RuntimeError: Si la requête échoue ou retourne une erreur HTTP.
        """
        data = urllib.parse.urlencode({"data": query}).encode()
        req = urllib.request.Request(
            OVERPASS_API_URL,
            data=data,
            headers={
                "User-Agent": USER_AGENT,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                result = json.loads(response.read().decode())
            return result.get("elements", [])
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la requête Overpass : {e}") from e

    def _parse_element(
        self, element: dict, ref_lat: float, ref_lng: float
    ) -> dict | None:
        """
        Convertit un élément OSM brut en dictionnaire restaurant standardisé.

        Args:
            element (dict): Élément OSM brut (node ou way).
            ref_lat (float): Latitude du point de référence.
            ref_lng (float): Longitude du point de référence.

        Returns:
            dict | None: Restaurant standardisé, ou None si l'élément est invalide.
        """
        tags = element.get("tags", {})
        name = tags.get("name")
        if not name:
            return None

        # Coordonnées : nœud direct ou centre du way
        if element.get("type") == "node":
            lat = element.get("lat", 0.0)
            lng = element.get("lon", 0.0)
        else:
            center = element.get("center", {})
            lat = center.get("lat", 0.0)
            lng = center.get("lon", 0.0)

        if not lat or not lng:
            return None

        distance = calculate_distance(ref_lat, ref_lng, lat, lng)

        # Extraction de la cuisine
        cuisine_raw = tags.get("cuisine", "")
        cuisine = cuisine_raw.split(";")[0].strip().lower() if cuisine_raw else None

        # Adresse approximative depuis les tags OSM
        address_parts = [
            tags.get("addr:housenumber", ""),
            tags.get("addr:street", ""),
            tags.get("addr:city", ""),
        ]
        address = " ".join(p for p in address_parts if p).strip()
        if not address:
            address = tags.get("addr:full", "")

        return self.make_restaurant(
            id=f"osm_{element.get('type', 'node')}_{element.get('id', 0)}",
            name=name,
            address=address,
            latitude=lat,
            longitude=lng,
            rating=None,           # OSM ne fournit pas de notes
            price_level=None,      # OSM ne fournit pas de niveaux de prix standardisés
            cuisine=cuisine,
            is_open_now=None,      # Nécessiterait un parsing des horaires OSM
            distance_m=round(distance, 1),
            phone=tags.get("phone"),
            website=tags.get("website"),
            source=self.SOURCE_NAME,
        )
