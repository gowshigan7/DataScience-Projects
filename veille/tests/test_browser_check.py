"""
test_browser_check.py
=====================
Feature : Tests du bot navigateur, du secours automatique et de la commande « check ».

Description :
    - select_article_links / BrowserPageSource avec un renderer simulé
    - FallbackSource : principale OK, en erreur, vide ; secours indisponible
    - check_sources / format_check
    - test d'intégration avec le vrai Chromium sur un serveur HTTP local en
      mémoire (page rendue en JavaScript) ; ignoré si Playwright/Chromium absent

Entrée  : HTML en mémoire, sources factices
Sortie  : Assertions pytest (aucun accès Internet, aucun fichier écrit)
"""

import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

from veille import main as cli
from veille.config import CHECK_STATUS_EMPTY, CHECK_STATUS_ERROR, CHECK_STATUS_OK, GROUP_LABS
from veille.diagnostics.source_check import check_sources, format_check
from veille.sources import browser_page
from veille.sources.base_source import BaseSource
from veille.sources.browser_page import BrowserPageSource, select_article_links
from veille.sources.digest_registry import build_digest_sources, reddit_page, with_browser_fallback
from veille.sources.fallback import FallbackSource

PAGE = {"name": "Anthropic", "group": GROUP_LABS, "url": "https://www.anthropic.com/news",
        "link_pattern": r"anthropic\.com/news/[^/?#]+$"}

LINKS = [
    {"href": "https://www.anthropic.com/news", "text": "News", "date": ""},
    {"href": "https://www.anthropic.com/news/careers", "text": "Careers", "date": ""},
    {"href": "https://www.anthropic.com/news/new-model",
     "text": "Announcements\nIntroducing a brand new model family\nOur best model.", "date": "2026-10-02"},
    {"href": "https://www.anthropic.com/news/new-model#x", "text": "Read more about the model", "date": ""},
    {"href": "https://other.com/news/a", "text": "Unrelated long enough title", "date": ""},
]


class Fixed(BaseSource):
    """Source factice : renvoie des articles, rien, ou lève une erreur."""

    def __init__(self, name, result):
        self.name, self.result = name, result

    def fetch(self, topic, since_days, max_results=None):
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


ART = {"title": "Titre", "url": "https://a", "published": None}


# --- bot navigateur ---------------------------------------------------------------

def test_select_article_links():
    kept = select_article_links(LINKS, PAGE["link_pattern"])
    assert [k["href"] for k in kept] == ["https://www.anthropic.com/news/new-model"]
    assert kept[0]["title"] == "Introducing a brand new model family"
    assert "Our best model." in kept[0]["summary"]


def test_browser_source_with_fake_renderer():
    src = BrowserPageSource(PAGE, renderer=lambda url: LINKS)
    arts = src.fetch(None, 7)
    assert src.is_configured() and len(arts) == 1
    assert arts[0]["published"].day == 2 and arts[0]["category"] == GROUP_LABS


def test_reddit_page():
    page = reddit_page("LocalLLaMA")
    assert page["url"].startswith("https://old.reddit.com/r/LocalLLaMA/top")
    assert select_article_links(
        [{"href": "https://old.reddit.com/r/LocalLLaMA/comments/abc/a_long_post_title/",
          "text": "A long post title here"}], page["link_pattern"])


# --- secours ----------------------------------------------------------------------

def test_fallback_primary_ok():
    src = FallbackSource(Fixed("rss", [ART]), Fixed("nav", RuntimeError("ne doit pas servir")))
    assert src.fetch(None, 1) == [ART] and src.last_used == "rss"


@pytest.mark.parametrize("primary", [RuntimeError("403"), []])
def test_fallback_uses_secondary(primary):
    src = FallbackSource(Fixed("rss", primary), Fixed("nav", [ART]))
    assert src.fetch(None, 1) == [ART] and src.last_used == "nav"


def test_fallback_secondary_unavailable():
    nav = Fixed("nav", [ART])
    nav.is_configured = lambda: False
    with pytest.raises(RuntimeError):
        FallbackSource(Fixed("rss", RuntimeError("403")), nav).fetch(None, 1)
    assert FallbackSource(Fixed("rss", []), nav).fetch(None, 1) == []


def test_with_browser_fallback():
    src = Fixed("OpenAI", [])
    assert with_browser_fallback(src, {"name": "OpenAI", "group": GROUP_LABS}, False) is src
    wrapped = with_browser_fallback(src, {"name": "OpenAI", "group": GROUP_LABS}, True)
    assert isinstance(wrapped, FallbackSource) and "openai.com/news" in wrapped.secondary.page["url"]
    assert with_browser_fallback(src, {"name": "Sans secours", "group": GROUP_LABS}, True) is src


def test_registry_browser_kind(monkeypatch):
    monkeypatch.setattr("veille.sources.digest_registry.playwright_available", lambda: False)
    _, skipped = build_digest_sources(skip=["mail", "grok"])
    assert any("Playwright" in s for s in skipped)
    monkeypatch.setattr("veille.sources.digest_registry.playwright_available", lambda: True)
    sources, _ = build_digest_sources(skip=["feeds", "github", "hf_papers", "hacker_news",
                                            "reddit", "mail", "grok"])
    assert all(isinstance(s, BrowserPageSource) for s in sources) and sources


# --- diagnostic -------------------------------------------------------------------

def test_check_sources_and_format():
    fb = FallbackSource(Fixed("rss", RuntimeError("403")), Fixed("nav", [ART]))
    rows = check_sources([Fixed("ok", [ART]), Fixed("vide", []),
                          Fixed("ko", ValueError("boom\ntrace")), fb],
                         ["grok_x : non configuré (XAI_API_KEY)"], 7, 5)
    status = {r["name"]: r["status"] for r in rows}
    assert status["ok"] == CHECK_STATUS_OK and status["vide"] == CHECK_STATUS_EMPTY
    assert status["ko"] == CHECK_STATUS_ERROR and rows[2]["error"] == "ValueError: boom"
    assert rows[3]["via"] == "nav" and "secours" in rows[3]["error"]
    table = format_check(rows)
    assert "[via nav]" in table and "NON CONFIGURÉ : 1" in table


def test_cli_check(monkeypatch, capsys):
    monkeypatch.setattr(cli, "build_digest_sources",
                        lambda skip: ([Fixed("hf_papers", [ART]), Fixed("autre", [])], []))
    assert cli.main(["check", "--only", "hf"]) == 0
    out = capsys.readouterr().out
    assert "hf_papers" in out and "autre" not in out


# --- intégration : vrai Chromium sur un serveur local -------------------------------

JS_PAGE = b"""<html><body><nav><a href="/news">News</a></nav><div id="app"></div><script>
document.getElementById('app').innerHTML = '<article><a href="/news/new-model">'
 + '<span>Product</span><h3>Introducing a brand new model family</h3></a>'
 + '<time datetime="2026-10-02">Oct 2</time></article>';
</script></body></html>"""


@pytest.fixture
def local_site():
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(JS_PAGE)

        def log_message(self, *args):
            pass

    server = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{server.server_port}/news"
    server.shutdown()


def test_real_browser_renders_javascript(local_site):
    if not browser_page.playwright_available():
        pytest.skip("Playwright non installé")
    page = {"name": "Local", "group": GROUP_LABS, "url": local_site,
            "link_pattern": r"/news/[^/?#]+$"}
    try:
        arts = BrowserPageSource(page).fetch(None, 7)
    except Exception as exc:  # Chromium absent / incompatible
        pytest.skip(f"Chromium indisponible : {exc}".splitlines()[0])
    assert [a["title"] for a in arts] == ["Introducing a brand new model family"]
    assert arts[0]["published"].day == 2
