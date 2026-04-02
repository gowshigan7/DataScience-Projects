# CLAUDE.md — Restaurant Scraper

## Running tests

```bash
pytest restaurant_scraper/tests/ -v
```

All 89 tests must pass before committing. Tests use mock data only — no API calls, no files written.

## Quick smoke test (no API key needed)

```bash
python -m restaurant_scraper.main --location "48.8566,2.3522" --dry-run
python -m restaurant_scraper.main --location "Paris" --cuisine italian --min-rating 4.0 --dry-run
```

## Architecture — one file = one feature

```
config.py              ← ALL constants live here. Never hardcode values elsewhere.
geo/geolocation.py     ← geocoding + haversine distance
scraper/base_scraper.py   ← abstract interface + standardised dict format
scraper/google_places.py  ← Google Places API (needs GOOGLE_PLACES_API_KEY)
scraper/overpass_osm.py   ← OpenStreetMap fallback (free, no key)
filters/filter_engine.py  ← orchestrates all filters via apply_filters()
filters/filter_*.py        ← one filter per file, pure functions
output/formatter_*.py      ← terminal table | JSON | CSV
main.py                ← CLI entry point (argparse), assembles the pipeline
tests/mock_data.py     ← 15 static restaurants, used by --dry-run and all tests
```

## Non-default conventions

- **Config-only constants**: every configurable value belongs in `config.py`. No magic strings or numbers in business logic.
- **Docstring format**: every module has a header docstring (Description / Use cases / Input / Output). Every function has Args + Returns.
- **Filter contract**: each `filter_*.py` exposes a single pure function. No side effects. Returns the full list unchanged when the filter param is `None` or falsy.
- **Scraper contract**: all scrapers extend `BaseScraper` and return `list[dict]` in the standard format defined in `base_scraper.py`.
- **Dry-run**: `--dry-run` loads `tests/mock_data.MOCK_RESTAURANTS`, skips all network calls, and never writes files to disk.

## Environment

```bash
export GOOGLE_PLACES_API_KEY="your_key"   # optional — OSM fallback works without it
```

## Adding a new filter

1. Create `filters/filter_<name>.py` with a module docstring and a single pure function.
2. Register it in `filters/filter_engine.py` inside `apply_filters()`.
3. Export it from `filters/__init__.py`.
4. Add the CLI flag in `main.py`.
5. Add tests in `tests/test_filters.py`.
