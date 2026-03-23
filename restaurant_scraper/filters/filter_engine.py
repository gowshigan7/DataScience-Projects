"""
filter_engine.py
================
Feature : Moteur de filtrage principal — orchestration de tous les filtres.

Description :
    Ce module fournit le moteur central de filtrage qui applique séquentiellement
    tous les filtres disponibles sur une liste de restaurants.

    Chaque filtre est indépendant et optionnel. Si un critère de filtre n'est pas
    spécifié (None ou valeur par défaut), le filtre correspondant est ignoré.

    L'ordre d'application des filtres est optimisé pour réduire la liste le plus
    tôt possible :
    1. Distance (filtre le plus structurel)
    2. Note minimale
    3. Niveau de prix
    4. Type de cuisine
    5. Ouvert maintenant

Cas d'usage :
    - Applique tous les filtres configurés en une seule passe
    - Retourne les résultats filtrés et un rapport de réduction
    - Utilisé par main.py après le scraping

Entrée  : List[dict] (restaurants), dict (paramètres de filtrage)
Sortie  : List[dict] — liste filtrée, int — nombre de résultats avant filtrage
"""

from restaurant_scraper.filters.filter_distance import filter_by_distance
from restaurant_scraper.filters.filter_rating import filter_by_rating
from restaurant_scraper.filters.filter_price import filter_by_price
from restaurant_scraper.filters.filter_cuisine import filter_by_cuisine
from restaurant_scraper.filters.filter_open_now import filter_by_open_now


def apply_filters(
    restaurants: list[dict],
    min_rating: float | None = None,
    cuisines: list[str] | None = None,
    price_levels: list[int] | None = None,
    open_now: bool = False,
    max_radius_km: float | None = None,
    limit: int | None = None,
) -> tuple[list[dict], int]:
    """
    Applique séquentiellement tous les filtres configurés sur une liste de restaurants.

    Args:
        restaurants (list[dict]): Liste brute de restaurants récupérés par le scraper.
        min_rating (float | None): Note minimale acceptable (ex: 4.0). None = pas de filtre.
        cuisines (list[str] | None): Types de cuisine acceptés (ex: ["italian", "japanese"]).
                                      None ou [] = pas de filtre.
        price_levels (list[int] | None): Niveaux de prix acceptés (ex: [1, 2]).
                                          None ou [] = pas de filtre.
        open_now (bool): Si True, ne conserve que les restaurants ouverts. Défaut : False.
        max_radius_km (float | None): Rayon maximum en km. None ou 0 = pas de filtre.
        limit (int | None): Nombre maximum de résultats finaux. None = pas de limite.

    Returns:
        tuple[list[dict], int]: (liste filtrée, nombre de résultats avant filtrage)
    """
    total_before = len(restaurants)

    # Application séquentielle des filtres
    result = filter_by_distance(restaurants, max_radius_km)
    result = filter_by_rating(result, min_rating)
    result = filter_by_price(result, price_levels)
    result = filter_by_cuisine(result, cuisines)
    result = filter_by_open_now(result, open_now)

    # Tri par distance croissante
    result = sorted(result, key=lambda r: r.get("distance_m") or float("inf"))

    # Application de la limite finale
    if limit is not None and limit > 0:
        result = result[:limit]

    return result, total_before


class FilterEngine:
    """
    Classe utilitaire encapsulant le moteur de filtrage avec configuration persistante.

    Permet de configurer les filtres une fois et de les appliquer sur plusieurs
    listes de restaurants (utile pour les tests ou les appels multiples).
    """

    def __init__(
        self,
        min_rating: float | None = None,
        cuisines: list[str] | None = None,
        price_levels: list[int] | None = None,
        open_now: bool = False,
        max_radius_km: float | None = None,
        limit: int | None = None,
    ):
        """
        Initialise le moteur de filtrage avec des paramètres persistants.

        Args:
            min_rating (float | None): Note minimale acceptable.
            cuisines (list[str] | None): Types de cuisine acceptés.
            price_levels (list[int] | None): Niveaux de prix acceptés.
            open_now (bool): Filtre ouvert maintenant.
            max_radius_km (float | None): Rayon maximum en km.
            limit (int | None): Nombre maximum de résultats.
        """
        self.min_rating = min_rating
        self.cuisines = cuisines
        self.price_levels = price_levels
        self.open_now = open_now
        self.max_radius_km = max_radius_km
        self.limit = limit

    def apply(self, restaurants: list[dict]) -> tuple[list[dict], int]:
        """
        Applique les filtres configurés sur une liste de restaurants.

        Args:
            restaurants (list[dict]): Liste brute de restaurants.

        Returns:
            tuple[list[dict], int]: (liste filtrée, nombre avant filtrage).
        """
        return apply_filters(
            restaurants=restaurants,
            min_rating=self.min_rating,
            cuisines=self.cuisines,
            price_levels=self.price_levels,
            open_now=self.open_now,
            max_radius_km=self.max_radius_km,
            limit=self.limit,
        )

    def describe(self) -> str:
        """
        Retourne une description textuelle des filtres configurés.

        Returns:
            str: Description lisible des filtres actifs.
        """
        parts = []
        if self.min_rating:
            parts.append(f"note >= {self.min_rating}")
        if self.cuisines:
            parts.append(f"cuisine in [{', '.join(self.cuisines)}]")
        if self.price_levels:
            parts.append(f"prix in {self.price_levels}")
        if self.open_now:
            parts.append("ouvert maintenant")
        if self.max_radius_km:
            parts.append(f"rayon <= {self.max_radius_km}km")
        if self.limit:
            parts.append(f"limite {self.limit} résultats")

        return " | ".join(parts) if parts else "aucun filtre"
