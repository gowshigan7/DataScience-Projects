# Hermes Bridge — monitoring, ontology & fun

Exploratory branch for wiring our projects (starting with `restaurant_scraper`)
into our **Hermes agent** (Nous Research). Inspired by an r/hermesagent post
(https://www.reddit.com/r/hermesagent/s/rQoulVVXAA) about
[Nexus Village](https://kanzie.com/#builds) by Christian Nilsson.

## Quick start: the terminal village

```bash
python -m hermes_bridge.main --demo            # simulated Hermes, no install needed
python -m hermes_bridge.main                   # your real ~/.hermes (read-only)
python -m hermes_bridge.main --watch 5         # live, redraws every 5 s
python -m hermes_bridge.main --json            # VillageSnapshot for the 3D step
pytest hermes_bridge/tests/ -v
```

```
 ☀  Hermes Village — 16:54    2 working · 1 idle · 1 sleeping · 1 trouble
 🏛  BUILDINGS
   🟢 Gateway          running · 2 agents
   🔴 Discord          retrying: invalid token
 🐾 RESIDENTS
   🦊 Fennel     mail-digest            ⚒  working   @default
   🦡 Bruno      restaurant-scout       🔥 trouble   @default  (Overpass API timeout)
   🦦 Ottilie    nightly-tests          💤 sleeping  @coder
 💬 Tilda: anyone up for boule by the pond?
```

How the mapping works:

- **Each cron job becomes a resident.** Jobs come from `cron/jobs.json` and
  `profiles/*/cron/jobs.json`. A resident's state is one of:
  - **working:** the job ran in the last 5 minutes;
  - **trouble:** `last_status == "error"`;
  - **sleeping:** the job is paused, or it's night;
  - **idle:** none of the above.
- **The gateway and each chat platform become buildings.** These come from
  `gateway_state.json`.
- **Field names come from the hermes-agent source.** Everything lives in
  `config.py`.

Files: `village_state.py` (backend, pure mapping), `village_tui.py`
(terminal frontend), `demo_data.py`, `main.py` (CLI).

## 0. What Nexus Village does (our reference)

Nexus is a self-hosted personal AI operations system that Hermes orchestrates.
The **Village** ([live demo](https://kanzie.com/nexus/village/index.html)) is a
3D felt-toy diorama of the server, a monitoring dashboard disguised as a game:

| Village thing | Real system state |
|---|---|
| Animal resident (e.g. Nora the fox) | A Hermes agent or cron job. It walks to work while its job runs, and naps near home or sleeps at night when idle |
| Building / hotel room | A service or website: lit when up, dim at night, red on error, with an uptime label |
| Cables with coloured beads | Network traffic and events between services, plus a last-hour sparkline |
| Robots (investigator / executor / verifier) | Helper agents working a "case". A robot at the notice board means a plan needs your decision |
| Worker robot in a hard hat | A background job with no owner. It counts down and pops into confetti when done |
| Workshop and gnomes | CI/CD: the release being built, deliveries by parachute, a town crier on release day |
| Fireworks | A test suite passing |
| "Souls" | Each resident has a personality, memories and feelings about others (a relationship graph), reflects nightly, and spreads rumours |

From its client code, the frontend reads a live stream at
`/api/village/stream?links=1`. It also calls `/api/village/souls/graph`
(the relationship web), `/api/village/souls/bench`,
`/api/village/speak/reflect` and `/api/village/resolve?case=…`.
That means: **backend = a state reducer over Hermes data → event stream;
frontend = a pure renderer.** We copy that split.

## 1. Monitoring

Hermes keeps all of its state under `~/.hermes/`. For example: `state.db`,
`cron/jobs.json`, `cron/executions.db`, `logs/*.log`, `sessions/*.json`,
`skills/*/SKILL.md` and `state/gateway.heartbeat`.

- **Short term:** run [`hermesd`](https://pypi.org/project/hermesd/), a
  read-only TUI dashboard. Install it with `uv tool install hermesd`. It shows
  gateway health, sessions, tokens and cost, cron, skills and logs.
- **Our layer:** have the scraper emit one JSONL event per pipeline stage to
  `~/.hermes/logs/restaurant_scraper.log`. Hermes and hermesd then pick it up
  for free.
- **Health rule:** a process being "up" isn't enough. We check each stage of
  the run (see the ontology below) and alert on the first stage that is
  missing.

## 2. Ontology

This is a small, typed vocabulary shared by the agent, the dashboards and the
scraper. The draft lives in [`ontology.yaml`](ontology.yaml).

```
Trigger ─starts─▶ Run ─calls─▶ ToolCall ─produces─▶ Artifact ─sent_via─▶ Delivery
                   │                                   │
                   └─about─▶ Place(Restaurant) ◀─describes─┘
```

- **Monitoring classes:** Trigger, Run, ToolCall, Artifact and Delivery. Each
  maps to a Hermes file (a cron job, a session, the tool log, cron output or
  deliveries.db).
- **Village classes:** Resident, Building, Link, Case and Soul, the visual
  layer. Each is *bound to* a monitoring class, so the picture can't drift
  from the truth ("truthful robots").
- **Domain classes:** Restaurant, Cuisine, PriceLevel and Location. These
  mirror the standard dict in `scraper/base_scraper.py`, so a scraper result
  maps 1:1 onto ontology instances.

## 3. Fun: our own mini-village

The same split, at our scale:

1. **`village_state.py` (backend):** reads `~/.hermes/` (cron jobs,
   sessions, logs) plus scraper JSONL events. It emits one `VillageSnapshot`
   JSON (residents, buildings, links, cases) in the shape of the ontology below.
2. **Renderer:** start with a terminal or 2D HTML page, and maybe three.js
   later. Residents = Hermes jobs, buildings = our services (the scraper, the
   OSM and Google Places backends).
3. **Souls-lite:** each resident has a `SOUL.md`-style persona (Hermes
   profiles already have `SOUL.md`) plus an affinity score per resident pair.
   It goes up when they collaborate (share a Run) and nudges the chatter
   lines.

Restaurant-flavoured ideas:

- **Hermes skill `restaurant-scout`** (`skills/restaurant-scout/SKILL.md`):
  "find me 4★+ italian near X". It calls
  `python -m restaurant_scraper.main ... --format json`.
- **Daily cron "Lunch roulette":** Hermes picks a random open restaurant within
  1 km and posts it to our chat. The Trigger → Delivery chain is fully
  traceable.
- **Taste memory:** feed likes and dislikes back into Hermes `MEMORY.md`, so
  suggestions improve over time.

## Next steps

- [x] Study the Nexus Village reference (above)
- [x] Decide on a renderer: terminal first, then three.js
- [x] Write `village_state.py`: Hermes state → `VillageSnapshot` JSON
- [x] Build the terminal village (`village_tui.py`)
- [ ] Build the 3D village (three.js) on top of `--json`
- [ ] Add Case/robots (kanban) and Souls-lite
- [ ] Add a `--format json` path that is stable for agent use (already exists,
      but needs verifying)
- [ ] Write the `restaurant-scout` skill
- [ ] Add a JSONL event emitter (as a new `output/` or `monitoring/` module that
      follows the config-only constants rule)
- [ ] Add the lunch-roulette cron job
