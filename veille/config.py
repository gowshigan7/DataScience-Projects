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
from urllib.parse import quote_plus

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

# ===========================================================================
# DIGEST IA (commande « digest ») — flux fixes, sans sujet
# ===========================================================================

ATOM_NS = "http://www.w3.org/2005/Atom"
DIGEST_TOPIC_NAME = "Veille IA"           # Nom utilisé pour le rapport et l'historique
DIGEST_DEFAULT_SINCE_DAYS = 1
DIGEST_MAX_PER_FEED = 15

# Groupes affichés dans le rapport (ordre d'affichage)
GROUP_LABS = "Labs & entreprises"
GROUP_PRESS = "Presse (labs sans flux)"
GROUP_RESEARCH = "Recherche"
GROUP_RELEASES = "Releases & outils"
GROUP_COMMUNITY = "Communauté"
GROUP_NEWSLETTERS = "Newsletters"
GROUP_X = "X (via Grok)"
DIGEST_GROUPS = [GROUP_LABS, GROUP_PRESS, GROUP_X, GROUP_NEWSLETTERS, GROUP_RESEARCH,
                 GROUP_RELEASES, GROUP_COMMUNITY]

_GN = GOOGLE_NEWS_RSS_URL + "?hl=en-US&gl=US&ceid=US:en&q="
AI_KEYWORDS = ["ai", "a.i.", "llm", "gpt", "model", "agent", "inference", "training",
               "neural", "machine learning", "deep learning", "transformer", "genai",
               "generative", "openai", "anthropic", "claude", "gemini", "llama", "mistral",
               "deepseek", "qwen", "grok", "copilot", "diffusion", "reasoning", "cuda", "gpu"]

# Flux RSS / Atom. "keywords" (optionnel) = ne garder que les items qui en contiennent un.
DIGEST_FEEDS = [
    {"name": "OpenAI", "group": GROUP_LABS, "url": "https://openai.com/news/rss.xml"},
    {"name": "Google DeepMind", "group": GROUP_LABS, "url": "https://deepmind.google/blog/rss.xml"},
    {"name": "Google AI", "group": GROUP_LABS, "url": "https://blog.google/technology/ai/rss/"},
    {"name": "Google Research", "group": GROUP_LABS, "url": "https://research.google/blog/rss/"},
    {"name": "Microsoft AI", "group": GROUP_LABS, "url": "https://blogs.microsoft.com/ai/feed/"},
    {"name": "Microsoft Research", "group": GROUP_LABS,
     "url": "https://www.microsoft.com/en-us/research/feed/"},
    {"name": "NVIDIA", "group": GROUP_LABS, "url": "https://blogs.nvidia.com/feed/",
     "keywords": AI_KEYWORDS},
    {"name": "NVIDIA Developer", "group": GROUP_LABS, "url": "https://developer.nvidia.com/blog/feed",
     "keywords": AI_KEYWORDS},
    {"name": "Hugging Face", "group": GROUP_LABS, "url": "https://huggingface.co/blog/feed.xml"},
    # Labs sans flux RSS officiel → presse via Google News
    {"name": "Anthropic (presse)", "group": GROUP_PRESS,
     "url": _GN + quote_plus('"Anthropic" OR "Claude AI" when:2d')},
    {"name": "Meta AI (presse)", "group": GROUP_PRESS,
     "url": _GN + quote_plus('"Meta AI" OR "Llama" OR "Meta Superintelligence" when:2d')},
    {"name": "xAI (presse)", "group": GROUP_PRESS, "url": _GN + quote_plus('"xAI" OR "Grok" when:2d')},
    {"name": "Mistral (presse)", "group": GROUP_PRESS, "url": _GN + quote_plus('"Mistral AI" when:2d')},
    {"name": "DeepSeek / Qwen (presse)", "group": GROUP_PRESS,
     "url": _GN + quote_plus('"DeepSeek" OR "Qwen" when:2d')},
    # Recherche
    {"name": "arXiv (cs.AI, cs.CL, cs.LG)", "group": GROUP_RESEARCH,
     "url": "https://rss.arxiv.org/rss/cs.AI+cs.CL+cs.LG"},
]

# Releases GitHub (flux Atom https://github.com/<repo>/releases.atom)
GITHUB_RELEASES_URL = "https://github.com/{repo}/releases.atom"
GITHUB_REPOS = ["anthropics/claude-code", "openai/codex", "google-gemini/gemini-cli",
                "huggingface/transformers", "vllm-project/vllm", "ollama/ollama",
                "modelcontextprotocol/modelcontextprotocol"]
GITHUB_RELEASES_MAX = 3                   # Releases max par dépôt

# Hugging Face Daily Papers
HF_DAILY_PAPERS_URL = "https://huggingface.co/api/daily_papers"
HF_PAPER_URL = "https://huggingface.co/papers/"
HF_PAPERS_MIN_UPVOTES = 5

# Hacker News (stories populaires filtrées par AI_KEYWORDS)
HACKER_NEWS_DIGEST_URL = "https://hn.algolia.com/api/v1/search"
HACKER_NEWS_MIN_POINTS = 100
HACKER_NEWS_DIGEST_HITS = 100

# Reddit (JSON public, repli sur le flux Atom si bloqué)
REDDIT_TOP_JSON_URL = "https://www.reddit.com/r/{sub}/top.json"
REDDIT_TOP_RSS_URL = "https://www.reddit.com/r/{sub}/top/.rss"
REDDIT_BASE_URL = "https://www.reddit.com"
REDDIT_SUBREDDITS = ["LocalLLaMA", "MachineLearning", "OpenAI", "ClaudeAI", "singularity"]
REDDIT_MIN_SCORE = 100
REDDIT_MAX_PER_SUB = 10
REDDIT_PERIOD_DAY = "day"
REDDIT_PERIOD_WEEK = "week"

# Boîte mail (IMAP) — newsletters des expéditeurs choisis
IMAP_HOST = os.environ.get("VEILLE_IMAP_HOST", "imap.gmail.com")
IMAP_USER = os.environ.get("VEILLE_IMAP_USER", "")
IMAP_PASSWORD = os.environ.get("VEILLE_IMAP_PASSWORD", "")   # mot de passe d'application
IMAP_FOLDER = os.environ.get("VEILLE_IMAP_FOLDER", "INBOX")
IMAP_DATE_FORMAT = "%d-%b-%Y"
IMAP_OK_STATUS = "OK"
# Expéditeurs retenus (sous-chaîne de l'adresse ou du domaine). À adapter à vos abonnements.
NEWSLETTER_SENDERS = [s.strip() for s in os.environ.get(
    "VEILLE_NEWSLETTER_SENDERS",
    "tldrnewsletter.com,deeplearning.ai,smol.ai,therundown.ai,bensbites,importai,"
    "lastweekin.ai,alphasignal.ai,interconnects.ai,latent.space").split(",") if s.strip()]
NEWSLETTER_SUMMARY_CHARS = 400
NEWSLETTER_SKIP_LINK_WORDS = ["unsubscribe", "désinscri", "desinscri", "preferences",
                              "manage", "privacy", "mailto:", "twitter.com/intent"]
NEWSLETTER_WEB_VERSION_WORDS = ["view in browser", "view online", "web version",
                                "read online", "voir en ligne", "version web"]

# Grok (xAI) — recherche des posts X des comptes suivis
XAI_API_KEY = os.environ.get("XAI_API_KEY", "")
XAI_RESPONSES_URL = "https://api.x.ai/v1/responses"
GROK_MODEL = os.environ.get("VEILLE_GROK_MODEL", "grok-4-1-fast")
GROK_TIMEOUT_SECONDS = 120
GROK_MAX_HANDLES_PER_CALL = 20            # Limite de l'outil x_search
GROK_MAX_POSTS_PER_CALL = 25
X_POST_URL = "https://x.com/{handle}/status/{id}"
X_HANDLES = [
    # Labs
    "OpenAI", "GoogleDeepMind", "xai", "AnthropicAI", "AIatMeta", "MistralAI", "deepseek_ai",
    "Alibaba_Qwen", "huggingface", "nvidia", "MSFTResearch",
    # Personnes
    "karpathy", "ylecun", "emollick", "sama", "demishassabis", "AndrewYNg", "simonw",
    "swyx", "_akhaliq", "ClementDelangue",
]
GROK_PROMPT = (
    "Search X for the most important posts published by these accounts since {from_date}: "
    "announcements, model releases, research, product launches, notable opinions. Skip "
    "replies and small talk. Answer ONLY with a JSON array (no prose, no code fence) of at "
    "most {max_posts} objects with keys: \"handle\" (without @), \"date\" (YYYY-MM-DD), "
    "\"text\" (the post, or a faithful one-sentence summary in its language), \"url\" "
    "(the post URL)."
)
X_TITLE_CHARS = 140

# Sites à ouvrir à la main (affichés en tête du rapport digest)
MANUAL_LINKS = [
    {"label": "OpenAI — News", "url": "https://openai.com/news/"},
    {"label": "Anthropic — News", "url": "https://www.anthropic.com/news"},
    {"label": "xAI — News", "url": "https://x.ai/news"},
    {"label": "Claude Code — Changelog",
     "url": "https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md"},
    {"label": "Codex — Changelog", "url": "https://developers.openai.com/codex/changelog"},
    {"label": "Cursor — Changelog", "url": "https://cursor.com/changelog"},
    {"label": "Gemini CLI — Releases", "url": "https://github.com/google-gemini/gemini-cli/releases"},
    {"label": "Artificial Analysis", "url": "https://artificialanalysis.ai/"},
]

DIGEST_SOURCE_KINDS = ["feeds", "github", "hf_papers", "hacker_news", "reddit", "browser", "mail", "grok"]
FEED_SUMMARY_MAX_CHARS = 400              # Résumés tronqués (notes de release, abstracts)
ISO_DATE_FORMAT = "%Y-%m-%d"

# ---------------------------------------------------------------------------
# Bot navigateur (Playwright) — sites sans flux ou qui bloquent les requêtes simples
# ---------------------------------------------------------------------------

BROWSER_EXECUTABLE_PATH = os.environ.get("VEILLE_BROWSER_PATH", "") or None  # None = Chromium de Playwright
BROWSER_TIMEOUT_MS = 30000
BROWSER_SETTLE_MS = 1500                  # Attente après chargement (sites en JavaScript)
BROWSER_MIN_TITLE_CHARS = 12              # Liens plus courts ignorés (menus, boutons)
BROWSER_MAX_TITLE_CHARS = 200
BROWSER_PREFERRED_TITLE_CHARS = 25      # Ligne ≥ 25 car. = titre probable (vs « News », date…)
BROWSER_USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/140.0 Safari/537.36")

# Pages lues par le navigateur : liens dont l'URL correspond à link_pattern (regex).
BROWSER_PAGES = [
    {"name": "Anthropic", "group": GROUP_LABS, "url": "https://www.anthropic.com/news",
     "link_pattern": r"anthropic\.com/news/[^/?#]+$"},
    {"name": "xAI", "group": GROUP_LABS, "url": "https://x.ai/news",
     "link_pattern": r"x\.ai/news/[^/?#]+$"},
    {"name": "Meta AI", "group": GROUP_LABS, "url": "https://ai.meta.com/blog/",
     "link_pattern": r"ai\.meta\.com/blog/[^/?#]+/?$"},
    {"name": "Mistral AI", "group": GROUP_LABS, "url": "https://mistral.ai/news",
     "link_pattern": r"mistral\.ai/news/[^/?#]+$"},
    {"name": "Qwen", "group": GROUP_LABS, "url": "https://qwenlm.github.io/blog/",
     "link_pattern": r"qwenlm\.github\.io/blog/[^/?#]+/?$"},
    {"name": "Cursor changelog", "group": GROUP_RELEASES, "url": "https://cursor.com/changelog",
     "link_pattern": r"cursor\.com/changelog/[^/?#]+$"},
]

# Secours navigateur des flux RSS : page HTML à lire si le flux échoue ou est vide.
FEED_BROWSER_FALLBACKS = {
    "OpenAI": {"url": "https://openai.com/news/", "link_pattern": r"openai\.com/index/[^/?#]+/?$"},
    "Google DeepMind": {"url": "https://deepmind.google/discover/blog/",
                        "link_pattern": r"deepmind\.google/discover/blog/[^/?#]+/?$"},
    "Hugging Face": {"url": "https://huggingface.co/blog",
                     "link_pattern": r"huggingface\.co/blog/[^/?#]+$"},
}
REDDIT_BROWSER_URL = "https://old.reddit.com/r/{sub}/top/?t={period}"
REDDIT_BROWSER_LINK_PATTERN = r"reddit\.com/r/{sub}/comments/"

# ---------------------------------------------------------------------------
# Diagnostic des sources (commande « check »)
# ---------------------------------------------------------------------------

CHECK_SAMPLE_CHARS = 60
CHECK_ERROR_CHARS = 140
CHECK_DEFAULT_SINCE_DAYS = 7
CHECK_STATUS_OK = "OK"
CHECK_STATUS_EMPTY = "VIDE"
CHECK_STATUS_ERROR = "ERREUR"
CHECK_STATUS_SKIPPED = "NON CONFIGURÉ"
