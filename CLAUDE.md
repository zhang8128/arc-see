# arc-see

Perceptual lens system for ARC-AGI-3. An average person finds these puzzles
easy. The bottleneck is understanding the rules — once you get them, solving
is trivial.

## How to play

**Trust the frame, not your memory.** Every call to `perceive()` or `step()`
tells you exactly where everything is right now. Never track positions in
your head — look at the current frame. Your mental arithmetic will drift.
The lenses won't. But do notice things that change *between* frames — a
counter going down, cells disappearing, colors shifting. Those changes are
the rules talking to you.

**Play the game, don't reverse-engineer it.** Do not read the game source
code. Do not try to extract level layouts from Python files. That's cheating
and it doesn't help you understand the rules. Play: step, perceive, observe
what changed. The lenses give you structured information about the board —
use that. The `perceive()` output tells you about regions, movement,
mechanics, resources, and action effects. Read it.

**One level at a time.** Each level can have different rules. Learn the rules
for this level, then solve it — write a script if that helps. But if a script
isn't working, drop it and just play: step, perceive, step, perceive. Look
at what's happening. Don't assume the next level works the same way. What
you learned on level 1 might not apply to level 2.

**Learn the rules first, solve second.** You don't know what the game is yet.
Before trying to win:

1. Try each action once. Watch what happens. What moved? What changed?
2. Form hypotheses: "ACTION1 moves the player up. Walls block movement."
3. Test them: try ACTION1 next to a wall. Did it block? Hypothesis confirmed.
   Try ACTION1 next to a colored object. Did something unexpected happen?
   Hypothesis needs revision.
4. When you hit something surprising — a pickup changes the rules, an action
   does something different in a new context — that's the interesting part.
   That's the actual puzzle.
5. Once you understand the rules, solving is just execution.

**Challenge your hypotheses.** Don't assume. "I think green is the goal" —
walk into it and see. "I think walls always block" — maybe a pickup lets you
pass through. Spend early lives learning, not winning.

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
- `learn(insight, level, category)` — record a rule or hypothesis. Tag with the level number, or -1 for game-wide rules
- `recall(level?)` — read back what you've learned, grouped by level
- `forget(substring)` — remove a hypothesis that turned out wrong
- `level_summary(level, summary)` — record what a level is about in one line
- `level_map()` — bird's-eye view of all levels

To change games, edit the game_id in `.mcp.json`.

## Session state

Durable session knowledge (what you learn via tools) is stored per game at
`journals/{game_base}.json` in this repo (e.g., `journals/re86.json`). The
`game_base` is the `game_id` from `.mcp.json` up to the first `-`.

- Update: use `learn(insight, level, category)`, `level_summary(level, summary)`,
  and `forget(substring)` — these write to the journal file.
- Read: use `recall(level?)` and `level_map()` — these read from the journal.
- Lifecycle: persists across context compaction and MCP restarts; `reset()`
  only clears in‑memory episode state, not the journal.
- Switch games: change `.mcp.json` `game_id` and restart the session; the
  journal path updates automatically to the new `{game_base}.json`.

## Key Files

| File | Role |
|------|------|
| `arc_see/lenses/` | 13 primitive lenses: spatial, temporal, structural, relational, goal |
| `arc_see/composer.py` | Pairwise combination scoring via entropy reduction |
| `arc_see/session.py` | GameSession — state container with text-based perception/action |
| `arc_see/mcp_server.py` | MCP server — exposes session methods as tools |
| `.mcp.json` | Claude Code MCP server config |
