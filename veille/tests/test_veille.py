"""
test_veille.py
==============
Feature : Tests unitaires de l'application de veille.

Description :
    Couvre sujets, parsing RSS, sources (HTTP mocké), pertinence, dédoublonnage,
    catégorisation, filtre de date, pipeline, historique et formateurs.
    Aucun appel réseau ; les fichiers éventuels vont dans tmp_path de pytest.

Entrée  : tests/mock_data.py
Sortie  : Assertions pytest
"""

import json
from datetime import datetime, timezone

import pytest

from veille import main as cli
from veille import topics as tp
from veille.processing.categorize import categorize_article
from veille.processing.date_filter import filter_by_date
from veille.processing.dedup import deduplicate, normalize_title
from veille.processing.pipeline import collect, process
from veille.processing.relevance import filter_relevant, score_article
from veille.output.report_writer import render
from veille.sources import base_source
from veille.sources.base_source import BaseSource, clean_text, parse_date
from veille.sources.bing_news import BingNewsSource
from veille.sources.google_news import GoogleNewsSource, split_title
from veille.sources.hacker_news import HackerNewsSource
from veille.sources.registry import get_sources
from veille.sources.rss_parser import parse_rss
from veille.storage import history
from veille.tests.mock_data import MOCK_ARTICLES, MOCK_NOW, MOCK_TOPIC

GOOGLE_RSS = b"""<?xml version="1.0"?><rss><channel>
<item><title>Covea choisit Shift Technology - Les Echos</title><link>https://ex.com/a</link>
<pubDate>Tue, 31 Mar 2026 08:00:00 GMT</pubDate><source url="https://lesechos.fr">Les Echos</source></item>
</channel></rss>"""

BING_RSS = b"""<?xml version="1.0"?><rss xmlns:News="https://www.bing.com/news/search?q=&amp;format=rss">
<channel><item><title>Shift Technology lance un agent IA</title><link>https://ex.com/b</link>
<description>&lt;b&gt;Shift Technology&lt;/b&gt; annonce...</description>
<pubDate>Wed, 01 Apr 2026 10:00:00 GMT</pubDate><News:Source>L'Argus</News:Source></item>
</channel></rss>"""

HN_JSON = json.dumps({"hits": [{"title": "Shift Technology raises", "url": None, "objectID": "42",
                                "created_at": "2026-04-02T10:00:00Z", "points": 10,
                                "num_comments": 3}]}).encode()


@pytest.fixture
def processed():
    """Articles mockés passés dans le pipeline (fenêtre 365 jours)."""
    return process(MOCK_ARTICLES, MOCK_TOPIC, 365, MOCK_NOW)


# --- topics -----------------------------------------------------------------

def test_make_topic_defaults():
    t = tp.make_topic("  Shift Technology ", ["Shift Tech", " "], None)
    assert t == {"name": "Shift Technology", "aliases": ["Shift Tech"], "exclude": [],
                 "languages": ["fr", "en"]}


def test_topics_roundtrip_upsert_remove(tmp_path):
    path = str(tmp_path / "t.json")
    assert tp.load_topics(path) == []
    topics = tp.upsert_topic([], tp.make_topic("A"))
    topics = tp.upsert_topic(topics, tp.make_topic("a", languages=["fr"]))
    tp.save_topics(topics, path)
    loaded = tp.load_topics(path)
    assert len(loaded) == 1 and loaded[0]["languages"] == ["fr"]
    assert tp.find_topic(loaded, "A")["name"] == "a"
    assert tp.remove_topic(loaded, "A") == []


# --- base / parsing -----------------------------------------------------------

def test_clean_text_and_parse_date():
    assert clean_text("<b>A&amp;B</b>\n  c") == "A&B c"
    assert parse_date("Tue, 31 Mar 2026 08:00:00 GMT") == datetime(2026, 3, 31, 8, tzinfo=timezone.utc)
    assert parse_date("2026-04-02T10:00:00Z").day == 2
    assert parse_date("nope") is None and parse_date("") is None


def test_build_query():
    assert BaseSource.build_query(MOCK_TOPIC) == '"Shift Technology" OR "Shift Tech"'


def test_parse_rss_google_and_bing():
    g = parse_rss(GOOGLE_RSS)[0]
    assert g["source"] == "Les Echos" and g["link"] == "https://ex.com/a"
    assert parse_rss(BING_RSS)[0]["source"] == "L'Argus"
    assert parse_rss(b"not xml") == []


def test_split_title():
    assert split_title("Titre - Les Echos", "Les Echos") == ("Titre", "Les Echos")
    assert split_title("Titre - Les Echos", "") == ("Titre", "Les Echos")
    assert split_title("Sans média", "X") == ("Sans média", "X")


# --- sources (HTTP mocké) -----------------------------------------------------

def _fake_http(payload):
    calls = []

    def fake(url, params=None):
        calls.append((url, params))
        return payload
    return fake, calls


def test_google_source(monkeypatch):
    fake, calls = _fake_http(GOOGLE_RSS)
    monkeypatch.setattr(base_source, "http_get", fake)
    arts = GoogleNewsSource().fetch(MOCK_TOPIC, 7, 10)
    assert len(arts) == 2 and len(calls) == 2  # fr + en
    assert "when:7d" in calls[0][1]["q"]
    assert arts[0]["title"] == "Covea choisit Shift Technology"
    assert arts[0]["publisher"] == "Les Echos" and arts[0]["source"] == "google_news"


def test_bing_source(monkeypatch):
    fake, _ = _fake_http(BING_RSS)
    monkeypatch.setattr(base_source, "http_get", fake)
    arts = BingNewsSource().fetch({**MOCK_TOPIC, "languages": ["fr"]}, 7, 10)
    assert arts[0]["summary"] == "Shift Technology annonce..."
    assert arts[0]["publisher"] == "L'Argus"


def test_hacker_news_source(monkeypatch):
    fake, calls = _fake_http(HN_JSON)
    monkeypatch.setattr(base_source, "http_get", fake)
    arts = HackerNewsSource().fetch(MOCK_TOPIC, 7, 10)
    assert arts[0]["url"].endswith("item?id=42")
    assert "created_at_i>" in calls[0][1]["numericFilters"]


def test_registry_ignores_unknown():
    assert [s.name for s in get_sources(["google_news", "nope"])] == ["google_news"]


def test_collect_survives_failing_source():
    class Boom(BaseSource):
        name = "boom"

        def fetch(self, topic, since_days, max_results):
            raise RuntimeError("down")

    class Ok(BaseSource):
        name = "ok"

        def fetch(self, topic, since_days, max_results):
            return [self.make_article("Shift Technology", "https://x")]

    arts, errors = collect(MOCK_TOPIC, [Boom(), Ok()], 7, 5)
    assert len(arts) == 1 and errors == ["boom : down"]


# --- traitement -----------------------------------------------------------------

def test_score_and_exclusion():
    art = {"title": "Shift Technology lance", "summary": "Shift Technology et Shift Tech"}
    assert score_article(art, MOCK_TOPIC) == 3 + 2 + 1
    assert score_article({"title": "Shift Technologies stock"}, MOCK_TOPIC) == 0
    assert score_article({"title": "Unrelated"}, MOCK_TOPIC) == 0


def test_filter_relevant_no_min_keeps_all():
    arts = [{"title": "Unrelated", "summary": ""}]
    assert len(filter_relevant(arts, MOCK_TOPIC, min_score=0)) == 1
    assert filter_relevant(arts, MOCK_TOPIC) == []


def test_dedup_merges_publishers_and_summary():
    unique = deduplicate(MOCK_ARTICLES[:2])
    assert len(unique) == 1
    assert unique[0]["also_in"] == ["Nasdaq"] and unique[0]["summary"]
    assert normalize_title("Covéa, l'assureur !") == "covea l assureur"


def test_categorize():
    assert categorize_article({"title": "X lève 50 M€"}) == "Levée de fonds / Finance"
    assert categorize_article({"title": "AXA renews partnership"}) == "Partenariat / Client"
    assert categorize_article({"title": "Nouveau director"}) == "Autre"
    assert categorize_article({"title": "Rien", "summary": "keynote"}) == "Événement"


def test_filter_by_date():
    assert len(filter_by_date(MOCK_ARTICLES, 0)) == len(MOCK_ARTICLES)
    kept = filter_by_date(MOCK_ARTICLES, 365, MOCK_NOW)
    assert all(a["published"] is None or a["published"].year == 2026 for a in kept)


def test_process_pipeline(processed):
    titles = [a["title"] for a in processed]
    assert len(processed) == 5
    assert not any("Technologies" in t for t in titles)          # homonyme exclu
    assert not any("220" in t for t in titles)                    # trop ancien
    assert processed[0]["score"] >= processed[-1]["score"]
    assert all("category" in a for a in processed)


# --- historique -------------------------------------------------------------------

def test_history_marks_new_once(processed):
    conn = history.connect(":memory:")
    first = history.mark_new(conn, "S", processed)
    second = history.mark_new(conn, "S", processed)
    assert all(a["is_new"] for a in first) and not any(a["is_new"] for a in second)
    assert all(a["is_new"] for a in history.mark_new(conn, "Autre sujet", processed))


# --- sorties --------------------------------------------------------------------

@pytest.mark.parametrize("fmt", ["terminal", "markdown", "html", "json"])
def test_render_all_formats(processed, fmt):
    results = [{"topic": MOCK_TOPIC, "articles": processed, "errors": ["bing_news : 403"]}]
    out = render(results, fmt, "01/10/2026")
    assert "Covéa" in out and "bing_news" in out


def test_html_escapes(processed):
    arts = [{**processed[0], "title": "<script>x</script>"}]
    out = render([{"topic": MOCK_TOPIC, "articles": arts, "errors": []}], "html", "d")
    assert "<script>x</script>" not in out and "&lt;script&gt;" in out


# --- CLI ------------------------------------------------------------------------

def test_cli_dry_run(capsys):
    assert cli.main(["run", "--dry-run", "--since-days", "365", "--output", "markdown"]) == 0
    captured = capsys.readouterr()
    assert "# Rapport de veille" in captured.out and "[DRY-RUN]" in captured.err


def test_cli_add_list_remove(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cli, "TOPICS_FILE", str(tmp_path / "t.json"))
    cli.main(["add", "Shift Technology", "--exclude", "Shift Technologies"])
    cli.main(["list"])
    assert "Shift Technology [fr, en]" in capsys.readouterr().out
    cli.main(["remove", "shift technology"])
    cli.main(["list"])
    assert "Aucun sujet suivi." in capsys.readouterr().out


def test_cli_run_without_topics(tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "TOPICS_FILE", str(tmp_path / "none.json"))
    monkeypatch.setattr(cli, "HISTORY_DB", str(tmp_path / "h.sqlite"))
    assert cli.main(["run"]) == 1
