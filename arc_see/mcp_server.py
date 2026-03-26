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

    Clears frame history and turn counter. Preserves learned game semantics
    (player color, goal color, physics, action directions) across resets.

    Returns the same output as perceive() on the fresh frame.
    """
    return _get_session().reset()


@mcp.tool()
def status() -> str:
    """Quick check: game state, turns, levels, score, available actions."""
    return _get_session().status()


@mcp.tool()
def learn(insight: str, category: str = "mechanic") -> str:
    """Record a durable insight that survives context compaction.

    Write what you've learned about the game. This persists to disk
    and is returned by recall(). Use it for:
    - Game mechanics: "ACTION1=up, ACTION2=down"
    - Strategies: "collect pickups when <10 turns remain"
    - Hypotheses: "green cells might be time extensions"
    - Level patterns: "level 2 adds diagonal movement"

    Args:
        insight: What you learned. Be specific and actionable.
        category: One of "mechanic", "strategy", "hypothesis", "observation"
    """
    entry = {
        "insight": insight,
        "category": category,
        "turn": _get_session().total_turns,
        "level": _get_session().levels_completed,
        "timestamp": datetime.now().isoformat(),
    }

    entries = _load_journal()
    entries.append(entry)
    _save_journal(entries)

    return f"Learned: [{category}] {insight}"


@mcp.tool()
def recall() -> str:
    """Read back everything learned so far across all sessions.

    Call this after context compaction or at the start of a session
    to recover your accumulated knowledge about the game.

    Returns all insights organized by category.
    """
    entries = _load_journal()
    if not entries:
        return "No insights recorded yet. Use learn() to record what you discover."

    by_category: dict[str, list[dict]] = {}
    for e in entries:
        cat = e.get("category", "observation")
        by_category.setdefault(cat, []).append(e)

    parts = ["## Game Knowledge (durable — survives compaction)\n"]
    for cat in ["mechanic", "strategy", "hypothesis", "observation"]:
        if cat not in by_category:
            continue
        parts.append(f"### {cat.title()}s")
        for e in by_category[cat]:
            level_info = f" (level {e.get('level', '?')}, turn {e.get('turn', '?')})"
            parts.append(f"- {e['insight']}{level_info}")
        parts.append("")

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
