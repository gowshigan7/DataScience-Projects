"""
mock_data.py
============
Feature : Données de démonstration pour --dry-run et les tests.

Description :
    Articles réels sur Shift Technology (relevés par recherche web le 01/10/2026),
    plus du « bruit » volontaire pour montrer le nettoyage :
    - doublons (même communiqué repris par plusieurs médias)
    - homonyme « Shift Technologies » (site de voitures d'occasion, à exclure)
    - articles anciens (hors fenêtre temporelle)
    Les dates inconnues sont à None (non inventées).

Cas d'usage :
    - python -m veille.main run --dry-run
    - tests unitaires

Entrée  : Aucune
Sortie  : MOCK_TOPIC (dict), MOCK_ARTICLES (list[dict]), MOCK_NOW (datetime)
"""

from datetime import datetime, timezone

MOCK_NOW = datetime(2026, 10, 1, tzinfo=timezone.utc)

MOCK_TOPIC = {
    "name": "Shift Technology",
    "aliases": ["Shift Tech"],
    "exclude": ["Shift Technologies"],
    "languages": ["fr", "en"],
}


def _art(title, url, source, publisher, published, summary="", language="en"):
    """
    Construit un article mocké au format standard.

    Args:
        title (str): Titre.
        url (str): Lien.
        source (str): Nom de la source.
        publisher (str): Média.
        published (datetime | None): Date UTC.
        summary (str): Extrait.
        language (str): Langue.

    Returns:
        dict: Article standardisé.
    """
    return {"title": title, "url": url, "source": source, "publisher": publisher,
            "published": published, "summary": summary, "language": language}


def _d(y, m, d):
    """
    Raccourci de date UTC.

    Args:
        y (int): Année.
        m (int): Mois.
        d (int): Jour.

    Returns:
        datetime: Date UTC.
    """
    return datetime(y, m, d, tzinfo=timezone.utc)


MOCK_ARTICLES = [
    _art("Five-Year Renewal of Collaboration between Shift Technology and AXA to accelerate "
         "AI-Powered Insurance Transformation",
         "https://www.prnewswire.com/news-releases/five-year-renewal-of-collaboration-between-"
         "shift-technology-and-axa-to-accelerate-ai-powered-insurance-transformation-302704516.html",
         "google_news", "PR Newswire", _d(2026, 3, 5)),
    _art("Five-Year Renewal of Collaboration between Shift Technology and AXA to accelerate "
         "AI-Powered Insurance Transformation",
         "https://www.nasdaq.com/press-release/five-year-renewal-collaboration-between-shift-"
         "technology-and-axa-accelerate-ai",
         "bing_news", "Nasdaq", _d(2026, 3, 5),
         "Shift Technology and AXA renew their strategic partnership for five years; the "
         "collaboration, started in 2016, now spans 15 countries across Europe, Asia and Latin "
         "America and covers claims, fraud detection and underwriting."),
    _art("AXA renews partnership with Shift Technology",
         "https://www.itij.com/latest/news/axa-renews-partnership-shift-technology",
         "bing_news", "ITIJ", None),
    _art("Covéa chooses Shift Technology as strategic partner for fraud and risk management",
         "https://www.shift-technology.com/resources/news/covéa-chooses-shift-technology-as-"
         "strategic-partner-for-fraud-and-risk-management",
         "google_news", "Shift Technology", _d(2026, 3, 31),
         "Covéa selects Shift Technology as a long-term partner to get a consistent, shared "
         "view of risk from policy inception through to claims settlement.", "fr"),
    _art("Covéa chooses Shift Technology as strategic partner for fraud and risk management",
         "https://digital-release.kxan.com/business/press-releases/cision/20260331NE22569/"
         "covea-chooses-shift-technology-as-strategic-partner-for-fraud-and-risk-management",
         "bing_news", "Cision", _d(2026, 3, 31)),
    _art("Shift Technology and Covéa shortlisted for Counter Fraud Innovation of the Year – "
         "Insurance Times Tech & Innovation Awards 2026",
         "https://www.shift-technology.com/en-gb/resources/events/tech-innovation-awards-2026",
         "google_news", "Shift Technology", None,
         "Ceremony on Thursday 17 September 2026 at the Royal Lancaster, London."),
    _art("Shift Technology at ITC Vegas 2026",
         "https://www.shift-technology.com/resources/events",
         "google_news", "Shift Technology", None,
         "Shift Technology sponsors and exhibits at ITC Vegas, 29 September – 1 October 2026, "
         "Las Vegas."),
    # --- Bruit : homonyme à exclure
    _art("Shift Technologies (online marketplace)",
         "https://en.wikipedia.org/wiki/Shift_Technologies_(online_marketplace)",
         "bing_news", "Wikipedia", _d(2026, 8, 1),
         "Shift Technologies was an online used car marketplace."),
    # --- Bruit : articles anciens (hors fenêtre de 365 jours)
    _art("Le spécialiste en détection de fraude Shift Technology lève 220 M$",
         "https://www.lemondeinformatique.fr/actualites/lire-le-specialiste-en-detection-de-"
         "fraude-shift-technology-leve-220m$-82847.html",
         "google_news", "Le Monde Informatique", _d(2021, 5, 4),
         "Tour de table mené par Advent International ; valorisation d'un milliard de dollars.",
         "fr"),
    _art("Guidewire names Shift its strategic partner to help mitigate insurance fraud",
         "https://www.guidewire.com/about/press-center/press-releases/20241112/guidewire-names-"
         "shift-its-strategic-partner-to-help-mitigate-insurance-fraud",
         "bing_news", "Guidewire", _d(2024, 11, 12),
         "Guidewire announced Shift Technology as its strategic partner for insurance-based "
         "decisioning solutions."),
]
