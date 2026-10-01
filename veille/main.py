"""
main.py
=======
Point d'entrée de l'application de veille.

Description :
    Commandes :
    - add     : ajoute (ou met à jour) un sujet de veille
    - list    : liste les sujets suivis
    - remove  : retire un sujet
    - run     : lance la veille (tous les sujets ou --topic) et produit le rapport

    En --dry-run, les articles de tests/mock_data.py remplacent les sources,
    aucun appel réseau n'est fait et aucun fichier n'est écrit (sauf --save explicite).

Cas d'usage :
    python -m veille.main add "Shift Technology" --alias "Shift Tech" --exclude "Shift Technologies"
    python -m veille.main run --output html
    python -m veille.main run --topic "Shift Technology" --since-days 7
    python -m veille.main run --dry-run --since-days 365

Entrée  : Arguments CLI
Sortie  : Rapport (terminal, Markdown, HTML ou JSON)
"""

import argparse
import sys
from datetime import datetime

from veille.config import (
    DEFAULT_MAX_PER_SOURCE,
    DEFAULT_OUTPUT_FORMAT,
    DEFAULT_SINCE_DAYS,
    DEFAULT_SOURCES,
    GENERATED_AT_FORMAT,
    HISTORY_DB,
    OUTPUT_FORMATS,
    REPORT_STEM_FORMAT,
    REPORTS_DIR,
    SOURCE_NAMES,
    TOPICS_FILE,
)
from veille import topics as tp
from veille.output.report_writer import render, write_report
from veille.processing.pipeline import collect, process
from veille.sources.registry import get_sources
from veille.storage import history


def build_parser() -> argparse.ArgumentParser:
    """
    Construit le parser CLI.

    Returns:
        argparse.ArgumentParser: Parser avec les sous-commandes add/list/remove/run.
    """
    parser = argparse.ArgumentParser(prog="veille", description="Veille automatique sur vos sujets.")
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="Ajouter / modifier un sujet")
    add.add_argument("name", help='Nom du sujet, ex. "Shift Technology"')
    add.add_argument("--alias", nargs="*", default=[], help="Autres formulations à rechercher")
    add.add_argument("--exclude", nargs="*", default=[], help="Termes excluant un article (homonymes)")
    add.add_argument("--lang", nargs="*", default=None, help="Langues (fr, en)")

    sub.add_parser("list", help="Lister les sujets")

    rm = sub.add_parser("remove", help="Retirer un sujet")
    rm.add_argument("name")

    run = sub.add_parser("run", help="Lancer la veille")
    run.add_argument("--topic", nargs="*", help="Sujets à traiter (défaut : tous)")
    run.add_argument("--since-days", type=int, default=DEFAULT_SINCE_DAYS)
    run.add_argument("--sources", nargs="*", choices=SOURCE_NAMES, default=DEFAULT_SOURCES)
    run.add_argument("--max", type=int, default=DEFAULT_MAX_PER_SOURCE, help="Articles max par source")
    run.add_argument("--output", choices=OUTPUT_FORMATS, default=DEFAULT_OUTPUT_FORMAT)
    run.add_argument("--out-dir", default=REPORTS_DIR, help="Dossier des rapports")
    run.add_argument("--only-new", action="store_true", help="N'afficher que les nouveautés")
    run.add_argument("--dry-run", action="store_true", help="Données de démo, sans réseau")
    run.add_argument("--save", action="store_true", help="En dry-run, écrire quand même le rapport")
    return parser


def cmd_run(args) -> int:
    """
    Exécute la veille et affiche / enregistre le rapport.

    Args:
        args (argparse.Namespace): Arguments de la sous-commande run.

    Returns:
        int: Code de sortie (0 = OK, 1 = aucun sujet).
    """
    if args.dry_run:
        from veille.tests.mock_data import MOCK_ARTICLES, MOCK_NOW, MOCK_TOPIC
        print("[DRY-RUN] Données de démonstration, aucun appel réseau.", file=sys.stderr)
        topics, now = [MOCK_TOPIC], MOCK_NOW
        conn = history.connect(":memory:")
    else:
        topics, now = tp.load_topics(TOPICS_FILE), datetime.now().astimezone()
        conn = history.connect(HISTORY_DB)
    if args.topic:
        topics = [t for t in topics if t["name"].lower() in {n.lower() for n in args.topic}]
    if not topics:
        print('Aucun sujet. Ajoutez-en un : python -m veille.main add "Mon sujet"', file=sys.stderr)
        return 1

    results = []
    for topic in topics:
        if args.dry_run:
            raw, errors = MOCK_ARTICLES, []
        else:
            print(f"… collecte : {topic['name']}", file=sys.stderr)
            raw, errors = collect(topic, get_sources(args.sources), args.since_days, args.max)
        articles = history.mark_new(conn, topic["name"], process(raw, topic, args.since_days, now))
        if args.only_new:
            articles = [a for a in articles if a["is_new"]]
        results.append({"topic": topic, "articles": articles, "errors": errors})
    conn.close()

    content = render(results, args.output, now.strftime(GENERATED_AT_FORMAT))
    if args.output == "terminal" or (args.dry_run and not args.save):
        print(content)
    else:
        print(f"Rapport écrit : {write_report(content, args.output, args.out_dir, now.strftime(REPORT_STEM_FORMAT))}")
    return 0


def main(argv=None) -> int:
    """
    Point d'entrée CLI.

    Args:
        argv (list[str] | None): Arguments (sys.argv si None).

    Returns:
        int: Code de sortie.
    """
    args = build_parser().parse_args(argv)
    if args.command == "run":
        return cmd_run(args)
    topics = tp.load_topics(TOPICS_FILE)
    if args.command == "add":
        topic = tp.make_topic(args.name, args.alias, args.exclude, args.lang)
        tp.save_topics(tp.upsert_topic(topics, topic), TOPICS_FILE)
        print(f"Sujet enregistré : {topic['name']}")
    elif args.command == "remove":
        tp.save_topics(tp.remove_topic(topics, args.name), TOPICS_FILE)
        print(f"Sujet retiré : {args.name}")
    else:
        for t in topics or []:
            extra = f"  (alias : {', '.join(t['aliases'])})" if t["aliases"] else ""
            extra += f"  (exclus : {', '.join(t['exclude'])})" if t["exclude"] else ""
            print(f"- {t['name']} [{', '.join(t['languages'])}]{extra}")
        if not topics:
            print("Aucun sujet suivi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
