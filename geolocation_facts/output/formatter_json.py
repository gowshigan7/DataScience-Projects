"""
formatter_json.py
=================
Feature : Export des fun facts au format JSON.

Description :
    Ce module formate et exporte une liste de fun facts en JSON.
    Il peut retourner la chaîne JSON ou l'écrire dans un fichier.

    En mode dry-run, le fichier n'est pas écrit sur le disque.
    Le JSON produit est proprement indenté et encodé en UTF-8.

Cas d'usage :
    - Export vers un fichier JSON pour traitement ultérieur
    - Retour de la chaîne JSON (ex: pour une API ou affichage direct)
    - Mode dry-run : affiche le JSON sans écrire de fichier

Entrée  : List[dict] (faits), str (chemin de fichier optionnel)
Sortie  : str (JSON formaté), et optionnellement un fichier écrit sur le disque
"""

import json
import os


def format_json(facts: list[dict]) -> str:
    """
    Convertit une liste de fun facts en chaîne JSON formatée.

    Args:
        facts (list[dict]): Liste de fun facts à sérialiser.

    Returns:
        str: Chaîne JSON indentée (2 espaces), encodage UTF-8.
    """
    return json.dumps(facts, ensure_ascii=False, indent=2)


def save_json(
    facts: list[dict],
    filepath: str,
    dry_run: bool = False,
) -> str:
    """
    Exporte une liste de fun facts vers un fichier JSON.

    Args:
        facts (list[dict]): Liste de fun facts à exporter.
        filepath (str): Chemin du fichier de sortie (ex: "output/facts.json").
        dry_run (bool): Si True, affiche le JSON sans écrire de fichier.

    Returns:
        str: Chemin du fichier écrit, ou "[DRY-RUN]" si dry_run est True.
    """
    json_str = format_json(facts)

    if dry_run:
        print(f"[DRY-RUN] Export JSON (non ecrit) vers : {filepath}")
        print(json_str)
        return "[DRY-RUN]"

    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json_str)

    print(f"Export JSON : {len(facts)} fun facts -> {filepath}")
    return filepath
