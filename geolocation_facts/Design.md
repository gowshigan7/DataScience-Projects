# geolocation_facts — Design

Application en ligne de commande qui **pousse des « fun facts »** sur les lieux
proches d'une localisation donnée, à partir des articles géolocalisés de
Wikipedia (API MediaWiki `geosearch` + `extracts`). Gratuit, sans clé API.

## Objectif

Donner à l'utilisateur, à partir d'une adresse ou de coordonnées GPS, une petite
liste de faits intéressants sur ce qui l'entoure (monuments, histoire, lieux
notables), triés du plus proche au plus lointain.

## Architecture — une responsabilité par fichier

```
config.py                 ← TOUTES les constantes (endpoints, rayons, langues, limites)
geo/geolocation.py        ← geocoding (Google → Nominatim) + distance haversine
source/base_source.py     ← interface abstraite + format « fait » standardisé (make_fact)
source/wikipedia_geo.py   ← source Wikipedia geosearch (gratuite, sans clé)
filters/filter_engine.py  ← orchestre les filtres via apply_filters()
filters/filter_*.py       ← un filtre par fichier, fonctions pures
output/formatter_*.py     ← cartes terminal | export JSON
main.py                   ← point d'entrée CLI (argparse), assemble le pipeline
tests/mock_data.py        ← 8 faits statiques, utilisés par --dry-run et tous les tests
```

## Pipeline

1. **Parsing CLI** (`main.build_parser`)
2. **Résolution de la localisation** en `(lat, lng)` (`geo.resolve_location`)
   - coordonnées directes `"lat,lng"` → parsées localement, sans réseau
   - sinon Google Geocoding (si clé) → fallback Nominatim (OSM)
3. **Récupération des faits** (`source.WikipediaGeoSource.fetch_facts`)
   - `geosearch` : articles dans le rayon (borné à 10 km par l'API)
   - `extracts` : introduction de chaque article, résumée et tronquée
   - en `--dry-run` : court-circuit avant tout appel réseau, charge `MOCK_FACTS`
4. **Filtrage** (`filters.apply_filters`) : distance → mot-clé, tri par distance, limite
5. **Sortie** (`output`) : cartes terminal ou export JSON

## Format standardisé d'un fait

```python
{
    "id": str,           # ex: "wikipedia_fr_1359783"
    "title": str,        # titre de l'article / du lieu
    "fact": str,         # extrait résumé (<= MAX_FACT_LENGTH caractères)
    "latitude": float,
    "longitude": float,
    "distance_m": float, # distance haversine depuis le point de recherche, None si inconnue
    "category": str,     # None (l'API geosearch ne fournit pas de catégorie)
    "url": str,          # lien vers l'article Wikipedia
    "source": str,       # "wikipedia"
}
```

## Conventions (identiques à restaurant_scraper)

- **Constantes centralisées** : toute valeur configurable vit dans `config.py`.
- **Docstrings** : chaque module a un en-tête (Description / Cas d'usage / Entrée /
  Sortie) ; chaque fonction documente Args + Returns.
- **Contrat de filtre** : chaque `filter_*.py` expose une seule fonction pure qui
  retourne la liste inchangée quand son paramètre est `None`/falsy — jamais d'exception.
- **Contrat de source** : toute source étend `BaseFactSource` et retourne
  `list[dict]` via `make_fact()`. Le `--dry-run` court-circuite avant tout réseau.

## Utilisation

```bash
# Fun facts autour d'une adresse
python -m geolocation_facts.main --location "Paris, France" --radius 2.0

# Coordonnées GPS, en anglais, filtré par mot-clé
python -m geolocation_facts.main --location "48.8584,2.2945" --lang en --keyword tower

# Export JSON
python -m geolocation_facts.main --location "Lyon" --output json --limit 10

# Mode test (aucun réseau)
python -m geolocation_facts.main --location "Paris" --dry-run
```

## Tests

```bash
pytest geolocation_facts/tests/ -v   # 60 tests, données mockées, aucun appel réseau
```
