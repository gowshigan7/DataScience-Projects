"""
test_digest.py
==============
Feature : Tests unitaires du digest IA.

Description :
    Couvre le parsing Atom, les sources du digest (HTTP, IMAP et xAI mockés),
    l'analyse des newsletters, le registre, le pipeline et la commande CLI.
    Aucun appel réseau, aucun fichier écrit.

Entrée  : tests/mock_digest.py + payloads construits en mémoire
Sortie  : Assertions pytest
"""

import json
import urllib.error
from email.message import EmailMessage

import pytest

from veille import main as cli
from veille.config import GROUP_COMMUNITY, GROUP_LABS, GROUP_RELEASES, GROUP_X
from veille.processing.digest_pipeline import process_digest
from veille.sources import base_source
from veille.sources.base_source import matches_keywords, truncate
from veille.sources.digest_registry import build_digest_sources
from veille.sources.feed_rss import FeedSource, github_feed
from veille.sources.grok_x import GrokXSource, extract_output, parse_posts
from veille.sources.hf_papers import HFPapersSource
from veille.sources.hn_top import HackerNewsTopSource
from veille.sources.mailbox import MailboxSource
from veille.sources.newsletter_parser import newsletter_to_fields, pick_main_link, sender_matches
from veille.sources.reddit import RedditSource
from veille.sources.rss_parser import parse_rss
from veille.tests.mock_digest import MOCK_DIGEST_ARTICLES, MOCK_DIGEST_NOW

ATOM = b"""<?xml version="1.0"?><feed xmlns="http://www.w3.org/2005/Atom">
<entry><title>v2.0.0</title><link rel="alternate" href="https://github.com/o/r/releases/tag/v2"/>
<updated>2026-09-30T12:00:00Z</updated><content type="html">&lt;p&gt;Notes&lt;/p&gt;</content>
<author><name>bot</name></author></entry></feed>"""

RSS = b"""<?xml version="1.0"?><rss><channel>
<item><title>New GPU for gaming</title><link>https://n.com/1</link><pubDate>Wed, 30 Sep 2026 10:00:00 GMT</pubDate></item>
<item><title>Faster LLM inference</title><link>https://n.com/2</link><pubDate>Wed, 30 Sep 2026 11:00:00 GMT</pubDate></item>
</channel></rss>"""


def _patch_get(monkeypatch, payload):
    calls = []

    def fake(url, params=None):
        calls.append((url, params))
        if isinstance(payload, Exception):
            raise payload
        return payload(url) if callable(payload) else payload
    monkeypatch.setattr(base_source, "http_get", fake)
    return calls


# --- utilitaires -----------------------------------------------------------------

def test_matches_keywords_whole_word():
    assert matches_keywords("New AI model", ["ai"])
    assert not matches_keywords("He said hello", ["ai"])
    assert matches_keywords("anything", None)


def test_truncate():
    assert truncate("court", 10) == "court"
    assert truncate("un deux trois quatre", 10) == "un deux…"


def test_parse_atom():
    item = parse_rss(ATOM)[0]
    assert item["link"].endswith("/v2") and item["pubDate"].startswith("2026-09-30")
    assert item["source"] == "bot" and "Notes" in item["description"]


# --- flux ------------------------------------------------------------------------

def test_feed_source_keywords_and_group(monkeypatch):
    _patch_get(monkeypatch, RSS)
    feed = {"name": "NVIDIA", "group": GROUP_LABS, "url": "https://x", "keywords": ["llm"]}
    arts = FeedSource(feed).fetch(None, 1)
    assert [a["title"] for a in arts] == ["Faster LLM inference"]
    assert arts[0]["category"] == GROUP_LABS and arts[0]["publisher"] == "NVIDIA"


def test_github_feed(monkeypatch):
    calls = _patch_get(monkeypatch, ATOM)
    arts = FeedSource(github_feed("o/r")).fetch(None, 1)
    assert calls[0][0] == "https://github.com/o/r/releases.atom"
    assert arts[0]["category"] == GROUP_RELEASES and arts[0]["summary"] == "Notes"


def test_hf_papers(monkeypatch):
    data = [{"paper": {"id": "2609.1", "title": "Top", "upvotes": 50, "summary": "abs"},
             "publishedAt": "2026-09-30T00:00:00Z"},
            {"paper": {"id": "2609.2", "title": "Low", "upvotes": 1}}]
    _patch_get(monkeypatch, json.dumps(data).encode())
    arts = HFPapersSource().fetch(None, 1, 10)
    assert len(arts) == 1 and arts[0]["url"].endswith("/papers/2609.1")


def test_hn_top_filters_ai(monkeypatch):
    hits = {"hits": [{"title": "Show HN: my LLM agent", "points": 300, "objectID": "1",
                      "created_at": "2026-09-30T10:00:00Z"},
                     {"title": "Rust 2.0 released", "points": 900, "objectID": "2"}]}
    calls = _patch_get(monkeypatch, json.dumps(hits).encode())
    arts = HackerNewsTopSource().fetch(None, 1, 10)
    assert [a["title"] for a in arts] == ["Show HN: my LLM agent"]
    assert "points>=" in calls[0][1]["numericFilters"] and arts[0]["category"] == GROUP_COMMUNITY


def test_reddit_json(monkeypatch):
    data = {"data": {"children": [
        {"data": {"title": "Big", "permalink": "/r/x/1", "score": 500, "num_comments": 9,
                  "created_utc": 1790000000}},
        {"data": {"title": "Small", "permalink": "/r/x/2", "score": 3, "created_utc": 1790000000}}]}}
    _patch_get(monkeypatch, json.dumps(data).encode())
    arts = RedditSource("LocalLLaMA").fetch(None, 1)
    assert [a["title"] for a in arts] == ["Big"]
    assert arts[0]["url"] == "https://www.reddit.com/r/x/1"


def test_reddit_falls_back_to_rss(monkeypatch):
    def payload(url):
        if url.endswith(".json"):
            raise urllib.error.HTTPError(url, 403, "blocked", None, None)
        return ATOM
    calls = _patch_get(monkeypatch, payload)
    arts = RedditSource("OpenAI").fetch(None, 7)
    assert len(arts) == 1 and calls[-1][1] == {"t": "week"}


# --- newsletters / IMAP ----------------------------------------------------------

def _newsletter(sender="The Batch <thebatch@deeplearning.ai>"):
    msg = EmailMessage()
    msg["From"], msg["Subject"] = sender, "Cette semaine en IA"
    msg["Date"] = "Wed, 30 Sep 2026 07:00:00 +0000"
    msg.set_content("texte brut")
    msg.add_alternative(
        '<html><style>p{}</style><body><a href="https://x.com/unsubscribe">Unsubscribe</a>'
        '<p>Bonjour, voici les nouvelles.</p><a href="https://news.com/a">Article</a>'
        '<a href="https://nl.com/web">View in browser</a></body></html>', subtype="html")
    return msg


def test_sender_matches():
    assert sender_matches("X <a@deeplearning.ai>", ["deeplearning.ai"])
    assert not sender_matches("Promo <shop@store.com>", ["deeplearning.ai"])
    assert sender_matches("anyone", [])


def test_pick_main_link():
    assert pick_main_link([("https://a.com/unsubscribe", ""), ("https://b.com", "x")]) == "https://b.com"
    assert pick_main_link([("mailto:a@b", "")]) == ""


def test_newsletter_to_fields():
    f = newsletter_to_fields(_newsletter())
    assert f["url"] == "https://nl.com/web" and f["publisher"] == "The Batch"
    assert "Bonjour" in f["summary"] and "p{}" not in f["summary"]
    assert f["published"].day == 30


class FakeIMAP:
    """IMAP en mémoire : deux messages, dont un hors liste d'expéditeurs."""

    def __init__(self, host):
        self.msgs = {b"1": _newsletter(), b"2": _newsletter("Promo <shop@store.com>")}
        self.selected = None

    def login(self, user, password):
        return "OK", []

    def select(self, folder, readonly=False):
        self.selected = (folder, readonly)
        return "OK", []

    def search(self, charset, *criteria):
        return "OK", [b"1 2"]

    def fetch(self, msg_id, parts):
        assert "PEEK" in parts  # ne pas marquer comme lu
        return "OK", [(b"hdr", self.msgs[msg_id].as_bytes())]

    def logout(self):
        return "BYE", []


def test_mailbox_source():
    src = MailboxSource(user="u", password="p", senders=["deeplearning.ai"], imap_factory=FakeIMAP)
    arts = src.fetch(None, 1)
    assert len(arts) == 1 and arts[0]["title"] == "Cette semaine en IA"
    assert not MailboxSource(user="", password="").is_configured()


# --- Grok / X ----------------------------------------------------------------------

GROK_RESPONSE = {"output": [{"type": "message", "content": [{
    "type": "output_text",
    "text": '```json\n[{"handle": "@karpathy", "date": "2026-09-30", "text": "New video", '
            '"url": "https://x.com/karpathy/status/1"}]\n```',
    "annotations": [{"type": "url_citation", "url": "https://x.com/karpathy/status/1"}]}]}]}


def test_extract_and_parse_posts():
    text, urls = extract_output(GROK_RESPONSE)
    assert urls == ["https://x.com/karpathy/status/1"]
    assert parse_posts(text)[0]["handle"] == "@karpathy"
    assert parse_posts("pas de json") == []


def test_grok_source_chunks_handles(monkeypatch):
    calls = []

    def fake_post(url, payload, headers, timeout):
        calls.append(payload)
        return GROK_RESPONSE
    monkeypatch.setattr(base_source, "http_post_json", fake_post)
    handles = [f"h{i}" for i in range(25)]
    arts = GrokXSource(api_key="k", handles=handles).fetch(None, 1)
    assert len(calls) == 2 and len(calls[0]["tools"][0]["allowed_x_handles"]) == 20
    assert arts[0]["title"].startswith("@karpathy : ") and arts[0]["category"] == GROUP_X


def test_grok_falls_back_to_citations(monkeypatch):
    resp = {"output": [{"content": [{"type": "output_text", "text": "Résumé en prose",
            "annotations": [{"url": "https://x.com/ylecun/status/9"}, {"url": "https://a.com"}]}]}]}
    monkeypatch.setattr(base_source, "http_post_json", lambda *a: resp)
    arts = GrokXSource(api_key="k", handles=["ylecun"]).fetch(None, 1)
    assert len(arts) == 1 and arts[0]["publisher"] == "X · @ylecun"


# --- registre, pipeline, CLI ---------------------------------------------------------

def test_registry_skips_unconfigured(monkeypatch):
    monkeypatch.setattr(MailboxSource, "is_configured", lambda self: False)
    monkeypatch.setattr(GrokXSource, "is_configured", lambda self: False)
    sources, skipped = build_digest_sources(skip=["browser"])
    assert len(skipped) == 2 and sources
    only, _ = build_digest_sources(skip=["feeds", "github", "reddit", "browser", "mail", "grok"])
    assert {s.name for s in only} == {"hf_papers", "hacker_news_top"}


def test_process_digest():
    arts = process_digest(MOCK_DIGEST_ARTICLES, 1, MOCK_DIGEST_NOW)
    assert len(arts) == 9                                    # doublon fusionné, ancien retiré
    assert arts[0]["published"] >= arts[-1]["published"]
    openai = next(a for a in arts if a["url"] == "https://openai.com/news/")
    assert openai["also_in"] == ["Autre Média"]


@pytest.mark.parametrize("fmt", ["terminal", "markdown", "html"])
def test_cli_digest_dry_run(capsys, fmt):
    assert cli.main(["digest", "--dry-run", "--output", fmt]) == 0
    out = capsys.readouterr().out
    assert "Artificial Analysis" in out and "Communauté" in out
