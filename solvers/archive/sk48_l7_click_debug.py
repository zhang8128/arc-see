#!/usr/bin/env python3
"""SK48 L7 — Debug click targets for cage switching."""

import numpy as np
import arc_agi
from arcengine import GameAction, GameState

SOLUTIONS = {
    1: "UUURRRRLDDRLUR",
    2: "RRRRUUULLURRDDRURLLURRLLURR",
    3: "RRUUUURDDLDRRRRLLLLUUUURDDDLUUUUR",
    4: "RRUUUULLLLDRURDRURRDLLU",
    5: "LULLRRRRRURRDLLLLDDLDRRRRLURDRLUR",
}

L6_SEQ = [
    ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION4'),
    ('C', 31, 4),
    ('A', 'ACTION2'), ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION2'),
    ('A', 'ACTION1'), ('A', 'ACTION4'), ('A', 'ACTION2'), ('A', 'ACTION1'),
    ('A', 'ACTION4'), ('A', 'ACTION2'),
    ('C', 7, 34),
    ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION4'), ('A', 'ACTION3'),
    ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION2'),
    ('A', 'ACTION2'), ('A', 'ACTION4'), ('A', 'ACTION1'), ('A', 'ACTION3'),
    ('A', 'ACTION1'), ('A', 'ACTION4'),
    ('C', 49, 4),
    ('A', 'ACTION3'), ('A', 'ACTION3'), ('A', 'ACTION2'), ('A', 'ACTION2'),
    ('A', 'ACTION2'),
]

GA = {
    'U': GameAction.ACTION1, 'D': GameAction.ACTION2,
    'L': GameAction.ACTION3, 'R': GameAction.ACTION4,
}
AM = {
    'ACTION1': GameAction.ACTION1, 'ACTION2': GameAction.ACTION2,
    'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4,
    'ACTION6': GameAction.ACTION6,
}

def create_env():
    arcade = arc_agi.Arcade()
    env = arcade.make("sk48-41055498", render_mode=None)
    obs = env.reset()
    for lvl in range(1, 6):
        for c in SOLUTIONS[lvl]:
            obs = env.step(GA[c], data={})
    for item in L6_SEQ:
        if item[0] == 'C':
            obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
        else:
            obs = env.step(AM[item[1]], data={})
    return env, obs

def show_click_sprites(env, label=""):
    g = env._game
    level = g._levels[g._current_level_index]
    if label:
        print(f"  {label}")
    for s in level._sprites:
        if hasattr(s, 'tags') and 'sys_click' in s.tags:
            colors = set()
            if hasattr(s, 'pixels'):
                for row in s.pixels:
                    for px in row:
                        if px != -1:
                            colors.add(int(px))
            print(f"    sys_click at ({s.x},{s.y}) colors={colors}")

def try_click(env, x, y):
    """Try clicking at (x,y) and report result."""
    grid_before = np.array(env.step(GameAction.ACTION6, data={'x': x, 'y': y}).frame[-1], dtype=np.int64)
    # Actually we need to deepcopy first
    return None

# Create fresh env at L7
env, obs = create_env()

print("=== Initial state (cage6 active) ===")
show_click_sprites(env)

# Switch to cage15
obs = env.step(GameAction.ACTION6, data={'x': 31, 'y': 4})
print("\n=== After clicking cage15 at (31,4) ===")
show_click_sprites(env, "After switch to cage15")

# Do 5 V-rack actions: VD VR VD VD VL
for action_name in ['ACTION2', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION3']:
    obs = env.step(AM[action_name], data={})

print("\n=== After VD VR VD VD VL ===")
show_click_sprites(env, "Click targets now")

# Now try various click positions to switch back to cage6
print("\n=== Testing click positions to switch to cage6 ===")
grid_before = np.array(obs.frame[-1], dtype=np.int64)

# Try many positions
import copy
for x, y, desc in [
    (7, 22, "cage6 interior (sprite center)"),
    (7, 28, "cage6 interior (row 28)"),
    (7, 34, "scan column (like L6)"),
    (8, 26, "cage6 frame"),
    (5, 26, "cage6 left border"),
    (6, 27, "cage6 inner"),
    (7, 26, "cage6 top"),
    (8, 28, "cage6 right inner"),
    (10, 28, "cage6 right border"),
    (9, 27, "cage6 right inner 2"),
]:
    env2, obs2 = create_env()
    # Switch to cage15
    obs2 = env2.step(GameAction.ACTION6, data={'x': 31, 'y': 4})
    # Do V actions
    for an in ['ACTION2', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION3']:
        obs2 = env2.step(AM[an], data={})
    # Save grid
    g1 = np.array(obs2.frame[-1], dtype=np.int64)
    # Try click
    obs2 = env2.step(GameAction.ACTION6, data={'x': x, 'y': y})
    g2 = np.array(obs2.frame[-1], dtype=np.int64)
    diff = np.sum(g1 != g2)
    print(f"  ({x:2d},{y:2d}) {desc}: {diff} cells changed")
