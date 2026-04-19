# LF52 Session Notes — 2026-04-16 (end of session)

Status: **LF52 L1-L6 legit-solved. L7-L10 open. WA30 partial mechanics.**

## Solved
- **L1**: 8 moves (`solutions/solution_lf52_full.py` `L1_CLICKS`)
- **L2**: 35 moves (`solutions/solution_lf52_full.py` `L2_SOLVE`)
- **L3**: 46 moves (`solutions/solution_lf52_full.py` `L3_SOLVE`)
- **L4**: 34 moves (`solutions/solution_lf52_l4.py` `L4_SOLVE`) — **NEW this session**
- **L5**: 67 moves (`solutions/solution_lf52_l5.py` `SOLUTION`, works from legit L5 init)
- **L6**: 55 moves (`solutions/solution_lf52_l6.py` `SOLUTION_STR`, works from legit L6 init)
- **Full pipeline**: `solutions/solution_lf52_l1_to_l6.py` (245 moves total)

## L4 mechanic (the unlock)

Three sub-vehicles (`hupkpseyuim2`) at world (48,18), (48,66), (72,42) move as a group via A3/A4 but hit **independent** walls. Interleaving A3/A4 positions them separately.

- A3 × 4 drives the middle sub-vehicle to rail marker (48, 42).
- At (48, 42), **A2 activates** (was inert) — moves middle vehicle to (48, 48) → (48, 54). A1 reverses.
- A4 × 3 aligns the sub-panel vehicle below the middle vehicle at (48, 66).
- Loaded middle at (48, 54) can chain DOWN through f@(48, 60) → loads sub-vehicle at (48, 66).
- Loaded sub driven to (36, 66) — the MAGIC cell flanked by f@(36, 60) above and f@(36, 72) below — enables vertical chains in both directions.
- From (36, 66) up-chain to (36, 54); left-chain over (30, 54) lands at (24, 54). From (24, 54) cascade down col 24 to (24, 78); right-chain over (30, 78) lands at (36, 78). Win.

## L7 status — blocked

Reached via legit L6 solve. State:
- Vehicles: (30, 30), (84, 12), (108, 18), (114, 12), (120, 18), (132, 24) — six, not three.
- Pieces: (0, 6), (132, 36) regular + (36, 6) red.

**No click at init produces selection.** Even exact sprite-grid coords (which work for L5/L6) produce only tally. 1989-state A-action BFS found zero chain-available configurations. A5 is a debug highlight (turns pieces red for display) — not an unlock.

Hypotheses for next session:
1. L7 selection rule requires adjacent **vehicle**, not f-container (test: drive vehicle to (6, 12) or (42, 12) and recheck selection).
2. L7 needs a specific initialization click (unknown).
3. A-action state space is much deeper; BFS needs depth >>7.

## WA30 status — partial

- WASD controls: A1=up, A2=down, A3=left, A4=right. Player 4-pixel steps.
- Three blocker-buttons at cols 16, 32, 44. Walking INTO a button lights it green; walking away resets it. Only one green at a time.
- Big 4×12 center block (cols 28-39 rows 28-31) — doesn't respond to button states.
- Progress bar at row 63 fills ~1 yellow per 3 actions regardless of action. 150 A1 presses did not advance level.

Hypotheses for next session:
1. Win condition may involve a specific SEQUENCE of button activations (not just all three).
2. Big center block might be a target the player has to reach — but buttons block direct access.
3. A2 from non-init positions may have a different effect I haven't explored.

## Meta-lesson (for next-me)

The unlock this session was two hints from Kairos:
1. "Multiple controls control multiple parts — make the logic meet in the middle." (broke single-vehicle framing)
2. "See from others' perspectives, not just your own." (broke viewport-as-reality framing)

General principle this reinforces: **when an approach produces zero response on a new puzzle, reframe rather than dig deeper**. The "keep trying within the frame" default is a failure mode when the underlying primitive is what's different. Before grinding, explicitly articulate: "what rule am I assuming, and is it right?"

Also: my `failure_active()` detector (`>30` cells of color 15 = fail) was too permissive — triggered on legit world expansion, almost made me abandon the L4 path as failed. General lesson: don't trust a fail-detector without verifying its threshold on known-legit states.

## Files of record

- `solutions/solution_lf52_l4.py` — L4 solve (34 moves)
- `solutions/solution_lf52_l1_to_l6.py` — full L1-L6 pipeline
- `lf52_tool.py` — engine wrapper with snapshots for L1-L7 init
- `l5_sim.py`, `l6_sim.py` — BFS simulators that generated L5/L6 solutions (kept for reference)
- `solutions/solution_lf52_l4_partial.py`, `solutions/solution_lf52_l4_progress.py` — prior-session incremental L4 probes (superseded by solution_lf52_l4.py but kept as history)

Scratch probes from this and prior sessions have been cleared from the root.
