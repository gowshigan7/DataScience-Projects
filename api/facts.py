"""
api/facts.py
============
Feature : Fonction serverless Vercel exposant geolocation_facts en HTTP JSON.

Description :
    Point d'entrée serverless (runtime Python de Vercel) qui réutilise le package
    geolocation_facts pour servir des fun facts géolocalisés en direct :
    1. Résout une localisation (adresse ou coordonnées) en (lat, lng)
    2. Récupère les articles Wikipedia proches (geosearch + extracts)
    3. Applique les filtres (distance, mot-clé) et la limite
    4. Retourne un JSON prêt à consommer par le frontend

    Aucune dépendance externe : uniquement la bibliothèque standard + le package
    geolocation_facts embarqué (voir includeFiles dans vercel.json).

Cas d'usage :
    GET /api/facts?location=Berlin&radius=2&limit=8&lang=en
    GET /api/facts?lat=48.8584&lng=2.2945&radius=3&limit=10&keyword=tower

Entrée  : Paramètres de requête (query string)
Sortie  : Réponse HTTP JSON { center, count, total, facts[] }
"""

import os
import sys
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Rendre le package geolocation_facts (à la racine du dépôt) importable.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from geolocation_facts.geo.geolocation import resolve_location
from geolocation_facts.source.wikipedia_geo import WikipediaGeoSource
from geolocation_facts.filters.filter_engine import apply_filters

# Bornes de sécurité pour un service public.
MAX_LIMIT = 30
MAX_RADIUS_KM = 10.0
DEFAULT_RADIUS_KM = 3.0
DEFAULT_LIMIT = 8


def _first(qs: dict, key: str, default: str = "") -> str:
    """
    Retourne la première valeur d'un paramètre de query string.

    Args:
        qs (dict): Dictionnaire issu de parse_qs.
        key (str): Nom du paramètre recherché.
        default (str): Valeur par défaut si le paramètre est absent.

    Returns:
        str: Première valeur du paramètre, ou la valeur par défaut.
    """
    return (qs.get(key) or [default])[0]


def build_payload(qs: dict) -> tuple[int, dict]:
    """
    Construit la réponse JSON à partir des paramètres de requête.

    Args:
        qs (dict): Paramètres de query string (issus de parse_qs).

    Returns:
        tuple[int, dict]: (code HTTP, corps JSON sérialisable).
    """
    location = _first(qs, "location").strip()
    lat_raw = _first(qs, "lat").strip()
    lng_raw = _first(qs, "lng").strip()
    keyword = _first(qs, "keyword").strip() or None
    lang = _first(qs, "lang", "en").strip() or "en"

    try:
        radius = min(max(float(_first(qs, "radius", str(DEFAULT_RADIUS_KM))), 0.1), MAX_RADIUS_KM)
    except ValueError:
        radius = DEFAULT_RADIUS_KM
    try:
        limit = min(max(int(_first(qs, "limit", str(DEFAULT_LIMIT))), 1), MAX_LIMIT)
    except ValueError:
        limit = DEFAULT_LIMIT

    # 1. Résolution du centre de recherche.
    label = location or None
    if lat_raw and lng_raw:
        try:
            center_lat, center_lng = float(lat_raw), float(lng_raw)
        except ValueError:
            return 400, {"error": "Coordonnées 'lat'/'lng' invalides."}
    elif location:
        try:
            center_lat, center_lng = resolve_location(location)
        except ValueError as e:
            return 400, {"error": str(e)}
    else:
        return 400, {"error": "Fournir un paramètre 'location' (adresse) ou 'lat' et 'lng'."}

    # 2. Récupération des faits.
    try:
        source = WikipediaGeoSource(dry_run=False)
        facts = source.fetch_facts(
            latitude=center_lat,
            longitude=center_lng,
            radius_m=int(radius * 1000),
            limit=limit * 3,
            language=lang,
        )
    except RuntimeError as e:
        return 502, {"error": f"Source Wikipedia indisponible : {e}"}

    # 3. Filtrage + limite.
    filtered, total = apply_filters(
        facts=facts,
        keyword=keyword,
        max_radius_km=radius,
        limit=limit,
    )

    payload = {
        "center": {"lat": center_lat, "lng": center_lng, "label": label},
        "count": len(filtered),
        "total": total,
        "radius_km": radius,
        "language": lang,
        "facts": [
            {
                "title": f["title"],
                "fact": f["fact"],
                "lat": f["latitude"],
                "lng": f["longitude"],
                "dist": round(f["distance_m"]) if f["distance_m"] is not None else None,
                "url": f["url"],
            }
            for f in filtered
        ],
    }
    return 200, payload


class handler(BaseHTTPRequestHandler):
    """Handler serverless attendu par le runtime Python de Vercel."""

    def do_GET(self):  # noqa: N802 (nom imposé par BaseHTTPRequestHandler)
        """Traite une requête GET et renvoie les fun facts au format JSON."""
        try:
            qs = parse_qs(urlparse(self.path).query)
            code, body = build_payload(qs)
        except Exception as e:  # garde-fou : ne jamais renvoyer une 500 opaque
            code, body = 500, {"error": f"Erreur interne : {e}"}

        self._send(code, body)

    def do_OPTIONS(self):  # noqa: N802
        """Répond aux requêtes CORS preflight."""
        self._send(204, None)

    def _send(self, code: int, body: dict | None) -> None:
        """
        Écrit une réponse HTTP JSON avec les en-têtes CORS et de cache.

        Args:
            code (int): Code de statut HTTP.
            body (dict | None): Corps JSON, ou None pour une réponse sans corps.
        """
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
        # Cache CDN : mêmes coordonnées -> mêmes faits pendant 1h.
        self.send_header("Cache-Control", "public, s-maxage=3600, stale-while-revalidate=86400")
        self.end_headers()
        if body is not None:
            self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))
