"""
config.py
=========
Fichier centralisé de configuration du module geo_fun_facts.

Description :
    Ce fichier contient TOUTES les constantes et paramètres configurables du module.
    Aucune valeur ne doit être codée en dur ailleurs dans le projet.

Cas d'usage :
    - Changer le rayon de recherche par défaut
    - Ajouter une nouvelle source de fun facts
    - Modifier la langue Wikipedia utilisée

Entrée  : Aucune (fichier de constantes)
Sortie  : Variables importées par les autres modules
"""

# ---------------------------------------------------------------------------
# Paramètres de recherche par défaut
# ---------------------------------------------------------------------------

DEFAULT_RADIUS_KM = 50.0             # Rayon de recherche par défaut (en kilomètres)
DEFAULT_MAX_RESULTS = 10             # Nombre maximum de fun facts retournés

# ---------------------------------------------------------------------------
# Sources de fun facts
# ---------------------------------------------------------------------------

DEFAULT_SOURCE = "mock"
AVAILABLE_SOURCES = ["mock", "wikipedia"]

FACT_CATEGORIES = [
    "histoire",
    "nature",
    "culture",
    "record",
    "science",
    "insolite",
]

# ---------------------------------------------------------------------------
# Endpoints externes
# ---------------------------------------------------------------------------

NOMINATIM_GEOCODING_URL = "https://nominatim.openstreetmap.org/search"
WIKIPEDIA_API_URL_TEMPLATE = "https://{lang}.wikipedia.org/w/api.php"
DEFAULT_WIKIPEDIA_LANG = "fr"
WIKIPEDIA_EXTRACT_CHARS = 280         # Longueur max de l'extrait utilisé comme fun fact

# ---------------------------------------------------------------------------
# Paramètres réseau
# ---------------------------------------------------------------------------

REQUEST_TIMEOUT_SECONDS = 10
USER_AGENT = "GeoFunFacts/1.0 (educational project)"

# ---------------------------------------------------------------------------
# Constantes de conversion
# ---------------------------------------------------------------------------

EARTH_RADIUS_KM = 6371.0             # Rayon moyen de la Terre (pour calcul haversine)
