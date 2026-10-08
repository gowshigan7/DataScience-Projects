# Handover: Hermes Village

For whoever picks this up next, most likely a Claude Code session running on
the DGX Spark, next to the real Hermes install.

## Where things stand

- **Branch:** `ccr-9966154c-fjk1sf`. There is no PR yet.
- **Last commit:** `128d2b9 feat: add terminal Hermes Village`.
- **Tests:** 101 pass (89 `restaurant_scraper` + 12 `hermes_bridge`):
  ```bash
  pip install pytest requests
  pytest restaurant_scraper/tests/ hermes_bridge/tests/ -v
  ```
- **Done:** the terminal village. It reads `~/.hermes` read-only, maps cron
  jobs to residents and the gateway and chat platforms to buildings, and has
  `--demo`, `--watch N` and `--json` modes.
- **Not done:** it has never been run against a real `~/.hermes`. The cloud
  session had no Hermes, so it only ever ran on simulated data.

## The idea (one paragraph)

This copies [Nexus Village](https://kanzie.com/#builds) by Christian Nilsson:
Hermes agents shown as felt animals in a 3D village. Animals walk to work while
their job runs, buildings are services, and robots are helper agents. We split
it the same way:

- **Backend:** a pure mapping from Hermes state to a `VillageSnapshot` JSON
  (`village_state.py`).
- **Frontends:** they only render that snapshot. The terminal one exists
  (`village_tui.py`); 3D comes next.

`README.md` has the full mapping table, and `ontology.yaml` has the vocabulary
(monitoring, village and domain layers).

## Files

| File | Role |
|---|---|
| `config.py` | Every constant: paths, the 5-minute work window, night hours (22:00–07:00), cast, icons, chatter lines |
| `village_state.py` | `load_hermes_home()` (I/O) → `build_snapshot()` (pure) |
| `village_tui.py` | `render_village(snapshot)` → string |
| `demo_data.py` | Simulated `jobs.json` and `gateway_state.json`, used by `--demo` and the tests |
| `main.py` | CLI: `python -m hermes_bridge.main [--demo] [--watch N] [--json] [--hermes-home PATH]` |
| `tests/test_village.py` | 12 tests. No network, no file writes |

## First thing to do on the Spark

```bash
python -m hermes_bridge.main --no-color   # real ~/.hermes
python -m hermes_bridge.main --json | head -50
```

Check whether the residents and buildings match what `hermes` itself
reports. The field names were taken from the hermes-agent source
(`cron/jobs.py`, `gateway/status.py`), so expect small drift:

- **Jobs:** `cron/jobs.json` → `{"jobs": [...]}`, with each job having `id`,
  `name`, `enabled`, `state` (`scheduled`/`paused`/`completed`/`error`),
  `last_run_at`, `next_run_at`, `last_status`, `last_error`,
  `failure_streak` and `schedule_display`. Profiles live at
  `profiles/<name>/cron/jobs.json`.
- **Gateway:** `gateway_state.json` → `gateway_state`, `active_agents`,
  `exit_reason`, and `platforms: {name: {state, error_code, error_message}}`.

If something differs, fix the mapping in `village_state.py`, add a regression
test with the real shape in `demo_data.py`, and keep `demo_data.py`
realistic.

## Known limitations and decisions

- **"Working" is a guess.** Hermes keeps its list of running jobs in memory
  only (`cron/scheduler.py: _running_job_ids`), so a resident counts as
  working if `last_run_at` was in the last `WORK_WINDOW_MINUTES` (5).
  Better source to look for: `cron/executions.db` or
  `runtime/active_sessions.json`.
- **Character names are our own.** We avoided Nexus's names (Nora, Pip, Kai,
  Hazel). The cast is stable per job id and unique within the village.
- **Code conventions (see `/CLAUDE.md`, `.claude/rules/`):**
  - All constants go in `config.py`.
  - Every module has a docstring header (Description / Use cases / Input /
    Output), and every function documents its Args and Returns.
  - Commit messages use `<type>: <desc>`.

## Next steps (in order)

1. **Validate on real data** (above).
2. **3D village:** a three.js page that polls `--json` output. Add a tiny
   `python -m hermes_bridge.serve` (stdlib `http.server`) that serves
   `/api/village/snapshot` plus the static page. Do it on the Spark so it
   reads live state. Keep the backend and frontend split: the page only
   renders.
3. **Cases and robots:** helper agents and investigations, from
   `kanban.db` or delegation state (`cache/delegation/live/`).
4. **Souls-lite:** a persona per resident (from Hermes `profiles/*/SOUL.md`)
   and a pairwise affinity score that grows when residents share a run.
5. **Restaurant tie-in:** a `restaurant-scout` Hermes skill that calls
   `python -m restaurant_scraper.main --format json`, plus a
   `lunch-roulette` cron job. Both show up as residents automatically.

## Context the cloud session couldn't reach

- **The Reddit post** (https://www.reddit.com/r/hermesagent/s/rQoulVVXAA) was
  blocked. Nexus Village was identified from https://kanzie.com/#builds and
  the live demo's changelog.
- **SSH to the Spark** isn't possible from cloud sessions (no outbound port
  22). That's why the work moves onto the Spark itself.
