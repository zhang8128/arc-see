# arc-see

Perceptual lens system for ARC-AGI-3. The thesis: the bottleneck is seeing, not reasoning.

## Architecture

Lenses are Claude's eyes. Claude is the brain.

13 CV lenses compose pairwise (scored by entropy reduction). An MCP server
exposes the lenses + ARC-AGI-3 API as tools. A Claude session calls perceive()
to see, step() to act, and reasons in natural language between calls.

## Testing

```bash
uv run pytest tests/ -q
```

## Playing a game

Start a Claude Code session in this directory. The `.mcp.json` auto-connects
to the arc-see MCP server (default game: ls20). Claude can then call:

- `reset()` — start/restart level, get initial perception
- `perceive()` — run all lenses, get structured annotations
- `step(action)` — take an action, see what changed
- `reflect()` — summarize what's been learned
- `status()` — quick state check

To change games, edit the game_id in `.mcp.json`.

## Key Files

| File | Role |
|------|------|
| `arc_see/lenses/` | 13 primitive lenses: spatial, temporal, structural, relational, goal |
| `arc_see/composer.py` | Pairwise combination scoring via entropy reduction |
| `arc_see/session.py` | GameSession — state container with text-based perception/action |
| `arc_see/mcp_server.py` | MCP server — exposes session methods as tools |
| `.mcp.json` | Claude Code MCP server config |
