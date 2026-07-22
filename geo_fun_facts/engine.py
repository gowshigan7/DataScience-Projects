"""
engine.py
=========
Feature : Point d'entrée principal du module — récupération de fun facts par localisation.

Description :
    Ce module orchestre la résolution de la localisation et la récupération
    des fun facts via le fournisseur choisi (mock ou wikipedia). C'est la
    fonction publique à utiliser pour intégrer geo_fun_facts dans une autre
    application.

Cas d'usage :
    - get_fun_facts("Paris, France") → fun facts statiques (mock) autour de Paris
    - get_fun_facts("48.8566,2.3522", source="wikipedia") → articles Wikipedia proches
    - get_fun_facts("Tokyo", radius_km=100, limit=5) → jusqu'à 5 fun facts dans 100km

Entrée  : str (adresse ou coordonnées), float (rayon_km), int (limite), str (source)
Sortie  : List[dict] — fun facts au format standardisé (voir providers/base_provider.py)
"""

from geo_fun_facts.config import AVAILABLE_SOURCES, DEFAULT_MAX_RESULTS, DEFAULT_RADIUS_KM, DEFAULT_SOURCE
from geo_fun_facts.geo.geolocation import resolve_location
from geo_fun_facts.providers.base_provider import FactProvider
from geo_fun_facts.providers.mock_provider import MockFactProvider
from geo_fun_facts.providers.wikipedia_provider import WikipediaFactProvider

_PROVIDERS: dict[str, FactProvider] = {
    "mock": MockFactProvider(),
    "wikipedia": WikipediaFactProvider(),
}


def get_fun_facts(
    location: str,
    radius_km: float = DEFAULT_RADIUS_KM,
    limit: int = DEFAULT_MAX_RESULTS,
    source: str = DEFAULT_SOURCE,
) -> list[dict]:
    """
    Récupère des fun facts géolocalisés autour d'une adresse ou de coordonnées GPS.

    Args:
        location (str): Adresse textuelle (ex: "Paris, France") ou coordonnées GPS
                        (ex: "48.8566,2.3522").
        radius_km (float): Rayon de recherche en kilomètres. Défaut : DEFAULT_RADIUS_KM.
        limit (int): Nombre maximum de fun facts retournés. Défaut : DEFAULT_MAX_RESULTS.
        source (str): Fournisseur à utiliser, parmi AVAILABLE_SOURCES ("mock", "wikipedia").
                      Défaut : DEFAULT_SOURCE.

    Returns:
        list[dict]: Fun facts au format standardisé, triés par distance croissante.

    Raises:
        ValueError: Si la localisation ne peut pas être résolue, ou si la source
                    demandée n'existe pas.
    """
    if source not in AVAILABLE_SOURCES:
        raise ValueError(
            f"Source inconnue : '{source}'. Sources disponibles : {AVAILABLE_SOURCES}."
        )

    latitude, longitude = resolve_location(location)
    provider = _PROVIDERS[source]

    return provider.get_facts(latitude, longitude, radius_km, limit)
