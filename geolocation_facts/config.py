"""
config.py
=========
Fichier centralisé de configuration de l'application geolocation_facts.

Description :
    Ce fichier contient TOUTES les constantes et paramètres configurables de l'outil.
    Aucune valeur ne doit être codée en dur ailleurs dans le projet.
    Modifier ce fichier pour adapter le comportement de l'outil sans toucher au code métier.

Cas d'usage :
    - Changer le rayon de recherche par défaut
    - Changer la langue Wikipedia utilisée
    - Ajuster la longueur maximale d'un fun fact affiché
    - Modifier les chemins de sortie des fichiers

Entrée  : Aucune (fichier de constantes)
Sortie  : Variables importées par les autres modules
"""

import os

# ---------------------------------------------------------------------------
# Paramètres de recherche par défaut
# ---------------------------------------------------------------------------

DEFAULT_RADIUS_METERS = 5000          # Rayon de recherche par défaut (en mètres)
DEFAULT_MAX_RESULTS = 5               # Nombre de fun facts retournés par défaut
DEFAULT_LANGUAGE = "fr"              # Langue Wikipedia par défaut
DEFAULT_OUTPUT_FORMAT = "terminal"    # Format de sortie par défaut

# Rayon maximal accepté par l'API geosearch de Wikipedia (limite dure : 10 km)
MAX_GEOSEARCH_RADIUS_METERS = 10000

# ---------------------------------------------------------------------------
# Clés API et endpoints
# ---------------------------------------------------------------------------

GOOGLE_GEOCODING_API_KEY = os.environ.get("GOOGLE_GEOCODING_API_KEY", "")
GOOGLE_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
NOMINATIM_GEOCODING_URL = "https://nominatim.openstreetmap.org/search"

# L'endpoint Wikipedia dépend de la langue : on formate avec {lang}.
WIKIPEDIA_API_URL_TEMPLATE = "https://{lang}.wikipedia.org/w/api.php"
WIKIPEDIA_ARTICLE_URL_TEMPLATE = "https://{lang}.wikipedia.org/?curid={pageid}"

# ---------------------------------------------------------------------------
# Données de référence
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES = ["fr", "en", "es", "de", "it", "pt", "nl"]

OUTPUT_FORMATS = ["terminal", "json"]

# ---------------------------------------------------------------------------
# Chemins de fichiers
# ---------------------------------------------------------------------------

DEFAULT_JSON_OUTPUT_PATH = "output/facts.json"

# ---------------------------------------------------------------------------
# Paramètres réseau
# ---------------------------------------------------------------------------

REQUEST_TIMEOUT_SECONDS = 10         # Timeout des requêtes HTTP
USER_AGENT = "GeolocationFacts/1.0 (educational project)"

# Nombre de pages dont on récupère l'extrait en un seul appel API.
EXTRACT_BATCH_SIZE = 20

# ---------------------------------------------------------------------------
# Paramètres d'affichage / formatage des faits
# ---------------------------------------------------------------------------

# Longueur maximale d'un fun fact affiché (les extraits Wikipedia sont tronqués).
MAX_FACT_LENGTH = 280

# Largeur de la barre de séparation dans l'affichage terminal.
TERMINAL_DIVIDER_WIDTH = 70

# ---------------------------------------------------------------------------
# Constantes de conversion
# ---------------------------------------------------------------------------

METERS_PER_KM = 1000                 # Conversion km -> mètres
EARTH_RADIUS_KM = 6371.0             # Rayon moyen de la Terre (pour calcul haversine)
