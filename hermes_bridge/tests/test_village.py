"""
test_village.py
===============
Unit tests for the Hermes Village (state mapping + terminal rendering).

Description :
    Uses the simulated Hermes home from demo_data.py and small inline job
    dicts. No network, no files written, nothing read from a real ~/.hermes.

Input  : demo_data.demo_hermes, inline fixtures
Output : pytest assertions
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from hermes_bridge import config
from hermes_bridge.demo_data import demo_hermes
from hermes_bridge.main import main
from hermes_bridge.village_state import (
    assign_cast, build_snapshot, gateway_to_buildings, load_hermes_home,
    normalize_jobs, resident_state,
)
from hermes_bridge.village_tui import render_village

NOON = datetime(2026, 10, 8, 12, 0, tzinfo=timezone.utc)
MIDNIGHT = datetime(2026, 10, 8, 23, 30, tzinfo=timezone.utc)


def by_job(snapshot):
    """Index residents by job name.

    Args:
        snapshot (dict): VillageSnapshot.

    Returns:
        dict: {job name: resident}.
    """
    return {r["job"]: r for r in snapshot["residents"]}


def test_demo_snapshot_covers_every_state():
    snap = build_snapshot(*demo_hermes(NOON), now=NOON)
    r = by_job(snap)
    assert r["mail-digest"]["state"] == config.STATE_WORKING
    assert r["lunch-roulette"]["state"] == config.STATE_IDLE
    assert r["restaurant-scout"]["state"] == config.STATE_TROUBLE
    assert r["nightly-tests"]["state"] == config.STATE_SLEEPING
    assert r["nightly-tests"]["home"] == "coder"
    assert sum(snap["summary"].values()) == len(snap["residents"]) == 5


def test_snapshot_is_json_serialisable():
    snap = build_snapshot(*demo_hermes(NOON), now=NOON)
    assert json.loads(json.dumps(snap))["clock"] == "12:00"


def test_idle_resident_sleeps_at_night():
    job = {"id": "x", "enabled": True, "last_run_at": (NOON - timedelta(hours=2)).isoformat()}
    assert resident_state(job, MIDNIGHT) == config.STATE_SLEEPING
    assert resident_state(job, NOON) == config.STATE_IDLE


def test_quick_job_stays_at_work_for_window():
    just_ran = {"id": "x", "last_run_at": (NOON - timedelta(minutes=config.WORK_WINDOW_MINUTES - 1)).isoformat()}
    long_ago = {"id": "x", "last_run_at": (NOON - timedelta(minutes=config.WORK_WINDOW_MINUTES + 1)).isoformat()}
    assert resident_state(just_ran, NOON) == config.STATE_WORKING
    assert resident_state(long_ago, NOON) == config.STATE_IDLE


def test_naive_and_bad_timestamps_are_tolerated():
    naive = {"id": "x", "last_run_at": NOON.replace(tzinfo=None).isoformat()}
    assert resident_state(naive, NOON) == config.STATE_WORKING
    assert resident_state({"id": "x", "last_run_at": "not a date"}, NOON) == config.STATE_IDLE


def test_cast_is_unique_and_stable():
    ids = [f"job{i}" for i in range(len(config.SPECIES) + 3)]
    cast = assign_cast(ids)
    names = [c[2] for c in cast.values()]
    assert len(set(names)) == len(names)
    assert assign_cast(list(reversed(ids))) == cast


def test_normalize_jobs_accepts_hermes_shapes():
    assert normalize_jobs({"jobs": [{"id": "a"}, "junk"]}) == [{"id": "a"}]
    assert normalize_jobs({"jobs": {"b": {"name": "n"}}}) == [{"name": "n", "id": "b"}]
    assert normalize_jobs([{"id": "c"}]) == [{"id": "c"}]
    assert normalize_jobs(None) == [] and normalize_jobs({"jobs": 3}) == []


def test_gateway_buildings():
    _, gateway = demo_hermes(NOON)
    status = {b["name"]: b["status"] for b in gateway_to_buildings(gateway)}
    assert status == {"Gateway": config.BUILDING_UP, "Discord": config.BUILDING_ERROR,
                      "Signal": config.BUILDING_UP, "Telegram": config.BUILDING_UP}
    assert gateway_to_buildings(None)[0]["status"] == config.BUILDING_DOWN
    crashed = gateway_to_buildings({"gateway_state": "stopped", "exit_reason": "watchdog"})
    assert crashed[0]["status"] == config.BUILDING_ERROR


def test_missing_hermes_home_is_an_empty_village():
    jobs, gateway = load_hermes_home(Path("/nonexistent/hermes-home"))
    assert jobs == {"default": []} and gateway is None
    snap = build_snapshot(jobs, gateway, now=NOON)
    assert "the meadow is quiet" in render_village(snap, color=False)


def test_render_shows_residents_buildings_and_errors():
    text = render_village(build_snapshot(*demo_hermes(NOON), now=NOON), color=False)
    assert config.TITLE in text and "12:00" in text
    assert "restaurant-scout" in text and "Overpass API timeout" in text
    assert "Discord" in text and "💬" in text
    assert "\033[" not in text


def test_render_colors_and_night_sky():
    text = render_village(build_snapshot(*demo_hermes(MIDNIGHT), now=MIDNIGHT), color=True)
    assert config.MOON_ICON in text and config.ANSI_RESET in text


def test_cli_demo_json(capsys):
    main(["--demo", "--json"])
    snap = json.loads(capsys.readouterr().out)
    assert len(snap["residents"]) == 5 and snap["buildings"]
