#!/usr/bin/env python3
"""SK48 L7 — Test H-rack solution and observe game response."""

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

# Full solution: H=9,14,9 + V=8,14,8 with shared e at (17,20). V_BY=8.
abstract_path = "VD HR HR VR VD VD HR VD VD VD VU VU VU VU VL VU VL VL VD HL HL HL VD HU HR HR HR HR HR HR HL HL HL HL".split()

env, obs = create_env()
g = env._game

action_map_h = {'HR': 'ACTION4', 'HL': 'ACTION3', 'HU': 'ACTION1', 'HD': 'ACTION2'}
action_map_v = {'VD': 'ACTION2', 'VU': 'ACTION1', 'VL': 'ACTION3', 'VR': 'ACTION4'}

current = 'H'
total = 0
for i, a in enumerate(abstract_path):
    rack = a[0]
    if rack != current:
        if rack == 'V':
            obs = click_cage(env, 'cage15')
        else:
            obs = click_cage(env, 'cage6')
        total += 1
        current = rack

    am = action_map_h if rack == 'H' else action_map_v
    obs = env.step(AM[am[a]], data={})
    total += 1

    grid = np.array(obs.frame[-1], dtype=np.int64)
    blocks = find_blocks(grid)
    state = obs.state
    level_idx = g._current_level_index

    print(f"Step {total} ({a}): blocks={blocks} state={state}")
    if state == GameState.WIN or level_idx > 6:
        print(f"\n*** WIN! Level advanced to {level_idx} ***")
        break

# Final state
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"\nFinal: {total} game actions, state={obs.state}, level={g._current_level_index}")

print("\nH-rack area (rows 26-31):")
for r in range(26, 32):
    print(f"  {r}: {''.join(CHARS[grid[r,c]] for c in range(5, 45))}")

print("\nTarget area:")
for r in range(56, 62):
    print(f"  {r}: {''.join(CHARS[grid[r,c]] for c in range(5, 60))}")

# Now try additional actions to see if something triggers
print("\n=== Testing post-H-rack actions ===")

# Try HL (eject from H-rack)
prev_grid = grid.copy()
obs = env.step(AM['ACTION3'], data={})
total += 1
grid = np.array(obs.frame[-1], dtype=np.int64)
diff = np.sum(prev_grid != grid)
print(f"HL (eject): {diff} cells changed, state={obs.state}")
blocks = find_blocks(grid)
print(f"  Blocks after: {blocks}")

# Try ACTION7
prev_grid = grid.copy()
obs = env.step(GameAction.ACTION7, data={})
total += 1
grid = np.array(obs.frame[-1], dtype=np.int64)
diff = np.sum(prev_grid != grid)
print(f"ACTION7: {diff} cells changed, state={obs.state}")

# Try clicking cage15
prev_grid = grid.copy()
obs = click_cage(env, 'cage15')
total += 1
grid = np.array(obs.frame[-1], dtype=np.int64)
diff = np.sum(prev_grid != grid)
print(f"Click cage15: {diff} cells changed, state={obs.state}")
blocks = find_blocks(grid)
print(f"  Blocks after: {blocks}")

print(f"\nTotal actions used: {total}")
