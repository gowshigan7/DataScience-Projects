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

## Digest IA quotidien (`digest`)

Une seconde commande, sans sujet : elle agrège des **flux fixes** sur l'IA dans un seul rapport.

| Groupe | Sources | Comment |
|---|---|---|
| Labs & entreprises | OpenAI, Google DeepMind, Google AI, Google Research, Microsoft AI & Research, NVIDIA (filtré IA), Hugging Face | flux RSS officiels |
| Presse (labs sans flux) | Anthropic, Meta AI, xAI, Mistral, DeepSeek / Qwen | Google News RSS |
| X (via Grok) | OpenAI, DeepMind, xAI, Anthropic, Meta, Mistral, DeepSeek, Qwen, HF, NVIDIA + Karpathy, LeCun, Mollick, Altman, Hassabis, Ng, Willison… | API xAI, outil `x_search` (`XAI_API_KEY`) |
| Newsletters | expéditeurs choisis de **votre** boîte mail | IMAP en lecture seule |
| Recherche | HF Daily Papers (≥ 5 votes), arXiv cs.AI / cs.CL / cs.LG | API JSON + RSS |
| Releases & outils | claude-code, codex, gemini-cli, transformers, vllm, ollama, MCP | flux Atom des releases GitHub |
| Communauté | Hacker News (≥ 100 points, sujets IA), Reddit (LocalLLaMA, MachineLearning, OpenAI, ClaudeAI, singularity) | API Algolia, JSON Reddit (repli RSS) |
| À ouvrir à la main | news OpenAI / Anthropic / xAI, changelogs Claude Code / Codex / Cursor / Gemini CLI, Artificial Analysis | liens en tête du rapport |

```bash
python -m veille.main digest                              # dernières 24 h, terminal
python -m veille.main digest --output html --only-new     # rapport HTML des nouveautés
python -m veille.main digest --since-days 7 --skip grok mail
python -m veille.main digest --dry-run                    # démo hors-ligne (données fictives)
```

Exemple de mise en page : [`exemples/digest_ia_demo.html`](exemples/digest_ia_demo.html) (données « [Démo] »).

### Configuration (variables d'environnement)

```bash
# Boîte mail — Gmail : validation en 2 étapes + « mot de passe d'application »
export VEILLE_IMAP_HOST="imap.gmail.com"
export VEILLE_IMAP_USER="vous@gmail.com"
export VEILLE_IMAP_PASSWORD="xxxx xxxx xxxx xxxx"
export VEILLE_IMAP_FOLDER="INBOX"                # ou un libellé, ex. "Newsletters"
export VEILLE_NEWSLETTER_SENDERS="deeplearning.ai,tldrnewsletter.com,smol.ai"

# X via Grok (payant à l'usage ; 1 appel par paquet de 20 comptes)
export XAI_API_KEY="xai-..."
export VEILLE_GROK_MODEL="grok-4-1-fast"         # à adapter au modèle xAI disponible
```

Sans ces variables, la boîte mail et X sont simplement ignorés (c'est indiqué dans le rapport).
Les e-mails sont lus en lecture seule et ne sont **pas** marqués comme lus.
Flux, dépôts GitHub, subreddits, comptes X et liens manuels se modifient dans `config.py`
(`DIGEST_FEEDS`, `GITHUB_REPOS`, `REDDIT_SUBREDDITS`, `X_HANDLES`, `MANUAL_LINKS`).

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
5 8 * * * cd /chemin/DataScience-Projects && python -m veille.main digest --output html --only-new
```

## Architecture

```
config.py                  ← toutes les constantes (sources, catégories, chemins)
topics.py                  ← gestion des sujets (JSON)
sources/base_source.py     ← interface + format standard d'un article + HTTP
sources/google_news.py | bing_news.py | hacker_news.py
sources/rss_parser.py      ← lecture RSS (xml.etree)
sources/registry.py        ← nom → classe de source (veille par sujet)
sources/feed_rss.py | hf_papers.py | hn_top.py | reddit.py   ← digest IA
sources/mailbox.py + newsletter_parser.py                     ← newsletters IMAP
sources/grok_x.py          ← posts X via l'API xAI (x_search)
sources/digest_registry.py ← assemble les sources du digest
processing/date_filter.py | dedup.py | relevance.py | categorize.py
processing/pipeline.py     ← collecte + enchaînement des traitements
processing/digest_pipeline.py ← date + doublons + tri (digest)
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
