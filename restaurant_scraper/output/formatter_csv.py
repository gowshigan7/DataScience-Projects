"""
formatter_csv.py
================
Feature : Export des restaurants au format CSV.

Description :
    Ce module formate et exporte une liste de restaurants en CSV (comma-separated values).
    Il peut retourner la chaîne CSV ou l'écrire dans un fichier.

    Le CSV produit est compatible avec Excel et les outils d'analyse de données.
    En mode dry-run, le fichier n'est pas écrit sur le disque.

    Colonnes exportées :
        id, name, address, latitude, longitude, rating, price_level,
        cuisine, is_open_now, distance_m, phone, website, source

Cas d'usage :
    - Export vers un fichier CSV pour analyse dans Excel / pandas
    - Mode dry-run : affiche le CSV sans écrire de fichier
    - Retour de la chaîne CSV pour usage programmatique

Entrée  : List[dict] (restaurants), str (chemin de fichier optionnel)
Sortie  : str (CSV formaté), et optionnellement un fichier écrit sur le disque
"""

import csv
import io
import os


CSV_COLUMNS = [
    "id",
    "name",
    "address",
    "latitude",
    "longitude",
    "rating",
    "price_level",
    "cuisine",
    "is_open_now",
    "distance_m",
    "phone",
    "website",
    "source",
]


def format_csv(restaurants: list[dict]) -> str:
    """
    Convertit une liste de restaurants en chaîne CSV formatée.

    Args:
        restaurants (list[dict]): Liste de restaurants à sérialiser.

    Returns:
        str: Chaîne CSV avec en-tête, séparateur virgule, encodage UTF-8.
    """
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=CSV_COLUMNS,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    for restaurant in restaurants:
        writer.writerow({col: restaurant.get(col, "") for col in CSV_COLUMNS})

    return output.getvalue()


def save_csv(
    restaurants: list[dict],
    filepath: str,
    dry_run: bool = False,
) -> str:
    """
    Exporte une liste de restaurants vers un fichier CSV.

    Args:
        restaurants (list[dict]): Liste de restaurants à exporter.
        filepath (str): Chemin du fichier de sortie (ex: "output/restaurants.csv").
        dry_run (bool): Si True, affiche le CSV sans écrire de fichier.

    Returns:
        str: Chemin du fichier écrit, ou "[DRY-RUN]" si dry_run est True.
    """
    csv_str = format_csv(restaurants)

    if dry_run:
        print(f"[DRY-RUN] Export CSV (non ecrit) vers : {filepath}")
        print(csv_str)
        return "[DRY-RUN]"

    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        f.write(csv_str)

    print(f"Export CSV : {len(restaurants)} restaurants -> {filepath}")
    return filepath
