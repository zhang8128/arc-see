#!/usr/bin/env python3
"""SK48 L7 — Trace abstract solution through actual game, comparing states."""

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
    """Find all colored blocks (8, 9, 14) in the grid."""
    blocks = []
    for color in [8, 9, 14]:
        visited = set()
        for r in range(row_range[0], row_range[1]):
            for c in range(64):
                if grid[r, c] == color and (r, c) not in visited:
                    # BFS to find block extent
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
                        blocks.append((min_c - 1, min_r - 1, color))  # sprite coords
        visited.clear()
    return sorted(blocks)

# Abstract solution v2 (with rack position constraint):
abstract_path = "HR HR HU VL VD VR VR VD HR HR HR HL VD VD VD HL HL HD HR HL VL VU VU VU".split()

# Map to game actions with cage switches
game_sequence = []
current = 'H'
for a in abstract_path:
    rack = a[0]
    if rack != current:
        if rack == 'V':
            game_sequence.append(('CLICK_V', None))
        else:
            game_sequence.append(('CLICK_H', None))
        current = rack
    action_map = {
        'HR': 'ACTION4', 'HL': 'ACTION3', 'HU': 'ACTION1', 'HD': 'ACTION2',
        'VD': 'ACTION2', 'VU': 'ACTION1', 'VL': 'ACTION3', 'VR': 'ACTION4',
    }
    game_sequence.append((action_map[a], a))

# Execute and trace
env, obs = create_env()
g = env._game
grid = np.array(obs.frame[-1], dtype=np.int64)

print("=== STEP-BY-STEP TRACE ===")
print(f"Initial blocks: {find_blocks(grid)}")
step = 0

for game_action, abstract_name in game_sequence:
    if game_action == 'CLICK_V':
        # Find cage15 sys_click sprite
        level = g._levels[g._current_level_index]
        for s in level._sprites:
            if hasattr(s, 'tags') and 'sys_click' in s.tags and s.y < 54:
                colors = set()
                for row in s.pixels:
                    for px in row:
                        if px != -1:
                            colors.add(int(px))
                if 15 in colors:
                    cx, cy = s.x + 2, s.y + 2
                    obs = env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
                    step += 1
                    grid = np.array(obs.frame[-1], dtype=np.int64)
                    print(f"\n  Step {step}: CLICK cage15 at ({cx},{cy})")
                    print(f"    Blocks: {find_blocks(grid)}")
                    break
    elif game_action == 'CLICK_H':
        level = g._levels[g._current_level_index]
        for s in level._sprites:
            if hasattr(s, 'tags') and 'sys_click' in s.tags and s.y < 54:
                colors = set()
                for row in s.pixels:
                    for px in row:
                        if px != -1:
                            colors.add(int(px))
                if 6 in colors:
                    cx, cy = s.x + 2, s.y + 2
                    obs = env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
                    step += 1
                    grid = np.array(obs.frame[-1], dtype=np.int64)
                    print(f"\n  Step {step}: CLICK cage6 at ({cx},{cy})")
                    print(f"    Blocks: {find_blocks(grid)}")
                    break
    else:
        obs = env.step(AM[game_action], data={})
        step += 1
        grid = np.array(obs.frame[-1], dtype=np.int64)
        blocks = find_blocks(grid)
        win = obs.state == GameState.WIN or g._current_level_index > 6
        print(f"\n  Step {step}: {game_action} ({abstract_name})")
        print(f"    Blocks: {blocks}")
        if win:
            print(f"    *** WIN! ***")
            break

print(f"\nTotal steps: {step}")
print(f"State: {obs.state}, Level: {g._current_level_index}")

# Also show the model's expected state at each step
print("\n\n=== MODEL EXPECTED STATES ===")
# Run through the abstract model
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solvers')

# Inline the model's succs logic to trace
CELL = 6
H_RX = 11
V_BY = 8

def model_trace():
    t = ((23, 20, 8), (29, 20, 9), (23, 26, 9), (29, 26, 8), (35, 32, 14))
    hry, hns, vrx, vns = 26, 1, 29, 1

    for a in abstract_path:
        hsl = [(H_RX + i * CELL, hry) for i in range(hns)]
        vsl = [(vrx, V_BY + i * CELL) for i in range(vns)]

        print(f"  {a}: hry={hry} hns={hns} vrx={vrx} vns={vns}")
        print(f"    tiles before: {t}")

        # Apply action (simplified - just update params)
        if a == 'HR': hns += 1
        elif a == 'HL': hns -= 1
        elif a == 'HU': hry -= CELL
        elif a == 'HD': hry += CELL
        elif a == 'VD': vns += 1
        elif a == 'VU': vns -= 1
        elif a == 'VL': vrx -= CELL
        elif a == 'VR': vrx += CELL

model_trace()
