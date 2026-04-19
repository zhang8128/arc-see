"""MCP server — exposes ARC-AGI-3 lenses and game actions as tools for Claude."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime

import arc_agi
from mcp.server.fastmcp import FastMCP

from arc_see.session import GameSession

mcp = FastMCP("arc-see")

_session: GameSession | None = None
_journal_path: str = ""


def _get_session() -> GameSession:
    if _session is None:
        raise RuntimeError("No game loaded. Start the server with a game_id argument.")
    return _session


@mcp.tool()
def perceive() -> str:
    """Run all 13 perceptual lenses on the current frame.

    Returns structured annotations: spatial (components, edges, enclosure),
    structural (symmetry, periodicity, alignment), temporal (movement, changes),
    relational (proximity, colors, sizes), goal detection, game semantics
    (player/goal/walls), and a compact grid visualization.

    Call this after reset() or step() to understand the current board state.
    """
    return _get_session().perceive()


@mcp.tool()
def step(action: str, x: int | None = None, y: int | None = None) -> str:
    """Take a game action and see what happens.

    Args:
        action: One of the available actions (e.g. ACTION1, ACTION2, ...).
        x: X coordinate for click actions (optional).
        y: Y coordinate for click actions (optional).

    Returns what changed: player movement, cells changed, game state, turns used.
    Automatically detects player color, movement direction, and physics model.
    """
    return _get_session().step(action, x, y)


@mcp.tool()
def reflect() -> str:
    """Summarize everything learned in this game session.

    Returns: turns used, actions tried and their effects, inferred physics,
    player/goal positions, direction to goal, top lens combinations,
    and stuck detection warnings.
    """
    return _get_session().reflect()


@mcp.tool()
def reset() -> str:
    """Reset the current level and get a fresh perception.

    Clears everything — frame history, turn counter, and inferred game
    semantics (player color, goal color, physics). Each level starts clean.

    Returns the same output as perceive() on the fresh frame.
    """
    return _get_session().reset()


@mcp.tool()
def status() -> str:
    """Quick check: game state, turns, levels, score, available actions."""
    return _get_session().status()


@mcp.tool()
def learn(insight: str, level: int, category: str = "mechanic") -> str:
    """Record a durable insight that survives context compaction.

    Write what you've learned about the game. This persists to disk
    and is returned by recall(). Use it for:
    - Game mechanics: "ACTION1=up, ACTION2=down"
    - Strategies: "collect pickups when <10 turns remain"
    - Hypotheses: "green cells might be time extensions"
    - Level patterns: "level 2 adds diagonal movement"

    Args:
        insight: What you learned. Be specific and actionable.
        level: Which level this applies to. Use -1 for game-wide rules.
        category: One of "mechanic", "strategy", "hypothesis", "observation"
    """
    entry = {
        "insight": insight,
        "category": category,
        "turn": _get_session().total_turns,
        "level": level,
        "timestamp": datetime.now().isoformat(),
    }

    entries = _load_journal()
    entries.append(entry)
    _save_journal(entries)

    return f"Learned: [{category}] L{level}: {insight}"


@mcp.tool()
def recall(level: int | None = None) -> str:
    """Read back everything learned, organized by level.

    Call this after context compaction or at the start of a session
    to recover your accumulated knowledge about the game.

    Args:
        level: If set, show only insights for this level. Otherwise show all.

    Returns insights grouped by level, then by category within each level.
    """
    entries = _load_journal()
    if not entries:
        return "No insights recorded yet. Use learn() to record what you discover."

    # Group by level
    by_level: dict[int, list[dict]] = {}
    for e in entries:
        lvl = e.get("level", 0)
        by_level.setdefault(lvl, []).append(e)

    parts = ["## Game Knowledge (durable — survives compaction)\n"]

    levels_to_show = [level] if level is not None else sorted(by_level.keys())

    for lvl in levels_to_show:
        if lvl not in by_level:
            parts.append(f"### Level {lvl}\nNo insights recorded.\n")
            continue
        level_entries = by_level[lvl]
        header = "Game-wide" if lvl == -1 else f"Level {lvl}"
        parts.append(f"### {header}")

        # Group by category within level
        by_cat: dict[str, list[dict]] = {}
        for e in level_entries:
            cat = e.get("category", "observation")
            if cat == "summary":
                continue  # shown by level_map()
            by_cat.setdefault(cat, []).append(e)

        for cat in ["mechanic", "strategy", "hypothesis", "observation"]:
            if cat not in by_cat:
                continue
            parts.append(f"**{cat.title()}s:**")
            for e in by_cat[cat]:
                parts.append(f"- {e['insight']}")
        parts.append("")

    return "\n".join(parts)


@mcp.tool()
def level_summary(level: int, summary: str) -> str:
    """Record a one-line summary of what a level is about.

    Call this when you've figured out a level's core mechanic.
    These summaries form the level map — a bird's-eye view of the game.

    Args:
        level: The level number.
        summary: One line — what makes this level tick. e.g. "push maze with moving pickups"
    """
    entries = _load_journal()
    # Remove any existing summary for this level
    entries = [e for e in entries if not (e.get("category") == "summary" and e.get("level") == level)]
    entries.append({
        "insight": summary,
        "category": "summary",
        "level": level,
        "turn": _get_session().total_turns,
        "timestamp": datetime.now().isoformat(),
    })
    _save_journal(entries)
    return f"Level {level}: {summary}"


@mcp.tool()
def level_map() -> str:
    """Show the bird's-eye level map — one-line summary per level.

    Call this to see what you know about the overall game structure.
    """
    entries = _load_journal()
    summaries = {e["level"]: e["insight"] for e in entries if e.get("category") == "summary"}
    if not summaries:
        return "No level summaries yet. Use level_summary() after understanding each level."
    parts = ["## Level Map\n"]
    for lvl in sorted(summaries.keys()):
        parts.append(f"- **Level {lvl}:** {summaries[lvl]}")
    return "\n".join(parts)


@mcp.tool()
def forget(insight_substring: str) -> str:
    """Remove a learned insight that turned out to be wrong.

    Args:
        insight_substring: Part of the insight text to match and remove.
    """
    entries = _load_journal()
    before = len(entries)
    entries = [e for e in entries if insight_substring.lower() not in e["insight"].lower()]
    after = len(entries)
    _save_journal(entries)
    removed = before - after
    return f"Removed {removed} insight(s) matching '{insight_substring}'."


def _load_journal() -> list[dict]:
    if not _journal_path or not os.path.exists(_journal_path):
        return []
    with open(_journal_path) as f:
        return json.load(f)


def _save_journal(entries: list[dict]) -> None:
    if not _journal_path:
        return
    os.makedirs(os.path.dirname(_journal_path), exist_ok=True)
    with open(_journal_path, "w") as f:
        json.dump(entries, f, indent=2)


def main():
    game_id = sys.argv[1] if len(sys.argv) > 1 else None
    if game_id is None:
        print("Usage: python -m arc_see.mcp_server <game_id>", file=sys.stderr)
        sys.exit(1)

    global _session, _journal_path
    arcade = arc_agi.Arcade()
    env = arcade.make(game_id, render_mode=None)
    if env is None:
        print(f"Failed to create environment for {game_id}", file=sys.stderr)
        sys.exit(1)

    # Journal lives next to the game files, persists across sessions
    game_base = game_id.split("-")[0]  # "ls20-abc123" -> "ls20"
    _journal_path = os.path.join(
        os.path.dirname(__file__), "..", "journals", f"{game_base}.json"
    )
    _journal_path = os.path.normpath(_journal_path)

    _session = GameSession(env)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
