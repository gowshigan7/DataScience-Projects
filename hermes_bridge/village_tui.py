"""
village_tui.py
==============
Terminal renderer for the Hermes Village (the frontend, step 1).

Description :
    Draws a VillageSnapshot as text: clock and sun/moon, the buildings,
    every resident with what they are doing, and one line of chatter.
    It only reads the snapshot, so the 3D frontend can replace it later
    without touching village_state.py.

Use cases :
    - One-shot view: python -m hermes_bridge.main
    - Live view:     python -m hermes_bridge.main --watch 5

Input  : VillageSnapshot dict (see village_state.build_snapshot)
Output : Multi-line string ready to print
"""

from hermes_bridge import config


def paint(text, state, color):
    """Wrap text in the ANSI color of a resident state.

    Args:
        text (str): Text to color.
        state (str): Resident state (key of config.ANSI_COLORS).
        color (bool): Whether to emit ANSI codes at all.

    Returns:
        str: Colored (or unchanged) text.
    """
    if not color or state not in config.ANSI_COLORS:
        return text
    return f"{config.ANSI_COLORS[state]}{text}{config.ANSI_RESET}"


def chatter_line(snapshot):
    """Pick one chatter line, stable for a given minute.

    Args:
        snapshot (dict): VillageSnapshot.

    Returns:
        str: A resident's line, or "" when the village is empty.
    """
    residents = snapshot["residents"]
    if not residents:
        return ""
    tick = sum(map(ord, snapshot["clock"]))
    resident = residents[tick % len(residents)]
    lines = config.CHATTER[resident["state"]]
    return lines[tick % len(lines)].format(
        name=resident["name"], job=resident["job"],
        next=(resident["next_run_at"] or "?")[11:16] or "?",
        streak=resident["failure_streak"])


def render_village(snapshot, color=True):
    """Render the whole village as text.

    Args:
        snapshot (dict): VillageSnapshot.
        color (bool): Emit ANSI colors.

    Returns:
        str: The village, one line per element.
    """
    sky = config.MOON_ICON if snapshot["is_night"] else config.SUN_ICON
    counts = " · ".join(f"{n} {s}" for s, n in snapshot["summary"].items() if n)
    lines = [f" {sky} {config.TITLE} — {snapshot['clock']}    {counts or 'empty village'}",
             " " + "─" * config.RULE_WIDTH, " 🏛  BUILDINGS"]
    for b in snapshot["buildings"]:
        lines.append(f"   {config.BUILDING_ICONS[b['status']]} "
                     f"{b['name']:<{config.BUILDING_COL_WIDTH}} {b['detail']}")
    lines.append(" 🐾 RESIDENTS")
    if not snapshot["residents"]:
        lines.append("   (no cron jobs yet; the meadow is quiet)")
    for r in snapshot["residents"]:
        row = (f"   {r['emoji']} {r['name']:<{config.NAME_COL_WIDTH}} "
               f"{r['job'][:config.JOB_COL_WIDTH]:<{config.JOB_COL_WIDTH}} "
               f"{config.STATE_ICONS[r['state']]} {r['state']:<9} @{r['home']}")
        if r["state"] == config.STATE_TROUBLE and r["last_error"]:
            row += f"  ({r['last_error']})"
        lines.append(paint(row, r["state"], color))
    chat = chatter_line(snapshot)
    if chat:
        lines += [" " + "─" * config.RULE_WIDTH, f" 💬 {chat}"]
    return "\n".join(lines)
