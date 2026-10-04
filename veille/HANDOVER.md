# Handover — `veille/` (tests sur machine locale)

Branche : `ccr-20c118e9-jyqcbi` · dernier commit : `b1e300c`
Contexte : développé dans une session cloud dont le réseau bloquait presque tous les sites.
**Aucune source réelle n'a pu être validée, sauf le flux Microsoft Research (10 articles OK).**
Le but de cette étape : faire tourner l'app sur une vraie connexion et corriger ce qui casse.

## 1. Installation (5 min)

```bash
git clone https://github.com/gowshigan7/DataScience-Projects.git
cd DataScience-Projects
git checkout ccr-20c118e9-jyqcbi
python3 -m venv .venv && source .venv/bin/activate   # Windows : .venv\Scripts\activate
pip install pytest playwright
playwright install chromium
```

Python 3.9+. L'app n'utilise que la bibliothèque standard ; Playwright est optionnel (bot navigateur).

## 2. Vérifier que tout est sain (hors-ligne)

```bash
pytest veille/tests/ -v                 # attendu : 59 passed (le test Chromium tourne si installé)
pytest restaurant_scraper/tests/ -q     # attendu : 89 passed
python -m veille.main digest --dry-run
python -m veille.main run --dry-run --since-days 365
```

## 3. Plan de test réel — dans cet ordre

| # | Commande | Ce qu'on vérifie |
|---|---|---|
| 1 | `python -m veille.main check` | **Le plus important.** Statut de chaque source (OK / VIDE / ERREUR), nb d'items, secours navigateur utilisé ou non |
| 2 | `python -m veille.main check --skip browser` | Ce qui passe sans navigateur (voie la plus simple) |
| 3 | `python -m veille.main digest --since-days 2 --output html` | Rapport réel → ouvrir le fichier HTML indiqué (`~/.veille/rapports/`) |
| 4 | `python -m veille.main digest --since-days 2` (2e fois) | Les 🆕 doivent avoir disparu (historique SQLite) |
| 5 | `python -m veille.main add "Shift Technology" --alias "Shift Tech" --exclude "Shift Technologies"` puis `python -m veille.main run --output html` | Veille par sujet (Google News, Bing News, Hacker News) |
| 6 | Boîte mail (optionnel) : variables ci-dessous puis `python -m veille.main check --only mailbox` | Newsletters lues, sans les marquer comme lues |
| 7 | Grok (optionnel, payant) : `XAI_API_KEY` puis `python -m veille.main check --only grok` | Posts X des comptes suivis |

```bash
# Gmail : validation en 2 étapes + « mot de passe d'application »
export VEILLE_IMAP_USER="vous@gmail.com"
export VEILLE_IMAP_PASSWORD="xxxx xxxx xxxx xxxx"
export VEILLE_IMAP_FOLDER="INBOX"                       # ou un libellé
export VEILLE_NEWSLETTER_SENDERS="deeplearning.ai,tldrnewsletter.com,smol.ai"
export XAI_API_KEY="xai-..."
export VEILLE_GROK_MODEL="grok-4-1-fast"                # vérifier le nom du modèle sur docs.x.ai
```

**À renvoyer** : la sortie complète de `check` (étape 1) + une capture du rapport HTML (étape 3).

## 4. Points incertains — à surveiller en priorité

| Zone | Risque | Où corriger |
|---|---|---|
| URLs des flux RSS (labs) | Jamais testées en réel ; certaines peuvent avoir bougé | `DIGEST_FEEDS` dans `veille/config.py` |
| Bot navigateur | `link_pattern` écrits sans voir les pages réelles → risque `VIDE` | `BROWSER_PAGES`, `FEED_BROWSER_FALLBACKS` |
| Reddit | JSON souvent bloqué sans compte → repli RSS puis old.reddit.com | `sources/reddit.py`, `REDDIT_*` |
| Grok / xAI | Format de l'API Responses + outil `x_search` déduit de docs secondaires ; nom du modèle incertain | `sources/grok_x.py` (`extract_output`, `parse_posts`), `GROK_*` |
| Titres du bot | Heuristique (1re ligne ≥ 25 car.) peut prendre une catégorie/date pour un titre | `select_article_links` dans `sources/browser_page.py` |
| Hacker News digest | Filtre mots-clés IA (`AI_KEYWORDS`) peut laisser passer du bruit ou en rater | `config.py` |
| Google News | Liens = redirections `news.google.com/...` (pas l'URL finale) | — (connu, acceptable) |

Si une source affiche `VIDE` avec le navigateur : ouvrir la page, copier l'URL d'un article,
et adapter le `link_pattern` (regex sur l'URL) pour qu'il la reconnaisse.

## 5. Architecture en bref

```
veille/
  main.py                    CLI : add | list | remove | run | digest | check
  config.py                  TOUTES les constantes (sources, comptes X, catégories, chemins)
  topics.py                  sujets suivis (~/.veille/topics.json)
  sources/
    base_source.py           interface BaseSource + format article + HTTP
    google_news.py bing_news.py hacker_news.py        veille par sujet
    feed_rss.py hf_papers.py hn_top.py reddit.py      digest IA
    mailbox.py newsletter_parser.py                   newsletters IMAP
    grok_x.py                                         X via xAI
    browser_page.py fallback.py                       bot Playwright + secours auto
    registry.py digest_registry.py                    assemblage des sources
  processing/                date, doublons, pertinence, catégories, pipelines
  storage/history.py         articles déjà vus (~/.veille/history.sqlite)
  output/                    terminal | markdown | html | json
  diagnostics/source_check.py  commande check
  tests/                     mock_data, mock_digest, 3 fichiers de tests (sans réseau)
  exemples/                  rapport Shift Technology (réel) + digest de démo
```

Conventions du dépôt (voir `CLAUDE.md` et `.claude/rules/`) : constantes uniquement dans
`config.py`, docstrings module (Description / Cas d'usage / Entrée / Sortie) et fonctions
(Args / Returns), une fonctionnalité par fichier, `--dry-run` = aucun réseau ni fichier écrit,
commits `feat:` / `fix:` …

## 6. Prochaines étapes envisagées

1. Corriger les sources KO d'après la sortie de `check`.
2. Résumé automatique du digest par un LLM (ex. « les 5 infos du jour »).
3. Planification quotidienne (cron / Planificateur de tâches) + envoi du rapport par e-mail.
4. Ouvrir une PR une fois les sources validées (diff actuel ≈ 3 000 lignes : à découper si besoin).

## Prompt de reprise (Claude Code sur la machine locale)

> Lis `veille/HANDOVER.md`. Lance `python -m veille.main check`, analyse les sources en
> ERREUR ou VIDE, corrige-les une par une (URL de flux, `link_pattern`, parsing), relance
> `check` après chaque correction, puis fais tourner les tests et commite.
