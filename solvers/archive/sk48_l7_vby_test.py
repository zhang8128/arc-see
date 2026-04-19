#!/usr/bin/env python3
"""SK48 L7 — Determine V_BY by testing V-rack slot positions.

Push a block to the V-rack, then eject (VU) and observe where it goes.
The ejection should place the block at the V-rack slot position.
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
      'ACTION3': GameAction.ACTION3, 'ACTION4': GameAction.ACTION4, 'ACTION6': GameAction.ACTION6}

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

# Test: Extend V-rack down step by step and observe which blocks get pushed
# The V-rack scan extends downward. Each VD adds 6 rows.
# The first block that gets pushed tells us V_BY.

print("=== V-rack slot discovery ===")
env, obs = create_env()
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"Initial blocks: {find_blocks(grid)}")

# Switch to cage15
obs = click_cage(env, 'cage15')
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"After switch to cage15: {find_blocks(grid)}")

# VD step by step — note when blocks first move
for i in range(8):
    prev_blocks = find_blocks(grid)
    obs = env.step(AM['ACTION2'], data={})  # VD
    grid = np.array(obs.frame[-1], dtype=np.int64)
    curr_blocks = find_blocks(grid)
    if curr_blocks != prev_blocks:
        print(f"\n  VD #{i+1}: BLOCKS MOVED!")
        print(f"    Before: {prev_blocks}")
        print(f"    After:  {curr_blocks}")
        # Figure out which blocks moved and by how much
        for b_before, b_after in zip(prev_blocks, curr_blocks):
            if b_before != b_after:
                print(f"    Changed: {b_before} -> {b_after}")
    else:
        print(f"  VD #{i+1}: no block movement (vns={i+2})")

# Now test: H-rack slot positions by extending and observing
print("\n\n=== H-rack slot discovery ===")
env, obs = create_env()
grid = np.array(obs.frame[-1], dtype=np.int64)

for i in range(8):
    prev_blocks = find_blocks(grid)
    obs = env.step(AM['ACTION4'], data={})  # HR
    grid = np.array(obs.frame[-1], dtype=np.int64)
    curr_blocks = find_blocks(grid)
    if curr_blocks != prev_blocks:
        print(f"\n  HR #{i+1}: BLOCKS MOVED!")
        print(f"    Before: {prev_blocks}")
        print(f"    After:  {curr_blocks}")
        for b_before, b_after in zip(prev_blocks, curr_blocks):
            if b_before != b_after:
                print(f"    Changed: {b_before} -> {b_after}")
    else:
        print(f"  HR #{i+1}: no block movement (hns={i+2})")

# Also: scan column positions (check V-rack scan in grid after each VD)
print("\n\n=== V-rack scan position tracking ===")
env, obs = create_env()
obs = click_cage(env, 'cage15')
grid = np.array(obs.frame[-1], dtype=np.int64)

# Find initial scan column
CHARS = '0123456789abcdef'
print("Initial scan at col 31-32:")
for r in range(7, 20):
    print(f"  row {r}: col31={grid[r,31]}, col32={grid[r,32]}")

for i in range(4):
    obs = env.step(AM['ACTION2'], data={})  # VD
    grid = np.array(obs.frame[-1], dtype=np.int64)
    # Find bottommost scan row
    bottom = 0
    for r in range(52, 7, -1):
        if grid[r, 31] in [1, 2] or grid[r, 32] in [1, 2]:
            if r < 53:  # exclude border
                bottom = r
                break
    print(f"  VD #{i+1}: scan extends to row {bottom}")
