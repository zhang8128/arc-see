"""MCP server — exposes ARC-AGI-3 lenses and game actions as tools for Claude."""

from __future__ import annotations

import sys
import arc_agi
from mcp.server.fastmcp import FastMCP

from arc_see.session import GameSession

mcp = FastMCP("arc-see")

_session: GameSession | None = None


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


def main():
    game_id = sys.argv[1] if len(sys.argv) > 1 else None
    if game_id is None:
        print("Usage: python -m arc_see.mcp_server <game_id>", file=sys.stderr)
        sys.exit(1)

    global _session
    arcade = arc_agi.Arcade()
    env = arcade.make(game_id, render_mode=None)
    if env is None:
        print(f"Failed to create environment for {game_id}", file=sys.stderr)
        sys.exit(1)

    _session = GameSession(env)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
