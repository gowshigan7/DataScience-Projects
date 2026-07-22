"""
geolocation.py
==============
Feature : Résolution d'une localisation en coordonnées GPS et calcul de distances.

Description :
    Ce module fournit les fonctions nécessaires pour :
    - Parser des coordonnées GPS fournies directement sous forme de chaîne "lat,lng"
    - Convertir une adresse textuelle en coordonnées GPS via Nominatim (OpenStreetMap)
    - Calculer la distance entre deux points GPS (formule haversine)

    Aucune clé API n'est nécessaire : le geocoding utilise exclusivement
    Nominatim, qui est gratuit et sans authentification.

Cas d'usage :
    - L'utilisateur fournit "48.8566,2.3522" → parse directement les coordonnées
    - L'utilisateur fournit "Paris, France" → résolu via Nominatim
    - Calcul de la distance entre le point de recherche et chaque fun fact

Entrée  : str (adresse ou coordonnées)
Sortie  : tuple (float, float) représentant (latitude, longitude)
"""

import json
import math
import urllib.parse
import urllib.request

from geo_fun_facts.config import (
    EARTH_RADIUS_KM,
    NOMINATIM_GEOCODING_URL,
    REQUEST_TIMEOUT_SECONDS,
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


def resolve_location(location: str) -> tuple[float, float]:
    """
    Résout une localisation (adresse ou coordonnées) en tuple (latitude, longitude).

    Stratégie de résolution :
    1. Tente de parser directement comme coordonnées "lat,lng"
    2. Fallback → Nominatim (OpenStreetMap, gratuit)

    Args:
        location (str): Adresse textuelle (ex: "Paris, France") ou coordonnées (ex: "48.8566,2.3522").

    Returns:
        tuple[float, float]: (latitude, longitude).

    Raises:
        ValueError: Si la localisation ne peut pas être résolue.
    """
    coords = parse_coordinates(location)
    if coords is not None:
        return coords

    coords = _geocode_nominatim(location)
    if coords is not None:
        return coords

    raise ValueError(
        f"Impossible de résoudre la localisation : '{location}'. "
        "Vérifiez l'adresse ou fournissez des coordonnées GPS directes (lat,lng)."
    )


def calculate_distance_km(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    """
    Calcule la distance en kilomètres entre deux points GPS via la formule haversine.

    Args:
        lat1 (float): Latitude du premier point (en degrés décimaux).
        lng1 (float): Longitude du premier point (en degrés décimaux).
        lat2 (float): Latitude du second point (en degrés décimaux).
        lng2 (float): Longitude du second point (en degrés décimaux).

    Returns:
        float: Distance en kilomètres entre les deux points.
    """
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return EARTH_RADIUS_KM * c
