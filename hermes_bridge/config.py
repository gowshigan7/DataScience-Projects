"""
config.py
=========
Central configuration for hermes_bridge (the Hermes Village).

Description :
    Every constant and tunable value of the village lives here. No other
    module hardcodes paths, time windows, species, icons or chatter lines.

Use cases :
    - Point the village at another Hermes home
    - Change how long a resident "stays at work" after a quick job
    - Add species, icons or chatter lines

Input  : None (constants file)
Output : Variables imported by the other modules
"""

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Hermes home and files we read (read-only, never written)
# ---------------------------------------------------------------------------

HERMES_HOME = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
CRON_JOBS_RELPATH = Path("cron") / "jobs.json"
GATEWAY_STATE_RELPATH = Path("gateway_state.json")
PROFILES_DIRNAME = "profiles"
DEFAULT_PROFILE = "default"

# ---------------------------------------------------------------------------
# Village rules
# ---------------------------------------------------------------------------

# A job counts as "working" this long after its last run, so quick jobs still show.
WORK_WINDOW_MINUTES = 5
NIGHT_START_HOUR = 22
NIGHT_END_HOUR = 7
WATCH_DEFAULT_SECONDS = 5

# Resident states (ontology: Resident.states)
STATE_WORKING = "working"
STATE_IDLE = "idle"
STATE_SLEEPING = "sleeping"
STATE_TROUBLE = "trouble"
RESIDENT_STATES = (STATE_WORKING, STATE_IDLE, STATE_SLEEPING, STATE_TROUBLE)

# Building states (ontology: Building.states)
BUILDING_UP = "up"
BUILDING_DOWN = "down"
BUILDING_ERROR = "error"

# Hermes values we map from
HERMES_STATUS_ERROR = "error"
HERMES_JOB_PAUSED = "paused"
HERMES_PLATFORM_CONNECTED = "connected"
HERMES_GATEWAY_RUNNING = "running"
HERMES_GATEWAY_STARTING = "starting"

# ---------------------------------------------------------------------------
# Cast: (species, emoji, name), picked deterministically from the job id
# ---------------------------------------------------------------------------

SPECIES = (
    ("fox", "🦊", "Fennel"), ("badger", "🦡", "Bruno"), ("otter", "🦦", "Ottilie"),
    ("beaver", "🦫", "Timber"), ("tortoise", "🐢", "Tilda"), ("corgi", "🐕", "Biscuit"),
    ("hedgehog", "🦔", "Spike"), ("owl", "🦉", "Olive"), ("rabbit", "🐇", "Rosie"),
    ("raccoon", "🦝", "Rocco"),
)

STATE_ICONS = {
    STATE_WORKING: "⚒ ",
    STATE_IDLE: "🏡",
    STATE_SLEEPING: "💤",
    STATE_TROUBLE: "🔥",
}
BUILDING_ICONS = {BUILDING_UP: "🟢", BUILDING_DOWN: "⚫", BUILDING_ERROR: "🔴"}
SUN_ICON = "☀ "
MOON_ICON = "🌙"

CHATTER = {
    STATE_WORKING: ("{name}: busy busy, {job} won't run itself!",
                    "{name}: almost done with {job}, then fishing."),
    STATE_IDLE: ("{name}: anyone up for boule by the pond?",
                 "{name}: next shift at {next}. Time for a snack."),
    STATE_SLEEPING: ("{name}: zzz… dreaming of {job}…",),
    STATE_TROUBLE: ("{name}: uh-oh, {job} went wrong ({streak}x). Help?",),
}

# ---------------------------------------------------------------------------
# Terminal rendering
# ---------------------------------------------------------------------------

TITLE = "Hermes Village"
RULE_WIDTH = 64
NAME_COL_WIDTH = 10
JOB_COL_WIDTH = 22
BUILDING_COL_WIDTH = 16
ANSI_CLEAR = "\033[2J\033[H"
ANSI_COLORS = {
    STATE_WORKING: "\033[33m", STATE_IDLE: "\033[32m",
    STATE_SLEEPING: "\033[2m", STATE_TROUBLE: "\033[31m",
}
ANSI_RESET = "\033[0m"
