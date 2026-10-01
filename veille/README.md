# Veille — surveillance automatique de sujets

Application en ligne de commande qui suit les sujets que vous choisissez (entreprise,
technologie, personne, thème) et rassemble les informations récentes dans un rapport
classé par catégorie : finance, partenariats/clients, nominations, produits, prix, événements.

**Aucune clé API, aucune dépendance** : Python 3.9+ et la bibliothèque standard suffisent.

## Démarrage

```bash
# 1. Ajouter un sujet (alias facultatifs, --exclude pour écarter les homonymes)
python -m veille.main add "Shift Technology" --alias "Shift Tech" --exclude "Shift Technologies"
python -m veille.main add "IA générative assurance" --lang fr

# 2. Lancer la veille (30 derniers jours, tous les sujets)
python -m veille.main run                       # affichage terminal
python -m veille.main run --output html         # rapport HTML dans ~/.veille/rapports/
python -m veille.main run --topic "Shift Technology" --since-days 7 --only-new

# Gérer les sujets
python -m veille.main list
python -m veille.main remove "Shift Technology"

# Démo hors-ligne (données réelles sur Shift Technology, relevées le 01/10/2026)
python -m veille.main run --dry-run --since-days 365
```

Exemple de rapport : [`exemples/rapport_shift_technology.html`](exemples/rapport_shift_technology.html)
(ou [version Markdown](exemples/rapport_shift_technology.md)).

## Ce que fait l'application

1. **Collecte** sur Google News (FR + EN), Bing News (FR + EN) et Hacker News.
   Une source en panne n'arrête pas les autres (elle est signalée dans le rapport).
2. **Filtre par date** (`--since-days`).
3. **Dédoublonnage** : un communiqué repris par 10 médias n'apparaît qu'une fois,
   avec la mention « repris aussi par … ».
4. **Pertinence** : score selon la présence du nom exact / des alias ; les articles contenant
   un terme `--exclude` sont écartés (ex. *Shift Technologies*, le site de voitures d'occasion).
5. **Catégorisation** par mots-clés (modifiables dans `config.py`).
6. **Nouveautés** : un historique SQLite (`~/.veille/history.sqlite`) marque 🆕 les articles
   jamais vus — idéal pour une veille quotidienne.

## Automatiser (tous les matins à 8h)

```cron
0 8 * * * cd /chemin/DataScience-Projects && python -m veille.main run --output html --only-new
```

## Architecture

```
config.py                  ← toutes les constantes (sources, catégories, chemins)
topics.py                  ← gestion des sujets (JSON)
sources/base_source.py     ← interface + format standard d'un article + HTTP
sources/google_news.py | bing_news.py | hacker_news.py
sources/rss_parser.py      ← lecture RSS (xml.etree)
sources/registry.py        ← nom → classe de source
processing/date_filter.py | dedup.py | relevance.py | categorize.py
processing/pipeline.py     ← collecte + enchaînement des traitements
storage/history.py         ← articles déjà vus (SQLite)
output/formatter_*.py      ← terminal | Markdown | HTML | JSON
main.py                    ← CLI (add / list / remove / run)
tests/                     ← mock_data.py + test_veille.py (sans réseau)
```

Ajouter une source : créer `sources/<nom>.py` qui étend `BaseSource`, l'enregistrer dans
`sources/registry.py` et ajouter son nom dans `SOURCE_NAMES` (`config.py`).

Le dossier de données se change avec `export VEILLE_DATA_DIR=/autre/dossier`.

## Tests

```bash
pytest veille/tests/ -v
```
