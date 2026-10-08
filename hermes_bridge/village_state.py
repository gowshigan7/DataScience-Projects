"""
village_state.py
================
Turns Hermes state into a VillageSnapshot (the backend of the village).

Description :
    Reads ~/.hermes (cron jobs of every profile, gateway_state.json) and maps
    it onto the village layer of ontology.yaml: each cron job becomes a
    Resident, the gateway and each chat platform become Buildings. The
    mapping itself (build_snapshot) is pure, so any renderer (terminal now,
    3D later) consumes the same JSON-ready dict.

Use cases :
    - Feed the terminal village (village_tui.py)
    - Serve the same snapshot to a future three.js frontend

Input  : A Hermes home directory, or already-loaded jobs/gateway dicts
Output : VillageSnapshot dict: {generated_at, clock, is_night, residents,
         buildings, summary}
"""

import json
import zlib
from datetime import datetime, timedelta

from hermes_bridge import config


def load_json(path):
    """Read a JSON file, tolerating a missing or broken file.

    Args:
        path (Path): File to read.

    Returns:
        Any: Parsed JSON, or None when the file is missing or unreadable.
    """
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.loads(f.read(), strict=False)
    except (OSError, ValueError):
        return None


def normalize_jobs(data):
    """Accept the shapes Hermes tolerates for jobs.json and return a list.

    Args:
        data (Any): Parsed jobs.json ({"jobs": [...]}, {"jobs": {id: job}} or [...]).

    Returns:
        list[dict]: Job dicts (non-dict entries dropped).
    """
    jobs = data.get("jobs", []) if isinstance(data, dict) else data
    if isinstance(jobs, dict):
        jobs = [{**v, "id": v.get("id") or k} for k, v in jobs.items() if isinstance(v, dict)]
    if not isinstance(jobs, list):
        return []
    return [j for j in jobs if isinstance(j, dict)]


def load_hermes_home(home=None):
    """Load cron jobs (per profile) and gateway state from a Hermes home.

    Args:
        home (Path | None): Hermes home; defaults to config.HERMES_HOME.

    Returns:
        tuple[dict, dict | None]: ({profile: [job, ...]}, gateway_state or None).
    """
    home = home or config.HERMES_HOME
    jobs_by_profile = {config.DEFAULT_PROFILE: normalize_jobs(load_json(home / config.CRON_JOBS_RELPATH))}
    profiles_dir = home / config.PROFILES_DIRNAME
    if profiles_dir.is_dir():
        for profile in sorted(p for p in profiles_dir.iterdir() if p.is_dir()):
            jobs = normalize_jobs(load_json(profile / config.CRON_JOBS_RELPATH))
            if jobs:
                jobs_by_profile[profile.name] = jobs
    gateway = load_json(home / config.GATEWAY_STATE_RELPATH)
    return jobs_by_profile, gateway if isinstance(gateway, dict) else None


def parse_time(value, now):
    """Parse a Hermes ISO timestamp; naive values take now's timezone.

    Args:
        value (str | None): ISO 8601 timestamp.
        now (datetime): Timezone-aware reference time.

    Returns:
        datetime | None: Aware datetime, or None if missing/invalid.
    """
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(str(value))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=now.tzinfo)


def is_night(now):
    """Tell whether the village is asleep at this hour.

    Args:
        now (datetime): Current time.

    Returns:
        bool: True between NIGHT_START_HOUR and NIGHT_END_HOUR.
    """
    return now.hour >= config.NIGHT_START_HOUR or now.hour < config.NIGHT_END_HOUR


def assign_cast(job_ids):
    """Give every job a stable, unique character (species, emoji, name).

    The preferred character comes from a hash of the job id; on a clash the
    next free one is taken. Ids are processed sorted so the cast is stable
    across runs. Past len(SPECIES) jobs, names get a number suffix.

    Args:
        job_ids (list[str]): Hermes job ids.

    Returns:
        dict: {job_id: (species, emoji, name)}.
    """
    cast, used = {}, set()
    n = len(config.SPECIES)
    for count, job_id in enumerate(sorted(set(job_ids))):
        start = zlib.crc32(str(job_id).encode()) % n
        idx = next(i % n for i in range(start, start + n) if i % n not in used)
        generation = count // n
        used.add(idx)
        if len(used) == n:
            used.clear()
        species, emoji, name = config.SPECIES[idx]
        cast[job_id] = (species, emoji, f"{name} {generation + 1}" if generation else name)
    return cast


def resident_state(job, now):
    """Map one Hermes cron job onto a Resident state.

    Args:
        job (dict): Hermes job dict.
        now (datetime): Current time (aware).

    Returns:
        str: One of config.RESIDENT_STATES.
    """
    if job.get("last_status") == config.HERMES_STATUS_ERROR:
        return config.STATE_TROUBLE
    if not job.get("enabled", True) or job.get("state") == config.HERMES_JOB_PAUSED:
        return config.STATE_SLEEPING
    last_run = parse_time(job.get("last_run_at"), now)
    if last_run and now - last_run <= timedelta(minutes=config.WORK_WINDOW_MINUTES):
        return config.STATE_WORKING
    return config.STATE_SLEEPING if is_night(now) else config.STATE_IDLE


def job_id_of(job):
    """Return the id used for a job (falls back to its name).

    Args:
        job (dict): Hermes job dict.

    Returns:
        str: Job id.
    """
    return str(job.get("id") or job.get("name") or "?")


def job_to_resident(job, profile, now, character):
    """Build a Resident dict from a Hermes cron job.

    Args:
        job (dict): Hermes job dict.
        profile (str): Hermes profile owning the job (the resident's home).
        now (datetime): Current time (aware).
        character (tuple[str, str, str]): (species, emoji, name) from assign_cast.

    Returns:
        dict: Resident (id, name, species, emoji, job, home, state, ...).
    """
    job_id = job_id_of(job)
    species, emoji, name = character
    return {
        "id": job_id,
        "name": name,
        "species": species,
        "emoji": emoji,
        "job": str(job.get("name") or job_id),
        "home": profile,
        "state": resident_state(job, now),
        "schedule": job.get("schedule_display"),
        "last_run_at": job.get("last_run_at"),
        "next_run_at": job.get("next_run_at"),
        "last_error": job.get("last_error"),
        "failure_streak": job.get("failure_streak") or 0,
    }


def gateway_to_buildings(gateway):
    """Map gateway_state.json onto Buildings: the gateway plus one per platform.

    Args:
        gateway (dict | None): Parsed gateway_state.json.

    Returns:
        list[dict]: Buildings (id, name, kind, status, detail).
    """
    if not gateway:
        return [{"id": "gateway", "name": "Gateway", "kind": "gateway",
                 "status": config.BUILDING_DOWN, "detail": "no gateway_state.json"}]
    g_state = gateway.get("gateway_state")
    if g_state in (config.HERMES_GATEWAY_RUNNING, config.HERMES_GATEWAY_STARTING):
        g_status = config.BUILDING_UP
    else:
        g_status = config.BUILDING_ERROR if gateway.get("exit_reason") else config.BUILDING_DOWN
    buildings = [{"id": "gateway", "name": "Gateway", "kind": "gateway", "status": g_status,
                  "detail": f"{g_state or 'unknown'} · {gateway.get('active_agents') or 0} agents"}]
    platforms = gateway.get("platforms") if isinstance(gateway.get("platforms"), dict) else {}
    for name, info in sorted(platforms.items()):
        info = info if isinstance(info, dict) else {}
        p_state = info.get("state")
        if p_state == config.HERMES_PLATFORM_CONNECTED:
            status, detail = config.BUILDING_UP, p_state
        elif info.get("error_message") or info.get("error_code"):
            status, detail = config.BUILDING_ERROR, f"{p_state or 'error'}: {info.get('error_message') or info.get('error_code')}"
        else:
            status, detail = config.BUILDING_DOWN, p_state or "unknown"
        buildings.append({"id": f"platform:{name}", "name": name.capitalize(),
                          "kind": "platform", "status": status, "detail": detail})
    return buildings


def build_snapshot(jobs_by_profile, gateway, now=None):
    """Build the full VillageSnapshot (pure: no I/O).

    Args:
        jobs_by_profile (dict): {profile: [hermes job, ...]}.
        gateway (dict | None): Parsed gateway_state.json.
        now (datetime | None): Reference time; defaults to local now.

    Returns:
        dict: VillageSnapshot, JSON-serialisable.
    """
    now = now or datetime.now().astimezone()
    pairs = [(profile, job) for profile, jobs in jobs_by_profile.items() for job in jobs]
    cast = assign_cast([job_id_of(job) for _, job in pairs])
    residents = [job_to_resident(job, profile, now, cast[job_id_of(job)]) for profile, job in pairs]
    summary = {state: sum(r["state"] == state for r in residents) for state in config.RESIDENT_STATES}
    return {
        "generated_at": now.isoformat(),
        "clock": now.strftime("%H:%M"),
        "is_night": is_night(now),
        "residents": residents,
        "buildings": gateway_to_buildings(gateway),
        "summary": summary,
    }
