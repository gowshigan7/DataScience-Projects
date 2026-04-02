# rules/conventions.md
# Non-default coding conventions for restaurant_scraper.
# Loaded automatically by CLAUDE.md via .claude/rules/.

## File conventions
- One feature per file — do not add unrelated logic to an existing module.
- Every new `.py` file must start with a module-level docstring: Description, Use cases, Input, Output.
- Every function must have a docstring with Args and Returns sections.

## Constants
- ALL constants and configurable values go in `config.py`. Never hardcode strings or numbers in business logic.

## Filters
- Each `filters/filter_*.py` exposes exactly ONE pure function.
- That function must return the full list unchanged when its filter param is `None` or falsy — never raise.

## Scrapers
- All scrapers must extend `BaseScraper` and return `list[dict]` using `BaseScraper.make_restaurant()`.
- Dry-run must short-circuit before any network call and print a `[DRY-RUN]` message.

## Tests
- Tests live in `tests/` and use `MOCK_RESTAURANTS` from `mock_data.py` — no real API calls, no files written.
- All 89 tests must pass before any commit: `pytest restaurant_scraper/tests/ -v`.
