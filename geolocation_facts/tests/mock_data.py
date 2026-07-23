"""
mock_data.py
============
Feature : Données fictives pour les tests (mode dry-run).

Description :
    Ce module fournit un jeu de fun facts statiques géolocalisés autour de Paris.
    Ces données sont utilisées dans les tests unitaires et le mode dry-run pour
    éviter toute consommation d'API réelle.

    Aucun appel réseau n'est effectué lors de l'import ou de l'utilisation de ce module.
    Les données couvrent des distances variées (dont un point hors rayon 5 km) afin
    de tester le filtre de distance, ainsi que des mots-clés variés pour le filtre
    par mot-clé.

Cas d'usage :
    - Mode --dry-run : python -m geolocation_facts.main --location "Paris" --dry-run
    - Tests unitaires : import direct dans test_filters.py, test_source.py
    - Démo : montrer l'outil sans connexion réseau

Entrée  : Aucune (données statiques)
Sortie  : MOCK_FACTS — List[dict] de fun facts au format standardisé
"""

# Point de référence : Tour Eiffel, Paris
MOCK_REFERENCE_LAT = 48.8584
MOCK_REFERENCE_LNG = 2.2945

MOCK_FACTS: list[dict] = [
    {
        "id": "wikipedia_fr_1",
        "title": "Tour Eiffel",
        "fact": "La Tour Eiffel est une tour de fer puddlé de 330 metres de hauteur "
                "construite par Gustave Eiffel pour l'Exposition universelle de 1889.",
        "latitude": 48.8584,
        "longitude": 2.2945,
        "distance_m": 15.0,
        "category": None,
        "url": "https://fr.wikipedia.org/?curid=1",
        "source": "wikipedia",
    },
    {
        "id": "wikipedia_fr_2",
        "title": "Champ-de-Mars",
        "fact": "Le Champ-de-Mars est un vaste jardin public parisien situe entre "
                "la Tour Eiffel et l'Ecole militaire.",
        "latitude": 48.8556,
        "longitude": 2.2986,
        "distance_m": 470.0,
        "category": None,
        "url": "https://fr.wikipedia.org/?curid=2",
        "source": "wikipedia",
    },
    {
        "id": "wikipedia_fr_3",
        "title": "Palais de Chaillot",
        "fact": "Le Palais de Chaillot, construit pour l'Exposition de 1937, abrite "
                "plusieurs musees dont le musee de l'Homme.",
        "latitude": 48.8623,
        "longitude": 2.2885,
        "distance_m": 640.0,
        "category": None,
        "url": "https://fr.wikipedia.org/?curid=3",
        "source": "wikipedia",
    },
    {
        "id": "wikipedia_fr_4",
        "title": "Les Invalides",
        "fact": "L'Hotel des Invalides fut fonde par Louis XIV en 1670 pour accueillir "
                "les soldats invalides ; il abrite le tombeau de Napoleon Ier.",
        "latitude": 48.8566,
        "longitude": 2.3126,
        "distance_m": 1330.0,
        "category": None,
        "url": "https://fr.wikipedia.org/?curid=4",
        "source": "wikipedia",
    },
    {
        "id": "wikipedia_fr_5",
        "title": "Arc de triomphe",
        "fact": "L'Arc de triomphe de l'Etoile, commande par Napoleon en 1806, "
                "domine la place Charles-de-Gaulle au bout des Champs-Elysees.",
        "latitude": 48.8738,
        "longitude": 2.2950,
        "distance_m": 1710.0,
        "category": None,
        "url": "https://fr.wikipedia.org/?curid=5",
        "source": "wikipedia",
    },
    {
        "id": "wikipedia_fr_6",
        "title": "Musee du Louvre",
        "fact": "Le musee du Louvre est le plus grand musee d'art du monde ; "
                "il expose notamment la Joconde de Leonard de Vinci.",
        "latitude": 48.8606,
        "longitude": 2.3376,
        "distance_m": 3180.0,
        "category": None,
        "url": "https://fr.wikipedia.org/?curid=6",
        "source": "wikipedia",
    },
    {
        "id": "wikipedia_fr_7",
        "title": "Cathedrale Notre-Dame de Paris",
        "fact": "Notre-Dame de Paris est une cathedrale gothique dont la construction "
                "debuta en 1163 ; elle fut ravagee par un incendie en 2019.",
        "latitude": 48.8530,
        "longitude": 2.3499,
        "distance_m": 4090.0,
        "category": None,
        "url": "https://fr.wikipedia.org/?curid=7",
        "source": "wikipedia",
    },
    {
        "id": "wikipedia_fr_8",
        "title": "Basilique du Sacre-Coeur",
        "fact": "La basilique du Sacre-Coeur, au sommet de la butte Montmartre, "
                "fut edifiee entre 1875 et 1914 en pierre de Chateau-Landon.",
        "latitude": 48.8867,
        "longitude": 2.3431,
        "distance_m": 5800.0,  # Hors rayon 5 km depuis la Tour Eiffel
        "category": None,
        "url": "https://fr.wikipedia.org/?curid=8",
        "source": "wikipedia",
    },
]
