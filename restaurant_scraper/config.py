"""
config.py
=========
Fichier centralisé de configuration de l'application restaurant_scraper.

Description :
    Ce fichier contient TOUTES les constantes et paramètres configurables de l'outil.
    Aucune valeur ne doit être codée en dur ailleurs dans le projet.
    Modifier ce fichier pour adapter le comportement de l'outil sans toucher au code métier.

Cas d'usage :
    - Changer le rayon de recherche par défaut
    - Configurer la clé API Google Places
    - Ajouter de nouveaux types de cuisine supportés
    - Modifier les chemins de sortie des fichiers

Entrée  : Aucune (fichier de constantes)
Sortie  : Variables importées par les autres modules
"""

import os

# ---------------------------------------------------------------------------
# Paramètres de recherche par défaut
# ---------------------------------------------------------------------------

DEFAULT_RADIUS_METERS = 1000          # Rayon de recherche par défaut (en mètres)
DEFAULT_MIN_RATING = 0.0              # Note minimale par défaut (0 = pas de filtre)
DEFAULT_MAX_RESULTS = 20              # Nombre maximum de résultats retournés
DEFAULT_OUTPUT_FORMAT = "terminal"    # Format de sortie par défaut

# ---------------------------------------------------------------------------
# Clés API et endpoints
# ---------------------------------------------------------------------------

GOOGLE_PLACES_API_KEY = os.environ.get("GOOGLE_PLACES_API_KEY", "")
GOOGLE_PLACES_NEARBY_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
GOOGLE_PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"
GOOGLE_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"

OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
NOMINATIM_GEOCODING_URL = "https://nominatim.openstreetmap.org/search"

# ---------------------------------------------------------------------------
# Données de référence
# ---------------------------------------------------------------------------

SUPPORTED_CUISINES = [
    "italian",
    "japanese",
    "french",
    "chinese",
    "indian",
    "mexican",
    "thai",
    "american",
    "mediterranean",
    "spanish",
    "greek",
    "vietnamese",
    "korean",
    "lebanese",
    "burger",
    "pizza",
    "sushi",
    "vegan",
    "seafood",
]

PRICE_LEVELS = {
    1: "€",
    2: "€€",
    3: "€€€",
    4: "€€€€",
}

OUTPUT_FORMATS = ["terminal", "json", "csv"]

# ---------------------------------------------------------------------------
# Chemins de fichiers
# ---------------------------------------------------------------------------

DRY_RUN_DATA_PATH = "tests/mock_data.py"
DEFAULT_JSON_OUTPUT_PATH = "output/restaurants.json"
DEFAULT_CSV_OUTPUT_PATH = "output/restaurants.csv"

# ---------------------------------------------------------------------------
# Paramètres réseau
# ---------------------------------------------------------------------------

REQUEST_TIMEOUT_SECONDS = 10         # Timeout des requêtes HTTP
MAX_RETRIES = 3                      # Nombre de tentatives en cas d'erreur réseau
USER_AGENT = "RestaurantScraper/1.0 (educational project)"

# ---------------------------------------------------------------------------
# Paramètres d'affichage terminal
# ---------------------------------------------------------------------------

TERMINAL_TABLE_MAX_NAME_WIDTH = 30   # Largeur max de la colonne "Nom" dans le tableau
TERMINAL_TABLE_MAX_ADDRESS_WIDTH = 40 # Largeur max de la colonne "Adresse"

# ---------------------------------------------------------------------------
# Constantes de conversion
# ---------------------------------------------------------------------------

METERS_PER_KM = 1000                 # Conversion km -> mètres
EARTH_RADIUS_KM = 6371.0             # Rayon moyen de la Terre (pour calcul haversine)
