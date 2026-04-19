#!/usr/bin/env python3
"""Debug: compare initial states of env vs direct engine."""

import arc_agi
from arcengine import GameAction, GameState
from arcengine.enums import ActionInput
import numpy as np
import sys

sys.path.insert(0, 'environment_files/sk48/41055498')
from sk48 import Sk48

# Direct
g = Sk48()
d_targets = {}
for t in g.vbelzuaian:
    d_targets[(t.x, t.y)] = int(t.pixels[1,1])
d_segs = {}
for r, sl in g.mwfajkguqx.items():
    d_segs[(r.x, r.y, r.rotation)] = len(sl)
d_active = (g.vzvypfsnt.x, g.vzvypfsnt.y, g.vzvypfsnt.rotation) if g.vzvypfsnt else None

print("=== Direct Sk48() ===")
print(f"Active: {d_active}")
print(f"Segs: {d_segs}")
print(f"Targets: {d_targets}")
print(f"Level: {g._current_level_index}")
print(f"Remaining: {g.qiercdohl}")

# Env
arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)
obs = env.reset()

e_game = env.env._game if hasattr(env, 'env') and hasattr(env.env, '_game') else None
if e_game is None:
    # Try other access paths
    for attr in ['_game', 'game', '_env']:
        if hasattr(env, attr):
            e_game = getattr(env, attr)
            break
    if e_game is None and hasattr(env, 'env'):
        for attr in ['_game', 'game']:
            if hasattr(env.env, attr):
                e_game = getattr(env.env, attr)
                break

if e_game:
    e_targets = {}
    for t in e_game.vbelzuaian:
        e_targets[(t.x, t.y)] = int(t.pixels[1,1])
    e_segs = {}
    for r, sl in e_game.mwfajkguqx.items():
        e_segs[(r.x, r.y, r.rotation)] = len(sl)
    e_active = (e_game.vzvypfsnt.x, e_game.vzvypfsnt.y, e_game.vzvypfsnt.rotation) if e_game.vzvypfsnt else None

    print(f"\n=== Env game ===")
    print(f"Active: {e_active}")
    print(f"Segs: {e_segs}")
    print(f"Targets: {e_targets}")
    print(f"Level: {e_game._current_level_index}")
    print(f"Remaining: {e_game.qiercdohl}")

    if d_targets == e_targets and d_segs == e_segs:
        print("\n=== States MATCH ===")
    else:
        print("\n=== States DIFFER ===")
        if d_targets != e_targets:
            print(f"  Direct targets: {d_targets}")
            print(f"  Env targets:    {e_targets}")
        if d_segs != e_segs:
            print(f"  Direct segs: {d_segs}")
            print(f"  Env segs:    {e_segs}")
else:
    print("\nCan't access env game object")
    # Compare frames instead
    env_frame = np.array(obs.frame[-1], dtype=np.int64) if obs.frame else None
    d_frame = g.render()[-1] if hasattr(g, 'render') else None
    if env_frame is not None and d_frame is not None:
        d_frame = np.array(d_frame, dtype=np.int64)
        diff = np.sum(env_frame != d_frame)
        print(f"Frame diff: {diff} cells")
    print(f"Env dir: {[a for a in dir(env) if not a.startswith('_')]}")
    if hasattr(env, 'env'):
        print(f"Env.env dir: {[a for a in dir(env.env) if not a.startswith('_')]}")
