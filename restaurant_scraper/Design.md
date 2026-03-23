# Restaurant Scraper — Design Document

## Objectif

`restaurant_scraper` est un outil modulaire en ligne de commande (CLI) permettant de rechercher et filtrer des restaurants à proximité d'une localisation donnée. L'outil récupère les données depuis Google Places API (source principale) ou OpenStreetMap via l'API Overpass (fallback gratuit), applique des filtres personnalisables, et exporte les résultats en tableau terminal, JSON ou CSV.

---

## Features disponibles

| Feature | Fichier | Description |
|---|---|---|
| Configuration centralisée | `config.py` | Toutes les constantes de l'application |
| Géolocalisation | `geo/geolocation.py` | Résolution d'adresse en GPS, calcul de distance |
| Scraper Google Places | `scraper/google_places.py` | Recherche via Google Places API |
| Scraper OpenStreetMap | `scraper/overpass_osm.py` | Recherche via Overpass (gratuit, sans clé) |
| Interface abstraite scraper | `scraper/base_scraper.py` | Contrat commun à tous les scrapers |
| Moteur de filtrage | `filters/filter_engine.py` | Orchestration de tous les filtres |
| Filtre par note | `filters/filter_rating.py` | Note minimale |
| Filtre par cuisine | `filters/filter_cuisine.py` | Type(s) de cuisine |
| Filtre par prix | `filters/filter_price.py` | Niveau(x) de prix (1-4) |
| Filtre ouvert maintenant | `filters/filter_open_now.py` | Restaurants actuellement ouverts |
| Filtre par distance | `filters/filter_distance.py` | Rayon de recherche max |
| Affichage terminal | `output/formatter_terminal.py` | Tableau ASCII formaté |
| Export JSON | `output/formatter_json.py` | Fichier JSON indenté |
| Export CSV | `output/formatter_csv.py` | Fichier CSV compatible Excel |
| Point d'entrée CLI | `main.py` | Pipeline complet + argparse |
| Données mockées | `tests/mock_data.py` | 15 restaurants fictifs pour les tests |
| Tests filtres | `tests/test_filters.py` | Tests unitaires des filtres |
| Tests scrapers | `tests/test_scraper.py` | Tests dry-run des scrapers |
| Tests formatters | `tests/test_output.py` | Tests des formateurs de sortie |

---

## Architecture des fichiers

```
restaurant_scraper/
│
├── Design.md                  # Ce fichier — documentation complète
├── config.py                  # Constantes et paramètres centralisés
├── main.py                    # Point d'entrée CLI (argparse)
│
├── scraper/
│   ├── __init__.py
│   ├── base_scraper.py        # Classe abstraite + format dict standardisé
│   ├── google_places.py       # Scraper Google Places API
│   └── overpass_osm.py        # Scraper OpenStreetMap / Overpass (gratuit)
│
├── filters/
│   ├── __init__.py
│   ├── filter_engine.py       # Orchestration des filtres (apply_filters + FilterEngine)
│   ├── filter_rating.py       # Filtre par note minimale
│   ├── filter_cuisine.py      # Filtre par type de cuisine
│   ├── filter_price.py        # Filtre par niveau de prix
│   ├── filter_open_now.py     # Filtre "ouvert maintenant"
│   └── filter_distance.py     # Filtre par rayon maximum
│
├── output/
│   ├── __init__.py
│   ├── formatter_terminal.py  # Tableau ASCII dans le terminal
│   ├── formatter_json.py      # Export JSON
│   └── formatter_csv.py       # Export CSV
│
├── geo/
│   ├── __init__.py
│   └── geolocation.py         # Geocoding + calcul distance haversine
│
└── tests/
    ├── __init__.py
    ├── mock_data.py            # 15 restaurants fictifs (aucun appel API)
    ├── test_filters.py         # Tests unitaires des filtres
    ├── test_scraper.py         # Tests scrapers en mode dry-run
    └── test_output.py          # Tests des formateurs de sortie
```

---

## Format de données standardisé (Restaurant)

Tous les scrapers retournent des listes de dictionnaires avec le format suivant :

```python
{
    "id":           str,        # Identifiant unique (issu de la source)
    "name":         str,        # Nom du restaurant
    "address":      str,        # Adresse complète
    "latitude":     float,      # Latitude GPS
    "longitude":    float,      # Longitude GPS
    "rating":       float|None, # Note moyenne (0.0 - 5.0), None si inconnue
    "price_level":  int|None,   # Niveau de prix (1-4), None si inconnu
    "cuisine":      str|None,   # Type de cuisine principal, None si inconnu
    "is_open_now":  bool|None,  # True si ouvert maintenant, None si inconnu
    "distance_m":   float|None, # Distance en mètres depuis le point de recherche
    "phone":        str|None,   # Numéro de téléphone, None si inconnu
    "website":      str|None,   # URL du site web, None si inconnu
    "source":       str,        # "google_places", "overpass_osm" ou "mock"
}
```

---

## Paramètres configurables (`config.py`)

| Paramètre | Valeur par défaut | Description |
|---|---|---|
| `DEFAULT_RADIUS_METERS` | `1000` | Rayon de recherche par défaut (mètres) |
| `DEFAULT_MIN_RATING` | `0.0` | Note minimale par défaut (0 = pas de filtre) |
| `DEFAULT_MAX_RESULTS` | `20` | Nombre max de résultats |
| `DEFAULT_OUTPUT_FORMAT` | `"terminal"` | Format de sortie par défaut |
| `GOOGLE_PLACES_API_KEY` | `""` | Clé API Google (ou variable `GOOGLE_PLACES_API_KEY`) |
| `SUPPORTED_CUISINES` | (liste) | Types de cuisine reconnus |
| `PRICE_LEVELS` | `{1:"€", 2:"€€", 3:"€€€", 4:"€€€€"}` | Mapping niveaux de prix |
| `OUTPUT_FORMATS` | `["terminal", "json", "csv"]` | Formats de sortie disponibles |
| `REQUEST_TIMEOUT_SECONDS` | `10` | Timeout HTTP |
| `EARTH_RADIUS_KM` | `6371.0` | Rayon terrestre (calcul haversine) |

---

## Arguments CLI

| Argument | Type | Défaut | Description |
|---|---|---|---|
| `--location` | `str` | *requis* | Adresse ou coordonnées GPS (`"lat,lng"`) |
| `--radius` | `float` | `1.0` | Rayon de recherche en km |
| `--min-rating` | `float` | `None` | Note minimale (ex: `4.0`) |
| `--cuisine` | `str+` | `None` | Type(s) de cuisine (ex: `italian japanese`) |
| `--price` | `int+` | `None` | Niveau(x) de prix `1`-`4` (ex: `1 2`) |
| `--open-now` | flag | `False` | Uniquement les restaurants ouverts |
| `--limit` | `int` | `20` | Nombre maximum de résultats |
| `--output` | `str` | `terminal` | Format : `terminal`, `json`, `csv` |
| `--output-file` | `str` | `None` | Chemin du fichier de sortie |
| `--source` | `str` | `auto` | Source : `google`, `osm`, `auto` |
| `--dry-run` | flag | `False` | Mode test sans appel API |

---

## Exemples d'utilisation CLI

```bash
# Recherche simple en mode dry-run (sans clé API)
python -m restaurant_scraper.main --location "Paris, France" --dry-run

# Restaurants italiens ou japonais, notés 4+, dans 1km, ouverts maintenant
python -m restaurant_scraper.main \
  --location "48.8566,2.3522" \
  --radius 1.0 \
  --cuisine italian japanese \
  --min-rating 4.0 \
  --open-now \
  --output terminal \
  --limit 15

# Export CSV des restaurants bon marché à Lyon
python -m restaurant_scraper.main \
  --location "Lyon, France" \
  --radius 2.0 \
  --price 1 2 \
  --output csv \
  --output-file results/lyon_restaurants.csv

# Export JSON via OpenStreetMap (sans clé Google)
python -m restaurant_scraper.main \
  --location "48.8566,2.3522" \
  --source osm \
  --radius 1.5 \
  --output json \
  --output-file results/restaurants.json

# Mode dry-run avec filtre cuisine et limite
python -m restaurant_scraper.main \
  --location "Paris" \
  --cuisine french italian \
  --min-rating 4.0 \
  --limit 5 \
  --dry-run
```

---

## Output terminal (exemple)

```
[DRY-RUN] Utilisation des donnees mockees

Restaurants trouves : 3 / 15 (filtres appliques)

==============================================================================
| Nom                           | Cuisine      | Note     | Prix   | Distance   | Ouvert   |
==============================================================================
| Mediterranean Dream           | Mediterranean| * 4.7    | €€€    | 180m       | Oui      |
------------------------------------------------------------------------------
| Trattoria Roma                | Italian      | * 4.6    | €€     | 320m       | Oui      |
------------------------------------------------------------------------------
| La Taverna Toscana            | Italian      | * 4.5    | €€€    | 550m       | ?        |
------------------------------------------------------------------------------
```

---

## Sources de données

### Google Places API (source principale)
- **Documentation** : https://developers.google.com/maps/documentation/places/web-service
- **Authentification** : Clé API requise (`GOOGLE_PLACES_API_KEY`)
- **Données disponibles** : Notes, niveaux de prix, horaires, photos, catégories
- **Limites** : Quota payant au-delà du crédit gratuit mensuel

### OpenStreetMap / Overpass API (fallback gratuit)
- **Documentation** : https://overpass-api.de/
- **Authentification** : Aucune clé requise
- **Données disponibles** : Nom, adresse, cuisine, téléphone, site web
- **Limites** : Pas de notes, pas de niveaux de prix, dépend de la qualité des contributions OSM

### Nominatim (geocoding)
- **Documentation** : https://nominatim.org/release-docs/latest/api/Search/
- **Authentification** : Aucune clé requise
- **Usage** : Fallback pour résoudre les adresses textuelles en GPS

---

## Pipeline de traitement

```
CLI (main.py)
    │
    ├── 1. resolve_location() → (lat, lng)
    │
    ├── 2. Scraper.fetch_restaurants() → List[dict]
    │       ├── GooglePlacesScraper  (si clé API disponible)
    │       └── OverpassOSMScraper   (fallback gratuit)
    │
    ├── 3. apply_filters() → (List[dict], int total)
    │       ├── filter_by_distance()
    │       ├── filter_by_rating()
    │       ├── filter_by_price()
    │       ├── filter_by_cuisine()
    │       └── filter_by_open_now()
    │
    └── 4. Formatter → Sortie
            ├── format_terminal()  → stdout
            ├── save_json()        → fichier .json
            └── save_csv()         → fichier .csv
```

---

## Mode dry-run

Le mode `--dry-run` permet d'utiliser l'outil sans aucune connexion réseau ni clé API :

1. Charge les 15 restaurants fictifs depuis `tests/mock_data.py`
2. Applique les filtres normalement
3. Formate et affiche les résultats (terminal) ou simule l'export (json/csv)
4. Affiche le bandeau `[DRY-RUN] Utilisation des donnees mockees`
5. N'écrit aucun fichier sur le disque

---

## Tests

```bash
# Lancer tous les tests
pytest restaurant_scraper/tests/ -v

# Tests uniquement des filtres
pytest restaurant_scraper/tests/test_filters.py -v

# Tests uniquement des scrapers (dry-run)
pytest restaurant_scraper/tests/test_scraper.py -v

# Tests uniquement des formateurs
pytest restaurant_scraper/tests/test_output.py -v

# Avec couverture de code
pytest restaurant_scraper/tests/ --cov=restaurant_scraper --cov-report=term-missing
```

---

## Installation et prérequis

```bash
# Python 3.11+ requis
python --version

# Aucune dépendance externe (stdlib uniquement)
# Pour les tests :
pip install pytest pytest-cov

# Configuration de la clé API (optionnel)
export GOOGLE_PLACES_API_KEY="votre_cle_api_google"

# Lancer en mode dry-run (sans clé API)
python -m restaurant_scraper.main --location "Paris" --dry-run
```

---

## Critères de succès

- [x] Tous les fichiers ont un docstring de module complet
- [x] Toutes les fonctions ont une docstring (Args / Returns)
- [x] `config.py` contient tous les paramètres (aucun hardcode ailleurs)
- [x] `Design.md` est complet et lisible
- [x] Le mode `--dry-run` fonctionne sans clé API
- [x] Les filtres sont combinables et indépendants
- [x] L'output JSON/CSV est propre et parseable
- [x] Tests unitaires couvrant tous les filtres, scrapers et formateurs
