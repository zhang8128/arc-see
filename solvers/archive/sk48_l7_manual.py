#!/usr/bin/env python3
"""SK48 L7 — Manual step-by-step solution attempt.

Strategy:
1. Move V-rack RIGHT past e-block (with vns=1 so scan doesn't reach e's row)
2. Extend V-rack down to cover e's row
3. Move V-rack LEFT to push e to H-rack slot 1 position (x=17)
4. Shrink V-rack, position 9-blocks using H-rack
5. Position 8-blocks using V-rack

Block positions (sprite coords):
  8@(23,20), 9@(29,20), 9@(23,26), 8@(29,26), e@(35,32)

Target:
  H-rack slot 0: 9@(11, 26)
  H-rack slot 1: 14@(17, 26)
  H-rack slot 2: 9@(23, 26)
  V-rack slot 0: 8@(29, 8)
  V-rack slot 1: 14@(29, 14)
  V-rack slot 2: 8@(29, 20)
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

def do(env, actions_str, current_rack='H'):
    """Execute a sequence of abstract actions. Returns (obs, total_steps, current_rack)."""
    steps = 0
    obs = None
    for a in actions_str.split():
        rack = a[0]
        if rack != current_rack:
            if rack == 'V':
                obs = click_cage(env, 'cage15')
            else:
                obs = click_cage(env, 'cage6')
            steps += 1
            current_rack = rack

        action_map = {
            'HR': 'ACTION4', 'HL': 'ACTION3', 'HU': 'ACTION1', 'HD': 'ACTION2',
            'VD': 'ACTION2', 'VU': 'ACTION1', 'VL': 'ACTION3', 'VR': 'ACTION4',
        }
        obs = env.step(AM[action_map[a]], data={})
        steps += 1
    return obs, steps, current_rack

env, obs = create_env()
g = env._game

grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"Initial blocks: {find_blocks(grid)}")
print(f"  8@(23,20), 9@(29,20), 9@(23,26), 8@(29,26), e@(35,32)")

# === PHASE 1: Move e-block to H-rack slot 1 position (17, 26) ===
# Step A: Move V-rack right past the e (vns=1, scan only at y=8, doesn't touch e at y=32)
#   VR VR → vrx from 29 to 41 (past e at x=35)
#   BUT: VR pushes tiles at (vrx, 8). No tile at (29,8) or (35,8). Clean.
# Step B: Extend V down to cover e's row
#   VD VD VD VD → vns from 1 to 5, covering y=8,14,20,26,32
#   Each VD pushes tiles at the new slot. At vrx=41, no tiles at (41,y). Clean.
# Step C: Move V left to push e
#   VL → vrx 41→35. Push at (41,y). No tiles at x=41. Clean.
#   Wait - the e was at x=35 initially. After VR VR, the e might have been pushed!
#   VR #1: vrx 29→35. Tiles at V-rack segments (29, 8): no tile.
#   But in the game, the scan sweeps from x=29 to x=35.
#   The e at (35,32) is at x=35 = new vrx. Does the scan REACH x=35?
#   With vns=1, scan only at y=8. e is at y=32. NO overlap → e NOT pushed!
#
#   VR #2: vrx 35→41. Scan at y=8 only. e at y=32. NO push.
#   After 2 VR: vrx=41, e still at (35,32).

print("\n=== PHASE 1: Position e-block ===")
# Switch to V-rack and move right (past e)
obs, steps, rack = do(env, "VR VR", 'H')
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"After VR VR ({steps} steps): blocks={find_blocks(grid)}")

# Extend V down to reach e's row (y=32)
obs, steps2, rack = do(env, "VD VD VD VD", rack)
grid = np.array(obs.frame[-1], dtype=np.int64)
print(f"After 4xVD (+{steps2} steps): blocks={find_blocks(grid)}")

# Now move V left to push e. vrx=41, e at (35,32).
# VL: vrx 41→35. Sweep x=40..35. e at x=35 → pushed to x=29.
# VL: vrx 35→29. Sweep x=34..29. e at x=29 → pushed to x=23.
# VL: vrx 29→23. Sweep x=28..23. e at x=23 → pushed to x=17. ← TARGET!
# But other tiles may also be pushed!
# 9@(29,20): at x=29, y=20 (slot 2 of V-rack). Gets pushed during VL #2.
# 8@(29,26): at x=29, y=26 (slot 3). Gets pushed during VL #2.
# Let me just try and see.

for i in range(3):
    obs, s, rack = do(env, "VL", rack)
    grid = np.array(obs.frame[-1], dtype=np.int64)
    print(f"After VL #{i+1} (+{s} steps): blocks={find_blocks(grid)}")

total = steps + steps2 + 3  # approximate
print(f"\nPhase 1 total: ~{total} game actions")
print(f"State: {obs.state}")

# === PHASE 2: Use H-rack to position 9-blocks ===
# Current expected state after phase 1:
# e should be at x=17, 9 and 8 may have been pushed left too
# Let's see what we have and plan accordingly

grid = np.array(obs.frame[-1], dtype=np.int64)
blocks = find_blocks(grid)
print(f"\n=== PHASE 2: Position blocks ===")
print(f"Current blocks: {blocks}")

# Show rack areas
print("\nH-rack area (rows 25-32):")
for r in range(25, 33):
    print(f"  {r}: {''.join(CHARS[grid[r,c]] for c in range(5, 50))}")

# Need: 9@(11,26), 14@(17,26), 9@(23,26) on H-rack
# Check what's currently at these positions

# Strategy depends on current block positions. Let me try H-rack operations.
# Switch to H-rack
obs = click_cage(env, 'cage6')
if obs:
    total += 1
    rack = 'H'
    grid = np.array(obs.frame[-1], dtype=np.int64)
    print(f"\nSwitched to cage6. Blocks: {find_blocks(grid)}")

# Try extending H-rack, then ejecting to position blocks
# HR HR HR HL HL HL → extend to hns=4, push tiles right, then eject 3x to push left
for seq_name, seq in [
    ("HR HR HR", "HR HR HR"),
    ("HL", "HL"),
    ("HL", "HL"),
    ("HL", "HL"),
]:
    obs, s, rack = do(env, seq, rack)
    total += s
    grid = np.array(obs.frame[-1], dtype=np.int64)
    print(f"After {seq_name} (total {total}): blocks={find_blocks(grid)}")

print(f"\nFinal state: {obs.state}, Level: {g._current_level_index}")

# Show final grid
print("\nFinal H-rack (rows 26-31):")
for r in range(26, 32):
    print(f"  {r}: {''.join(CHARS[grid[r,c]] for c in range(5, 45))}")

print("\nTarget area:")
for r in range(56, 62):
    print(f"  {r}: {''.join(CHARS[grid[r,c]] for c in range(5, 60))}")
