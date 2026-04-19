#!/usr/bin/env python3
"""SK48 L7 — Test sequential rack submission hypothesis.

Theory: Fill H-rack with 9,14,9 → submit (eject) → blocks freed →
Fill V-rack with 8,14,8 → submit → WIN.

We need to get the e-block at (35,32) onto the H-rack at slot 1 position.
"""

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

GA = {'U': GameAction.ACTION1, 'D': GameAction.ACTION2, 'L': GameAction.ACTION3, 'R': GameAction.ACTION4}
AM = {'ACTION1': GameAction.ACTION1, 'ACTION2': GameAction.ACTION2,
      'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4,
      'ACTION6': GameAction.ACTION6, 'ACTION7': GameAction.ACTION7}

CHARS = '0123456789abcdef'

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

def find_blocks(grid, row_range=(0, 53)):
    blocks = []
    for color in [8, 9, 14]:
        visited = set()
        for r in range(row_range[0], row_range[1]):
            for c in range(64):
                if grid[r, c] == color and (r, c) not in visited:
                    queue = [(r, c)]
                    cells = []
                    while queue:
                        cr, cc = queue.pop(0)
                        if (cr, cc) in visited or grid[cr, cc] != color:
                            continue
                        visited.add((cr, cc))
                        cells.append((cr, cc))
                        for dr, dc in [(0,1),(0,-1),(1,0),(-1,0)]:
                            nr, nc = cr+dr, cc+dc
                            if 0 <= nr < 64 and 0 <= nc < 64:
                                queue.append((nr, nc))
                    if cells:
                        min_r = min(r for r, c in cells)
                        min_c = min(c for r, c in cells)
                        blocks.append((min_c - 1, min_r - 1, color))
    return sorted(blocks)

def click_cage(env, cage_name):
    level = env._game._levels[env._game._current_level_index]
    for s in level._sprites:
        if hasattr(s, 'tags') and 'sys_click' in s.tags and s.y < 54:
            colors = {int(px) for row in s.pixels for px in row if px != -1}
            if cage_name == 'cage15' and 15 in colors:
                return env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
            elif cage_name == 'cage6' and 6 in colors:
                return env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
    return None

# First: try to get 9,14,9 onto the H-rack.
# We need:
# - 9 at slot 0 (x=11, y=26 in sprite coords)
# - 14 at slot 1 (x=17, y=26)
# - 9 at slot 2 (x=23, y=26) ← already there initially!

# The e-block is at (35,32). To get it to (17,26):
# Need to move it LEFT from x=35 to x=17 (-18 = -3*CELL)
# And UP from y=32 to y=26 (-6 = -1*CELL)

# Use V-rack to push e LEFT: extend V down to y=32, then move V left
# V-rack at vrx=29. Extend to cover y=32: need vns = (32-8)/6 +1 = 5 slots

# Strategy attempt:
# Phase 1: Use V-rack to push e-block left and up
# Phase 2: Use H-rack to position 9-blocks

env, obs = create_env()
g = env._game
total = 0

print("=== Phase 1: Position e-block using V-rack ===")
# Switch to cage15
obs = click_cage(env, 'cage15'); total += 1
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"Step {total}: Switch to cage15. Blocks: {find_blocks(grid)}")

# Extend V-rack down to reach e-block row (y=32 in sprite, row 33 in grid)
# V_BY=8, need to reach y=32 → slot = (32-8)/6 = 4. Need vns=5.
for i in range(4):
    obs = env.step(AM['ACTION2'], data={}); total += 1  # VD
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"Step {total}: After 4x VD. Blocks: {find_blocks(grid)}")

# Move V-rack right to be at vrx=35 (to align with e at x=35)
obs = env.step(AM['ACTION4'], data={}); total += 1  # VR
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"Step {total}: After VR (vrx→35). Blocks: {find_blocks(grid)}")

# Now move V-rack left to push e-block left
# Currently vrx=35. e at (35,32). Moving left pushes e to x=29.
for i in range(3):
    obs = env.step(AM['ACTION3'], data={}); total += 1  # VL
    grid = np.array(obs.frame[-1], dtype=np.int64)
    print(f"Step {total}: After VL #{i+1}. Blocks: {find_blocks(grid)}")

# Now e should be at x=17 (pushed from 35 by 3 VLs = 18 left).
# But 9 at (29,20) and 8 at (29,26) might block!

# Check current state
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"\nState after phase 1: {obs.state}")
print(f"Blocks: {find_blocks(grid)}")

# Now eject V (VU) to shorten rack — this pushes tiles UP
for i in range(3):
    obs = env.step(AM['ACTION1'], data={}); total += 1  # VU
    grid = np.array(obs.frame[-1], dtype=np.int64)
    print(f"Step {total}: After VU #{i+1}. Blocks: {find_blocks(grid)}")

print(f"\nAfter all V operations: {find_blocks(grid)}")

# Switch to cage6
obs = click_cage(env, 'cage6'); total += 1
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"Step {total}: Switch to cage6. Blocks: {find_blocks(grid)}")

# Show rack area
print("\nH-rack area (rows 26-31):")
for r in range(26, 32):
    print(f"  {r}: {''.join(CHARS[grid[r,c]] for c in range(5, 40))}")

print(f"\nTotal actions: {total}")
print(f"State: {obs.state}, Level: {g._current_level_index}")
