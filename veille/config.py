"""
config.py
=========
Fichier centralisé de configuration de l'application de veille.

Description :
    Contient TOUTES les constantes et paramètres configurables de l'outil.
    Aucune valeur ne doit être codée en dur ailleurs dans le projet.

Cas d'usage :
    - Ajouter / retirer une source d'information
    - Modifier les catégories et leurs mots-clés
    - Changer les chemins des fichiers (sujets, historique, rapports)

Entrée  : Aucune (fichier de constantes)
Sortie  : Variables importées par les autres modules
"""

import os

# ---------------------------------------------------------------------------
# Fichiers et dossiers (dans ~/.veille par défaut, surchargeable par variable d'env)
# ---------------------------------------------------------------------------

DATA_DIR = os.environ.get("VEILLE_DATA_DIR", os.path.join(os.path.expanduser("~"), ".veille"))
TOPICS_FILE = os.path.join(DATA_DIR, "topics.json")
HISTORY_DB = os.path.join(DATA_DIR, "history.sqlite")
REPORTS_DIR = os.path.join(DATA_DIR, "rapports")

# ---------------------------------------------------------------------------
# Paramètres de collecte
# ---------------------------------------------------------------------------

DEFAULT_LANGUAGES = ["fr", "en"]      # Langues interrogées par défaut
DEFAULT_SINCE_DAYS = 30               # Fenêtre temporelle par défaut (jours)
DEFAULT_MAX_PER_SOURCE = 30           # Nombre max d'articles par source et par langue
HTTP_TIMEOUT_SECONDS = 15
HTTP_USER_AGENT = "Mozilla/5.0 (compatible; veille-bot/1.0)"
SECONDS_PER_DAY = 86400
MIN_RELEVANCE_SCORE = 1               # Score minimal pour garder un article

# ---------------------------------------------------------------------------
# Sources (toutes gratuites, sans clé API)
# ---------------------------------------------------------------------------

GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search"
GOOGLE_NEWS_LOCALES = {
    "fr": {"hl": "fr", "gl": "FR", "ceid": "FR:fr"},
    "en": {"hl": "en-US", "gl": "US", "ceid": "US:en"},
}
BING_NEWS_RSS_URL = "https://www.bing.com/news/search"
BING_NEWS_MARKETS = {"fr": "fr-FR", "en": "en-US"}
HACKER_NEWS_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"
HACKER_NEWS_ITEM_URL = "https://news.ycombinator.com/item?id="

SOURCE_NAMES = ["google_news", "bing_news", "hacker_news"]
DEFAULT_SOURCES = ["google_news", "bing_news", "hacker_news"]

# ---------------------------------------------------------------------------
# Pertinence
# ---------------------------------------------------------------------------

SCORE_EXACT_IN_TITLE = 3              # Nom exact du sujet dans le titre
SCORE_EXACT_IN_SUMMARY = 2            # Nom exact du sujet dans le résumé
SCORE_ALIAS_MATCH = 1                 # Un alias trouvé (titre ou résumé)

# ---------------------------------------------------------------------------
# Catégories (premier match gagnant, ordre = priorité)
# ---------------------------------------------------------------------------

DEFAULT_CATEGORY = "Autre"
CATEGORY_KEYWORDS = {
    "Levée de fonds / Finance": ["levée", "lève", "funding", "raises", "series", "valuation",
                                 "valorisation", "investisseur", "investor", "ipo", "acquisition",
                                 "acquires", "rachète", "rachat", "revenue", "chiffre d'affaires"],
    "Partenariat / Client": ["partenariat", "partenaire", "partnership", "partner", "renews",
                             "renouvellement", "renewal", "collaboration", "choisit", "selects",
                             "chooses", "chose", "signs", "signe", "deploys", "déploie"],
    "Nomination / RH": ["nomme", "nomination", "appoints", "appointed", "names", "hires",
                        "recrute", "chief", "ceo", "cto", "cfo", "directeur", "directrice",
                        "layoffs", "licenciement"],
    "Produit / Innovation": ["lance", "launch", "launches", "nouvelle solution", "new solution",
                             "agentic", "agent", "product", "produit", "release", "genai",
                             "ia générative", "generative ai", "platform", "plateforme"],
    "Prix / Classement": ["award", "prix", "récompense", "wins", "remporte", "classement",
                          "ranking", "leader", "gartner", "forrester", "celent"],
    "Événement": ["conférence", "conference", "salon", "summit", "webinar", "webinaire",
                  "itc", "vivatech", "keynote"],
}

# ---------------------------------------------------------------------------
# Sorties
# ---------------------------------------------------------------------------

OUTPUT_FORMATS = ["terminal", "markdown", "html", "json"]
DEFAULT_OUTPUT_FORMAT = "terminal"
REPORT_FILE_EXTENSIONS = {"markdown": "md", "html": "html", "json": "json"}
TERMINAL_TITLE_WIDTH = 90
NEW_BADGE = "🆕"
DATE_DISPLAY_FORMAT = "%d/%m/%Y"
GENERATED_AT_FORMAT = "%d/%m/%Y %H:%M"
REPORT_STEM_FORMAT = "veille_%Y-%m-%d_%H%M"
