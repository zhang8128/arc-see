# MCP Lens Server Design

**Date:** 2026-03-26
**Status:** Approved

## Problem

The current agent.py uses heuristic action selection (cycle actions, memory graph exploitation) that scored 0/7 levels on LS20 with 129 wasted turns. The bottleneck isn't perception — the 13 lenses correctly identify edges, components, and structure. The bottleneck is reasoning: the heuristic agent can't interpret what it sees into game semantics (player, goal, walls, physics) or form multi-step plans.

## Solution

Replace the heuristic agent with Claude as the reasoning layer. The lenses become MCP tools that a Claude session calls to see and act. Claude reads structured perception, reasons in natural language, and picks actions.

```
Claude Code session
  calls MCP tools to see and act
    perceive() → structured lens annotations as text
    step(action, x?, y?) → new grid + diff summary
    reflect() → lens summary + change history
    reset() → reset level, return initial frame summary
    status() → game state, turns used, levels completed
```

## Architecture

### MCP Server: `arc_see/mcp_server.py`

A stdio MCP server that holds game session state (`Arcade`, `env`, `Composer`, frame history) and exposes 5 tools.

#### Tool: `perceive`

Runs all 13 lenses on the current frame via the existing `Composer.perceive()`. Returns structured text interpreting raw annotations into game-relevant language.

**Input:** None (operates on current frame held in server state).

**Output:** Text summarizing all lens findings, organized by category:

- **Spatial:** connected component count, edge density, enclosure relationships
- **Structural:** symmetry axes, periodicity, alignment grid
- **Temporal:** what moved since last frame, what appeared/disappeared, color changes
- **Relational:** proximity clusters, color-to-object mapping, size distribution
- **Goal:** candidate goal patterns with locations and similarity scores
- **Game semantics** (derived from diffs): player color/position, goal color/position, wall/floor colors, physics type if known

Game semantics are derived by comparing the current frame to the previous frame:
- **Player detection:** The color cluster that relocated between frames when an action was taken. Identified by finding colors that appear in new positions and disappear from old ones across action diffs.
- **Goal detection:** The rarest non-background, non-player, non-wall color with fewer than 20 cells. Validated by checking it doesn't move when actions are taken.
- **Physics detection:** If the player moved more than 1 cell in a single action, physics is SLIDING. If exactly 1 cell, STEPPING. Determined after at least one action has been observed.

#### Tool: `step`

Takes a game action, returns what happened.

**Input:**
- `action` (string, required): One of the actions in the current action space (e.g., "ACTION1", "ACTION2")
- `x` (int, optional): X coordinate for click actions
- `y` (int, optional): Y coordinate for click actions

**Output:** Text summary:
- Action taken and its inferred meaning (e.g., "ACTION1 (UP)" if direction is known)
- Player position before and after, distance moved
- Number of cells changed
- Game state (NOT_FINISHED, WIN, GAME_OVER)
- Turns used so far

Server updates internal state: stores new frame, increments turn counter, updates frame history.

#### Tool: `reflect`

Returns a summary of everything learned so far in the game session.

**Input:** None.

**Output:** Text summary:
- Turns used, levels completed, current game state
- All actions tried and their observed effects (direction, distance moved)
- Inferred physics model (SLIDING/STEPPING/UNKNOWN)
- Player and goal positions, direction from player to goal
- Which actions moved toward vs away from goal
- Which lenses found the most structure (top composer pairs)
- Any stuck detection: "Last N actions produced no state change"

#### Tool: `reset`

Resets the current level.

**Input:** None.

**Output:** Text summary of the fresh frame (same format as perceive output). Clears frame history and turn counter for current level. Preserves cross-level learned state (player color, physics model).

#### Tool: `status`

Lightweight state check.

**Input:** None.

**Output:** Game state, turns used, levels completed, score, action space.

### Server State

The MCP server maintains:
- `arcade`: The `arc_agi.Arcade` instance
- `env`: The current game environment
- `composer`: The `Composer` instance for running lenses
- `frames`: List of all frames seen in current level
- `turn_count`: Actions taken in current level
- `total_turns`: Actions taken across all levels
- `levels_completed`: Count
- `learned`: Persistent dict of learned game semantics (player_color, goal_color, physics, action_directions) that survives resets

### Text Formatting

All tool outputs are plain text with markdown headers. Grids are rendered as compact character maps when included. Annotations are summarized as human-readable sentences, not raw dataclass dumps. The goal is that Claude can read the output and immediately reason about it without parsing structured data.

## Files Changed

| File | Change |
|------|--------|
| `arc_see/mcp_server.py` | **New** — MCP server with 5 tools |
| `arc_see/lenses/` | **Unchanged** — still the perception layer |
| `arc_see/composer.py` | **Unchanged** — still orchestrates lenses |
| `arc_see/agent.py` | **Delete** — Claude replaces this |
| `arc_see/graph.py` | **Delete** — Claude's reasoning replaces memory graph |
| `arc_see/runner.py` | **Delete** — MCP server replaces the runner |
| `tests/` | **Update** — remove agent/graph/runner tests, add MCP server tests |

## Session Flow

A Claude Code session connects to the MCP server and plays a game:

1. Server starts with a game_id, creates Arcade and env
2. Claude calls `reset()` — gets initial frame perception
3. Claude calls `perceive()` — sees the board structure
4. Claude probes: calls `step("ACTION1")`, reads diff, repeats for each action
5. Claude reasons: "This is a sliding puzzle. ACTION1=UP, ACTION2=DOWN..."
6. Claude calls `reset()` — clean slate with learned knowledge
7. Claude plans a path and executes via `step()` calls
8. On WIN, Claude calls `perceive()` on the new level and adapts
9. On GAME_OVER or all levels done, session ends

## Testing

- Unit tests for each MCP tool in isolation (mock the env)
- Integration test: start MCP server, connect, play a sequence of actions, verify outputs
- Existing lens tests remain unchanged

## Out of Scope

- Individual lens tools (just `perceive` bundles all lenses)
- Grid visualization in browser
- Multi-game parallelism
- Persistent learning across game sessions
