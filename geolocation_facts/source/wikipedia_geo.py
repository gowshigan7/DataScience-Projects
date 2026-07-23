"""
wikipedia_geo.py
================
Feature : Récupération de fun facts géolocalisés via l'API Wikipedia.

Description :
    Ce module implémente la source utilisant l'API MediaWiki de Wikipedia.
    Il s'agit d'un backend GRATUIT et sans clé API.

    Le processus se déroule en deux étapes :
    1. `list=geosearch` : trouve les articles géolocalisés dans un rayon donné
       autour d'un point GPS (retourne pageid, titre, coordonnées).
    2. `prop=extracts` : récupère l'introduction (résumé en texte brut) de chaque
       article, qui constitue le « fun fact » présenté à l'utilisateur.

    L'extrait est tronqué à `MAX_FACT_LENGTH` caractères pour rester digeste.

Cas d'usage :
    - Pousser des faits sur les monuments/lieux proches de l'utilisateur
    - Recherche sans clé API : fonctionne immédiatement (Wikipedia public)
    - Mode dry-run : retourne une liste vide, données viennent de mock_data.py

Entrée  : float (lat), float (lng), int (radius_m), int (limit), str (lang)
Sortie  : List[dict] — fun facts au format standardisé BaseFactSource
"""

import json
import urllib.request
import urllib.parse

from geolocation_facts.source.base_source import BaseFactSource
from geolocation_facts.geo.geolocation import calculate_distance
from geolocation_facts.config import (
    WIKIPEDIA_API_URL_TEMPLATE,
    WIKIPEDIA_ARTICLE_URL_TEMPLATE,
    MAX_GEOSEARCH_RADIUS_METERS,
    REQUEST_TIMEOUT_SECONDS,
    EXTRACT_BATCH_SIZE,
    MAX_FACT_LENGTH,
    DEFAULT_LANGUAGE,
    USER_AGENT,
)


class WikipediaGeoSource(BaseFactSource):
    """
    Source de fun facts basée sur l'API geosearch de Wikipedia.

    Aucune clé API requise. Les faits sont issus de l'introduction des articles
    Wikipedia géolocalisés autour du point de recherche.
    """

    SOURCE_NAME = "wikipedia"

    def fetch_facts(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
        language: str = DEFAULT_LANGUAGE,
        **kwargs,
    ) -> list[dict]:
        """
        Récupère les fun facts via l'API Wikipedia (geosearch + extracts).

        Args:
            latitude (float): Latitude du point de recherche.
            longitude (float): Longitude du point de recherche.
            radius_m (int): Rayon de recherche en mètres (borné à 10 km par l'API).
            limit (int): Nombre maximum de faits à retourner.
            language (str): Code langue Wikipedia (ex: "fr", "en").
            **kwargs: Paramètres supplémentaires (non utilisés ici).

        Returns:
            list[dict]: Liste de fun facts au format standardisé.

        Raises:
            RuntimeError: Si une requête Wikipedia échoue.
        """
        if self.dry_run:
            print("[DRY-RUN] WikipediaGeoSource : aucun appel API effectué.")
            return []

        pages = self._geosearch(latitude, longitude, radius_m, limit, language)
        if not pages:
            return []

        page_ids = [p["pageid"] for p in pages]
        extracts = self._fetch_extracts(page_ids, language)

        facts = []
        for page in pages:
            if len(facts) >= limit:
                break
            fact = self._build_fact(page, extracts, latitude, longitude, language)
            if fact:
                facts.append(fact)

        return facts

    def _api_url(self, language: str) -> str:
        """
        Construit l'URL de base de l'API MediaWiki pour la langue donnée.

        Args:
            language (str): Code langue Wikipedia (ex: "fr").

        Returns:
            str: URL de l'endpoint api.php pour cette langue.
        """
        return WIKIPEDIA_API_URL_TEMPLATE.format(lang=language)

    def _get_json(self, url: str) -> dict:
        """
        Effectue une requête HTTP GET et retourne la réponse JSON décodée.

        Args:
            url (str): URL complète à requêter.

        Returns:
            dict: Réponse JSON décodée.

        Raises:
            RuntimeError: Si la requête échoue ou si la réponse n'est pas du JSON valide.
        """
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                return json.loads(response.read().decode())
        except Exception as e:
            raise RuntimeError(f"Erreur lors de la requête Wikipedia : {e}") from e

    def _geosearch(
        self,
        latitude: float,
        longitude: float,
        radius_m: int,
        limit: int,
        language: str,
    ) -> list[dict]:
        """
        Trouve les articles Wikipedia géolocalisés autour d'un point GPS.

        Args:
            latitude (float): Latitude du centre de recherche.
            longitude (float): Longitude du centre de recherche.
            radius_m (int): Rayon de recherche en mètres (borné à 10 km par l'API).
            limit (int): Nombre maximum d'articles à demander.
            language (str): Code langue Wikipedia.

        Returns:
            list[dict]: Liste d'articles bruts (pageid, title, lat, lon) de l'API geosearch.
        """
        radius = min(max(radius_m, 10), MAX_GEOSEARCH_RADIUS_METERS)
        params = urllib.parse.urlencode({
            "action": "query",
            "list": "geosearch",
            "gscoord": f"{latitude}|{longitude}",
            "gsradius": radius,
            "gslimit": min(max(limit, 1), 500),
            "format": "json",
        })
        url = f"{self._api_url(language)}?{params}"

        data = self._get_json(url)
        return data.get("query", {}).get("geosearch", [])

    def _fetch_extracts(self, page_ids: list[int], language: str) -> dict[int, str]:
        """
        Récupère l'introduction (extrait texte brut) de plusieurs articles.

        Les pages sont interrogées par lots de `EXTRACT_BATCH_SIZE` pour limiter
        le nombre d'appels réseau.

        Args:
            page_ids (list[int]): Identifiants de pages Wikipedia.
            language (str): Code langue Wikipedia.

        Returns:
            dict[int, str]: Association {pageid: extrait texte}.
        """
        extracts: dict[int, str] = {}

        for start in range(0, len(page_ids), EXTRACT_BATCH_SIZE):
            batch = page_ids[start:start + EXTRACT_BATCH_SIZE]
            params = urllib.parse.urlencode({
                "action": "query",
                "prop": "extracts",
                "exintro": 1,
                "explaintext": 1,
                "pageids": "|".join(str(pid) for pid in batch),
                "format": "json",
            })
            url = f"{self._api_url(language)}?{params}"

            data = self._get_json(url)
            pages = data.get("query", {}).get("pages", {})
            for pid_str, page in pages.items():
                try:
                    pid = int(pid_str)
                except (TypeError, ValueError):
                    continue
                extract = page.get("extract", "")
                if extract:
                    extracts[pid] = extract

        return extracts

    def _build_fact(
        self,
        page: dict,
        extracts: dict[int, str],
        ref_lat: float,
        ref_lng: float,
        language: str,
    ) -> dict | None:
        """
        Convertit un article brut + son extrait en fun fact standardisé.

        Args:
            page (dict): Article brut issu de geosearch (pageid, title, lat, lon).
            extracts (dict[int, str]): Association {pageid: extrait texte}.
            ref_lat (float): Latitude du point de référence.
            ref_lng (float): Longitude du point de référence.
            language (str): Code langue Wikipedia (pour construire l'URL).

        Returns:
            dict | None: Fun fact standardisé, ou None si aucun extrait disponible.
        """
        pageid = page.get("pageid")
        title = page.get("title")
        lat = page.get("lat")
        lng = page.get("lon")

        if pageid is None or not title or lat is None or lng is None:
            return None

        extract = extracts.get(pageid)
        if not extract:
            return None

        fact_text = self._summarize(extract)
        distance = calculate_distance(ref_lat, ref_lng, lat, lng)
        url = WIKIPEDIA_ARTICLE_URL_TEMPLATE.format(lang=language, pageid=pageid)

        return self.make_fact(
            id=f"wikipedia_{language}_{pageid}",
            title=title,
            fact=fact_text,
            latitude=lat,
            longitude=lng,
            distance_m=round(distance, 1),
            category=None,  # Wikipedia geosearch ne fournit pas de catégorie directe
            url=url,
            source=self.SOURCE_NAME,
        )

    @staticmethod
    def _summarize(extract: str) -> str:
        """
        Réduit un extrait Wikipedia à un fun fact court et lisible.

        Le texte est nettoyé (espaces normalisés) puis tronqué à
        `MAX_FACT_LENGTH` caractères, sans couper un mot en deux.

        Args:
            extract (str): Extrait brut de l'article Wikipedia.

        Returns:
            str: Fun fact résumé et tronqué.
        """
        text = " ".join(extract.split())
        if len(text) <= MAX_FACT_LENGTH:
            return text

        truncated = text[:MAX_FACT_LENGTH]
        last_space = truncated.rfind(" ")
        if last_space > 0:
            truncated = truncated[:last_space]
        return truncated.rstrip() + "…"
