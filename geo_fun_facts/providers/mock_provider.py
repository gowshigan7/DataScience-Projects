"""
mock_provider.py
=================
Feature : Fournisseur de fun facts statiques (aucun appel réseau).

Description :
    Ce module fournit un jeu de données statiques de fun facts géolocalisés
    autour de lieux célèbres dans le monde. Aucun appel réseau n'est effectué :
    c'est la source par défaut, utilisée pour les démonstrations et les tests.

    Le fournisseur filtre les fun facts dans le rayon demandé autour du point
    de recherche, les trie par distance croissante et applique la limite.

Cas d'usage :
    - Source par défaut : get_fun_facts("Paris", source="mock")
    - Tests unitaires : aucune consommation d'API, résultats déterministes
    - Démo hors-ligne de l'application

Entrée  : float (lat), float (lng), float (radius_km), int (limit)
Sortie  : List[dict] — fun facts au format standardisé FactProvider
"""

from geo_fun_facts.geo.geolocation import calculate_distance_km
from geo_fun_facts.providers.base_provider import FactProvider

MOCK_FUN_FACTS: list[dict] = [
    {
        "id": "mock_001",
        "title": "Tour Eiffel",
        "fact": "La Tour Eiffel grandit d'environ 15 cm en été à cause de la dilatation du fer sous la chaleur.",
        "category": "science",
        "latitude": 48.8584,
        "longitude": 2.2945,
    },
    {
        "id": "mock_002",
        "title": "Big Ben",
        "fact": "Big Ben est en réalité le nom de la cloche, pas de la tour elle-même, officiellement appelée Elizabeth Tower.",
        "category": "histoire",
        "latitude": 51.5007,
        "longitude": -0.1246,
    },
    {
        "id": "mock_003",
        "title": "Colisée de Rome",
        "fact": "Le Colisée pouvait être inondé pour simuler des batailles navales appelées naumachies.",
        "category": "histoire",
        "latitude": 41.8902,
        "longitude": 12.4922,
    },
    {
        "id": "mock_004",
        "title": "Statue de la Liberté",
        "fact": "La Statue de la Liberté était à l'origine de couleur cuivre brillant avant de virer au vert par oxydation.",
        "category": "science",
        "latitude": 40.6892,
        "longitude": -74.0445,
    },
    {
        "id": "mock_005",
        "title": "Christ Rédempteur",
        "fact": "Le Christ Rédempteur de Rio a déjà été frappé par la foudre plusieurs fois, y compris en 2014.",
        "category": "insolite",
        "latitude": -22.9519,
        "longitude": -43.2105,
    },
    {
        "id": "mock_006",
        "title": "Grande Muraille de Chine",
        "fact": "Contrairement à une légende répandue, la Grande Muraille de Chine n'est pas visible à l'œil nu depuis l'espace.",
        "category": "insolite",
        "latitude": 40.4319,
        "longitude": 116.5704,
    },
    {
        "id": "mock_007",
        "title": "Opéra de Sydney",
        "fact": "Le toit de l'Opéra de Sydney est recouvert de plus d'un million de tuiles en céramique.",
        "category": "culture",
        "latitude": -33.8568,
        "longitude": 151.2153,
    },
    {
        "id": "mock_008",
        "title": "Taj Mahal",
        "fact": "Le Taj Mahal change de couleur selon l'heure de la journée : rosé le matin, blanc l'après-midi, doré au clair de lune.",
        "category": "nature",
        "latitude": 27.1751,
        "longitude": 78.0421,
    },
    {
        "id": "mock_009",
        "title": "Mont Everest",
        "fact": "Le sommet de l'Everest continue de grandir de quelques millimètres par an sous l'effet de la tectonique des plaques.",
        "category": "record",
        "latitude": 27.9881,
        "longitude": 86.9250,
    },
    {
        "id": "mock_010",
        "title": "Machu Picchu",
        "fact": "Le Machu Picchu a été construit sans mortier : les pierres s'emboîtent si précisément qu'on ne peut pas glisser une lame entre elles.",
        "category": "histoire",
        "latitude": -13.1631,
        "longitude": -72.5450,
    },
    {
        "id": "mock_011",
        "title": "Chutes du Niagara",
        "fact": "Les chutes du Niagara reculent d'environ 30 cm par an à cause de l'érosion.",
        "category": "nature",
        "latitude": 43.0962,
        "longitude": -79.0377,
    },
    {
        "id": "mock_012",
        "title": "Grand Canyon",
        "fact": "Le Grand Canyon mesure jusqu'à 29 km de large et a mis environ 5 à 6 millions d'années à se former.",
        "category": "record",
        "latitude": 36.1069,
        "longitude": -112.1129,
    },
    {
        "id": "mock_013",
        "title": "Mont Blanc",
        "fact": "L'altitude du Mont Blanc varie légèrement chaque année selon l'épaisseur de la couche de neige et de glace au sommet.",
        "category": "science",
        "latitude": 45.8326,
        "longitude": 6.8652,
    },
    {
        "id": "mock_014",
        "title": "Sahara",
        "fact": "Le Sahara était une savane verdoyante et humide il y a environ 6000 ans, avant de devenir le désert actuel.",
        "category": "nature",
        "latitude": 23.4162,
        "longitude": 25.6628,
    },
    {
        "id": "mock_015",
        "title": "Forêt amazonienne",
        "fact": "L'Amazonie produit environ 20% de l'oxygène généré par l'ensemble des forêts de la planète.",
        "category": "nature",
        "latitude": -3.4653,
        "longitude": -62.2159,
    },
]


class MockFactProvider(FactProvider):
    """
    Fournisseur de fun facts statiques, sans aucun appel réseau.

    Utilise le jeu de données MOCK_FUN_FACTS comme source, filtré par distance
    depuis le point de recherche.
    """

    SOURCE_NAME = "mock"

    def get_facts(
        self,
        latitude: float,
        longitude: float,
        radius_km: float,
        limit: int,
    ) -> list[dict]:
        """
        Récupère les fun facts statiques proches d'un point GPS.

        Args:
            latitude (float): Latitude du point de recherche.
            longitude (float): Longitude du point de recherche.
            radius_km (float): Rayon de recherche en kilomètres.
            limit (int): Nombre maximum de résultats à retourner.

        Returns:
            list[dict]: Fun facts au format standardisé, triés par distance croissante.
        """
        results = []
        for entry in MOCK_FUN_FACTS:
            distance_km = calculate_distance_km(
                latitude, longitude, entry["latitude"], entry["longitude"]
            )
            if distance_km <= radius_km:
                results.append(
                    self.make_fact(
                        id=entry["id"],
                        title=entry["title"],
                        fact=entry["fact"],
                        latitude=entry["latitude"],
                        longitude=entry["longitude"],
                        distance_km=distance_km,
                        category=entry["category"],
                        url=None,
                        source=self.SOURCE_NAME,
                    )
                )

        results.sort(key=lambda f: f["distance_km"])

        if limit is not None and limit > 0:
            results = results[:limit]

        return results
