#!/usr/bin/env python3
"""SK48 — Submit via arc_agi with proper env handling."""

import arc_agi
from arcengine import GameAction, GameState
import numpy as np

GA = {
    'U': GameAction.ACTION1,
    'D': GameAction.ACTION2,
    'L': GameAction.ACTION3,
    'R': GameAction.ACTION4,
}

SOLUTIONS = {
    1: "UUURRRRLDDRLUR",
    2: "RRRRUUULLURRDDRURLLURRLLURR",
    3: "RRUUUURDDLDRRRRLLLLUUUURDDDLUUUUR",
    4: "RRUUUULLLLDRURDRURRDLLU",
    5: "LULLRRRRRURRDLLLLDDLDRRRRLURDRLUR",
}

arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)

# Check initial state
obs = env.reset()
print(f"Initial state: {obs.state.name}")
print(f"Available actions: {[a.name for a in env.action_space]}")

# Try L1
print(f"\n=== L1 ===")
for i, c in enumerate(SOLUTIONS[1]):
    obs = env.step(GA[c])
    if i < 3 or obs.state != GameState.NOT_FINISHED:
        print(f"  Step {i+1} ({c}): state={obs.state.name}")

if obs.state == GameState.WIN:
    print("L1 SOLVED!")
else:
    # Maybe the env uses different level data. Let me check.
    grid = np.array(obs.frame[-1], dtype=np.int64)
    print(f"L1 not solved. Grid shape: {grid.shape}")
    # Check what the game looks like
    game = env.unwrapped.game if hasattr(env, 'unwrapped') else env.game
    print(f"Game type: {type(game).__name__}")
    if hasattr(game, '_current_level_index'):
        print(f"Current level: {game._current_level_index}")
    if hasattr(game, 'qiercdohl'):
        print(f"Remaining actions: {game.qiercdohl}")

    # Try getting the game class directly
    if hasattr(env, 'game'):
        g = env.game
    elif hasattr(env, 'unwrapped') and hasattr(env.unwrapped, 'game'):
        g = env.unwrapped.game
    else:
        print("Can't access game object")
        g = None

    if g:
        print(f"\nGame internals:")
        if hasattr(g, 'vbelzuaian'):
            targets = {(t.x, t.y): int(t.pixels[1,1]) for t in g.vbelzuaian}
            print(f"  Targets: {targets}")
        if hasattr(g, 'mwfajkguqx'):
            for r, sl in g.mwfajkguqx.items():
                print(f"  Rack ({r.x},{r.y},r={r.rotation}): {len(sl)} segs")
