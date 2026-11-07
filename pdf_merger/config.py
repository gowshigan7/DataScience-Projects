"""
config.py
=========
Fichier centralisé de configuration de l'application pdf_merger.

Description :
    Contient TOUTES les constantes et textes configurables de l'outil.
    Aucune valeur ne doit être codée en dur ailleurs dans le projet.

Cas d'usage :
    - Changer le nom du fichier de sortie proposé par défaut
    - Modifier la taille ou le titre de la fenêtre
    - Traduire les messages de l'interface

Entrée  : Aucune (fichier de constantes)
Sortie  : Variables importées par les autres modules
"""

# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

APP_NAME = "PDF Merger"
APP_VERSION = "1.0.0"
DEFAULT_OUTPUT_NAME = "fusion.pdf"
PDF_EXTENSION = ".pdf"

# ---------------------------------------------------------------------------
# Plages de pages  (ex. "1-3, 5, 8-")
# ---------------------------------------------------------------------------

RANGE_SEPARATOR = ","
RANGE_DASH = "-"
ALL_PAGES_LABEL = "toutes"

# ---------------------------------------------------------------------------
# Interface graphique (Tkinter)
# ---------------------------------------------------------------------------

WINDOW_TITLE = f"{APP_NAME} {APP_VERSION}"
WINDOW_GEOMETRY = "820x480"
WINDOW_MIN_SIZE = (640, 360)
UI_PADDING = 8
POLL_INTERVAL_MS = 100
PYPDF_LOG_LEVEL = "ERROR"          # masque les avertissements pypdf sur les PDF abîmés

COLUMNS = ("fichier", "pages", "plage", "dossier")
COLUMN_HEADERS = {
    "fichier": "Fichier",
    "pages": "Pages",
    "plage": "Pages à garder",
    "dossier": "Dossier",
}
COLUMN_WIDTHS = {"fichier": 220, "pages": 60, "plage": 120, "dossier": 360}

FILE_DIALOG_TYPES = [("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")]

BTN_ADD = "Ajouter des PDF…"
BTN_REMOVE = "Retirer"
BTN_UP = "▲ Monter"
BTN_DOWN = "▼ Descendre"
BTN_SORT = "Trier A→Z"
BTN_CLEAR = "Tout vider"
BTN_RANGE = "Choisir les pages…"
BTN_MERGE = "Fusionner"
CHK_BOOKMARKS = "Ajouter un signet par fichier"

MSG_READY = "Ajoutez des PDF (bouton ou glisser-déposer), ordonnez-les, puis cliquez sur Fusionner."
MSG_READY_NO_DND = "Ajoutez des PDF avec le bouton, ordonnez-les, puis cliquez sur Fusionner."
MSG_NEED_FILES = "Ajoutez au moins un fichier PDF."
MSG_MERGING = "Fusion en cours…"
MSG_DONE = "Fusion terminée : {pages} pages → {path}"
MSG_ERROR_TITLE = "Erreur"
MSG_DONE_TITLE = "Terminé"
MSG_RANGE_PROMPT = (
    "Pages à garder pour « {name} » ({count} pages)\n"
    "Exemples : 1-3, 5, 8-   (vide = toutes)"
)
MSG_SKIPPED = "Ignorés (pas des PDF valides) :\n{files}"

# ---------------------------------------------------------------------------
# Messages d'erreur du moteur de fusion
# ---------------------------------------------------------------------------

ERR_NO_INPUT = "Aucun fichier PDF à fusionner."
ERR_NOT_FOUND = "Fichier introuvable : {path}"
ERR_NOT_PDF = "Ce fichier n'est pas un PDF lisible : {path}"
ERR_ENCRYPTED = "PDF protégé par mot de passe : {path}"
ERR_OUTPUT_IS_INPUT = "Le fichier de sortie ne peut pas être l'un des fichiers d'entrée : {path}"
ERR_BAD_RANGE = "Plage de pages invalide : « {spec} »"
ERR_RANGE_OUT = "Page {page} hors limites (le document a {count} pages)"
ERR_EMPTY_RESULT = "Aucune page sélectionnée : le PDF de sortie serait vide."
