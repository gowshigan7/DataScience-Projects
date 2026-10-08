# Hermes Bridge — monitoring, ontology & fun

Exploratory branch for wiring our projects (starting with `restaurant_scraper`)
into our **Hermes agent** (Nous Research). Inspired by an r/hermesagent post
(https://www.reddit.com/r/hermesagent/s/rQoulVVXAA). Reddit can't be reached
from the build container, so this plan is our own take. Update it once we
compare notes with the post.

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
- **Domain classes:** Restaurant, Cuisine, PriceLevel and Location. These
  mirror the standard dict in `scraper/base_scraper.py`, so a scraper result
  maps 1:1 onto ontology instances.

## 3. Fun

- **Hermes skill `restaurant-scout`** (`skills/restaurant-scout/SKILL.md`):
  "find me 4★+ italian near X". It calls
  `python -m restaurant_scraper.main ... --format json`.
- **Daily cron "Lunch roulette":** Hermes picks a random open restaurant within
  1 km and posts it to our chat. The Trigger → Delivery chain is fully
  traceable.
- **Taste memory:** feed likes and dislikes back into Hermes `MEMORY.md`, so
  suggestions improve over time.

## Next steps

- [ ] Read the Reddit post together and adjust this plan
- [ ] Add a `--format json` path that is stable for agent use (already exists,
      but needs verifying)
- [ ] Write the `restaurant-scout` skill
- [ ] Add a JSONL event emitter (as a new `output/` or `monitoring/` module that
      follows the config-only constants rule)
- [ ] Add the lunch-roulette cron job
