"""
wikipedia_provider.py
======================
Feature : Fournisseur de fun facts dynamiques via l'API Wikipedia (geosearch).

Description :
    Ce module implémente le fournisseur utilisant l'API publique de Wikipedia.
    Il combine le générateur "geosearch" (articles proches d'un point GPS) avec
    la propriété "extracts" (résumé de l'article) en une seule requête HTTP.

    Aucune clé API n'est nécessaire : l'API Wikipedia REST/action est publique
    et gratuite.

Cas d'usage :
    - Fun facts dynamiques et à jour autour d'une localisation donnée
    - Complète (ou remplace) les données statiques de mock_provider.py
    - Fallback : si aucun article n'est trouvé dans le rayon, retourne une liste vide

Entrée  : float (lat), float (lng), float (radius_km), int (limit)
Sortie  : List[dict] — fun facts au format standardisé FactProvider

Note :
    La logique réseau (_fetch_raw) est séparée de la logique de parsing
    (_parse_response) afin de permettre des tests unitaires sans appel réseau réel.
"""

import json
import urllib.error
import urllib.parse
import urllib.request

from geo_fun_facts.config import (
    DEFAULT_WIKIPEDIA_LANG,
    REQUEST_TIMEOUT_SECONDS,
    USER_AGENT,
    WIKIPEDIA_API_URL_TEMPLATE,
    WIKIPEDIA_EXTRACT_CHARS,
)
from geo_fun_facts.providers.base_provider import FactProvider


class WikipediaFactProvider(FactProvider):
    """
    Fournisseur de fun facts basé sur l'API geosearch + extracts de Wikipedia.
    """

    SOURCE_NAME = "wikipedia"

    def __init__(self, lang: str = DEFAULT_WIKIPEDIA_LANG):
        """
        Initialise le fournisseur Wikipedia.

        Args:
            lang (str): Code langue Wikipedia à interroger (ex: "fr", "en").
        """
        self.lang = lang

    def get_facts(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int,
    ) -> list[dict]:
        """
        Récupère les articles Wikipedia proches d'un point GPS comme fun facts.

        Args:
            latitude (float): Latitude du point de recherche.
            longitude (float): Longitude du point de recherche.
            radius_km (float): Rayon de recherche en kilomètres (max 10km côté API Wikipedia).
            limit (int): Nombre maximum de résultats à retourner (max 500 côté API).

        Returns:
            list[dict]: Fun facts au format standardisé, triés par distance croissante.
                        Liste vide si l'API est injoignable ou ne retourne rien.
        """
        radius_m = min(int(radius_km * 1000), 10000)  # limite Wikipedia : 10 000 m
        raw = self._fetch_raw(latitude, longitude, radius_m, limit, self.lang)
        if raw is None:
            return []
        return self._parse_response(raw, self.SOURCE_NAME, self.lang)

    @staticmethod
    def _fetch_raw(
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
        lang: str,
    ) -> dict | None:
        """
        Effectue l'appel réseau vers l'API Wikipedia et retourne le JSON brut.

        Args:
            latitude (float): Latitude du point de recherche.
            longitude (float): Longitude du point de recherche.
            radius_m (int): Rayon de recherche en mètres (max 10 000).
            limit (int): Nombre maximum d'articles à récupérer.
            lang (str): Code langue Wikipedia.

        Returns:
            dict | None: Réponse JSON décodée, ou None en cas d'échec réseau.
        """
        api_url = WIKIPEDIA_API_URL_TEMPLATE.format(lang=lang)
        params = urllib.parse.urlencode({
            "action": "query",
            "generator": "geosearch",
            "ggscoord": f"{latitude}|{longitude}",
            "ggsradius": radius_m,
            "ggslimit": max(limit, 1),
            "prop": "extracts|coordinates",
            "exintro": 1,
            "explaintext": 1,
            "exchars": WIKIPEDIA_EXTRACT_CHARS,
            "format": "json",
        })
        url = f"{api_url}?{params}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode())
        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
            return None

    @staticmethod
    def _parse_response(raw: dict, source_name: str, lang: str) -> list[dict]:
        """
        Transforme la réponse JSON brute de l'API Wikipedia en fun facts standardisés.

        Args:
            raw (dict): Réponse JSON décodée de l'API Wikipedia.
            source_name (str): Nom de la source à inscrire dans chaque fun fact.
            lang (str): Code langue Wikipedia, utilisé pour construire l'URL de l'article.

        Returns:
            list[dict]: Fun facts au format standardisé, triés par distance croissante.
        """
        pages = raw.get("query", {}).get("pages", {})
        results = []

        for page in pages.values():
            coordinates = page.get("coordinates") or [{}]
            coord = coordinates[0]
            extract = (page.get("extract") or "").strip()

            if not extract or "lat" not in coord or "lon" not in coord:
                continue

            results.append(
                FactProvider.make_fact(
                    id=f"wiki_{page.get('pageid')}",
                    title=page.get("title", ""),
                    fact=extract,
                    latitude=coord["lat"],
                    longitude=coord["lon"],
                    distance_km=coord.get("dist", 0.0) / 1000,
                    category=None,
                    url=f"https://{lang}.wikipedia.org/wiki/{urllib.parse.quote(page.get('title', ''))}",
                    source=source_name,
                )
            )

        results.sort(key=lambda f: f["distance_km"])
        return results
