"""
formatter_json.py
=================
Feature : Export des restaurants au format JSON.

Description :
    Ce module formate et exporte une liste de restaurants en JSON.
    Il peut retourner la chaîne JSON ou l'écrire dans un fichier.

    En mode dry-run, le fichier n'est pas écrit sur le disque.
    Le JSON produit est proprement indenté et encodé en UTF-8.

Cas d'usage :
    - Export vers un fichier JSON pour traitement ultérieur
    - Retour de la chaîne JSON (ex: pour une API ou affichage direct)
    - Mode dry-run : affiche le JSON sans écrire de fichier

Entrée  : List[dict] (restaurants), str (chemin de fichier optionnel)
Sortie  : str (JSON formaté), et optionnellement un fichier écrit sur le disque
"""

import json
import os


def format_json(restaurants: list[dict]) -> str:
    """
    Convertit une liste de restaurants en chaîne JSON formatée.

    Args:
        restaurants (list[dict]): Liste de restaurants à sérialiser.

    Returns:
        str: Chaîne JSON indentée (2 espaces), encodage UTF-8.
    """
    return json.dumps(restaurants, ensure_ascii=False, indent=2)


def save_json(
    restaurants: list[dict],
    filepath: str,
    dry_run: bool = False,
) -> str:
    """
    Exporte une liste de restaurants vers un fichier JSON.

    Args:
        restaurants (list[dict]): Liste de restaurants à exporter.
        filepath (str): Chemin du fichier de sortie (ex: "output/restaurants.json").
        dry_run (bool): Si True, affiche le JSON sans écrire de fichier.

    Returns:
        str: Chemin du fichier écrit, ou "[DRY-RUN]" si dry_run est True.
    """
    json_str = format_json(restaurants)

    if dry_run:
        print(f"[DRY-RUN] Export JSON (non ecrit) vers : {filepath}")
        print(json_str)
        return "[DRY-RUN]"

    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json_str)

    print(f"Export JSON : {len(restaurants)} restaurants -> {filepath}")
    return filepath
