"""
geolocation.py
==============
Feature : Résolution d'adresse en coordonnées GPS (geocoding).

Description :
    Ce module fournit les fonctions nécessaires pour :
    - Convertir une adresse textuelle en coordonnées GPS (lat, lng)
    - Parser des coordonnées GPS fournies directement sous forme de chaîne "lat,lng"
    - Calculer la distance entre deux points GPS (formule haversine)

    Il supporte deux backends de geocoding :
    1. Google Geocoding API (si clé API disponible)
    2. Nominatim / OpenStreetMap (fallback gratuit, sans clé)

Cas d'usage :
    - L'utilisateur fournit "Paris, France" → retourne (48.8566, 2.3522)
    - L'utilisateur fournit "48.8566,2.3522" → parse directement les coordonnées
    - Calcul de la distance entre le point de recherche et chaque restaurant

Entrée  : str (adresse ou coordonnées), optional str (API key)
Sortie  : tuple (float, float) représentant (latitude, longitude)
"""

import math
import urllib.request
import urllib.parse
import json

from restaurant_scraper.config import (
    GOOGLE_PLACES_API_KEY,
    GOOGLE_GEOCODING_URL,
    NOMINATIM_GEOCODING_URL,
    REQUEST_TIMEOUT_SECONDS,
    EARTH_RADIUS_KM,
    USER_AGENT,
)


def parse_coordinates(location: str) -> tuple[float, float] | None:
    """
    Tente de parser une chaîne "lat,lng" en tuple de coordonnées.

    Args:
        location (str): Chaîne de la forme "48.8566,2.3522" ou "48.8566, 2.3522".

    Returns:
        tuple[float, float] | None: (latitude, longitude) si parsing réussi, None sinon.
    """
    parts = location.split(",")
    if len(parts) == 2:
        try:
            lat = float(parts[0].strip())
            lng = float(parts[1].strip())
            if -90 <= lat <= 90 and -180 <= lng <= 180:
                return (lat, lng)
        except ValueError:
            pass
    return None


def _geocode_google(address: str, api_key: str) -> tuple[float, float] | None:
    """
    Geocode une adresse via l'API Google Geocoding.

    Args:
        address (str): Adresse textuelle à geocoder.
        api_key (str): Clé API Google valide.

    Returns:
        tuple[float, float] | None: (latitude, longitude) ou None si échec.
    """
    params = urllib.parse.urlencode({"address": address, "key": api_key})
    url = f"{GOOGLE_GEOCODING_URL}?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode())

        if data.get("status") == "OK" and data.get("results"):
            location = data["results"][0]["geometry"]["location"]
            return (location["lat"], location["lng"])
    except Exception:
        pass

    return None


def _geocode_nominatim(address: str) -> tuple[float, float] | None:
    """
    Geocode une adresse via l'API Nominatim (OpenStreetMap), sans clé API.

    Args:
        address (str): Adresse textuelle à geocoder.

    Returns:
        tuple[float, float] | None: (latitude, longitude) ou None si échec.
    """
    params = urllib.parse.urlencode({
        "q": address,
        "format": "json",
        "limit": 1,
    })
    url = f"{NOMINATIM_GEOCODING_URL}?{params}"

    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read().decode())

        if data:
            return (float(data[0]["lat"]), float(data[0]["lon"]))
    except Exception:
        pass

    return None


def resolve_location(location: str, api_key: str = "") -> tuple[float, float]:
    """
    Résout une localisation (adresse ou coordonnées) en tuple (latitude, longitude).

    Stratégie de résolution :
    1. Tente de parser directement comme coordonnées "lat,lng"
    2. Si clé API Google disponible → Google Geocoding API
    3. Fallback → Nominatim (OpenStreetMap, gratuit)

    Args:
        location (str): Adresse textuelle (ex: "Paris, France") ou coordonnées (ex: "48.8566,2.3522").
        api_key (str): Clé API Google Places (optionnel). Si vide, utilise Nominatim.

    Returns:
        tuple[float, float]: (latitude, longitude).

    Raises:
        ValueError: Si la localisation ne peut pas être résolue.
    """
    # Tentative de parsing direct des coordonnées
    coords = parse_coordinates(location)
    if coords is not None:
        return coords

    # Geocoding via Google si clé disponible
    effective_key = api_key or GOOGLE_PLACES_API_KEY
    if effective_key:
        coords = _geocode_google(location, effective_key)
        if coords is not None:
            return coords

    # Fallback vers Nominatim (OSM)
    coords = _geocode_nominatim(location)
    if coords is not None:
        return coords

    raise ValueError(
        f"Impossible de résoudre la localisation : '{location}'. "
        "Vérifiez l'adresse ou fournissez des coordonnées GPS directes (lat,lng)."
    )


def calculate_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calcule la distance en mètres entre deux points GPS via la formule haversine.

    Args:
        lat1 (float): Latitude du premier point (en degrés décimaux).
        lng1 (float): Longitude du premier point (en degrés décimaux).
        lat2 (float): Latitude du second point (en degrés décimaux).
        lng2 (float): Longitude du second point (en degrés décimaux).

    Returns:
        float: Distance en mètres entre les deux points.
    """
    r = EARTH_RADIUS_KM * 1000  # Rayon de la Terre en mètres

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return r * c
