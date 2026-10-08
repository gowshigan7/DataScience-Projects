"""
demo_data.py
============
Simulated Hermes state for --demo and for the tests.

Description :
    Mirrors the real shapes of ~/.hermes/cron/jobs.json and
    gateway_state.json (field names taken from hermes-agent), with times
    relative to "now" so every state shows up: working, idle, paused,
    in trouble, and a platform in error.

Use cases :
    - python -m hermes_bridge.main --demo   (no Hermes install needed)
    - Fixtures for tests/test_village.py

Input  : A reference datetime
Output : (jobs_by_profile, gateway_state) tuple
"""

from datetime import timedelta


def demo_hermes(now):
    """Build a simulated Hermes home in memory.

    Args:
        now (datetime): Reference time (aware); job times are relative to it.

    Returns:
        tuple[dict, dict]: ({profile: [job, ...]}, gateway_state dict).
    """
    def ago(minutes):
        return (now - timedelta(minutes=minutes)).isoformat()

    jobs_by_profile = {
        "default": [
            {"id": "a1f0", "name": "mail-digest", "schedule_display": "every 15m",
             "enabled": True, "state": "scheduled", "last_run_at": ago(1),
             "next_run_at": ago(-14), "last_status": "ok", "failure_streak": 0},
            {"id": "b2c1", "name": "lunch-roulette", "schedule_display": "0 12 * * 1-5",
             "enabled": True, "state": "scheduled", "last_run_at": ago(180),
             "next_run_at": ago(-1260), "last_status": "ok", "failure_streak": 0},
            {"id": "c3d2", "name": "restaurant-scout", "schedule_display": "every 1h",
             "enabled": True, "state": "scheduled", "last_run_at": ago(30),
             "next_run_at": ago(-30), "last_status": "error",
             "last_error": "Overpass API timeout", "failure_streak": 2},
        ],
        "coder": [
            {"id": "d4e3", "name": "nightly-tests", "schedule_display": "0 3 * * *",
             "enabled": False, "state": "paused", "last_run_at": ago(900),
             "next_run_at": None, "last_status": "ok", "failure_streak": 0},
            {"id": "e5f4", "name": "repo-watch", "schedule_display": "every 5m",
             "enabled": True, "state": "scheduled", "last_run_at": ago(3),
             "next_run_at": ago(-2), "last_status": "ok", "failure_streak": 0},
        ],
    }
    gateway = {
        "gateway_state": "running",
        "active_agents": 2,
        "exit_reason": None,
        "platforms": {
            "telegram": {"state": "connected"},
            "signal": {"state": "connected"},
            "discord": {"state": "retrying", "error_code": "auth",
                        "error_message": "invalid token"},
        },
    }
    return jobs_by_profile, gateway
