#!/usr/bin/env python3
"""SK48 L8 — Determine starting segment counts for H and V racks."""

import copy, numpy as np
import arc_agi
from arcengine import GameAction, GameState

SOLUTIONS = {1:"UUURRRRLDDRLUR",2:"RRRRUUULLURRDDRURLLURRLLURR",
    3:"RRUUUURDDLDRRRRLLLLUUUURDDDLUUUUR",4:"RRUUUULLLLDRURDRURRDLLU",
    5:"LULLRRRRRURRDLLLLDDLDRRRRLURDRLUR"}
L6_SEQ = [('A','ACTION2'),('A','ACTION4'),('A','ACTION4'),('A','ACTION4'),
    ('C',31,4),('A','ACTION2'),('A','ACTION2'),('A','ACTION4'),('A','ACTION2'),
    ('A','ACTION1'),('A','ACTION4'),('A','ACTION2'),('A','ACTION1'),
    ('A','ACTION4'),('A','ACTION2'),('C',7,34),('A','ACTION4'),('A','ACTION4'),
    ('A','ACTION4'),('A','ACTION3'),('A','ACTION3'),('A','ACTION3'),('A','ACTION3'),
    ('A','ACTION2'),('A','ACTION2'),('A','ACTION4'),('A','ACTION1'),('A','ACTION3'),
    ('A','ACTION1'),('A','ACTION4'),('C',49,4),('A','ACTION3'),('A','ACTION3'),
    ('A','ACTION2'),('A','ACTION2'),('A','ACTION2')]
L7_ABS = "VD HR HR VR VD VD HR VD VD VD VU VU VU VU VL VU VL VL VD HL HL HL VD HU HR HR HR HR HR HR HL HL HL HL".split()
GA = {'U':GameAction.ACTION1,'D':GameAction.ACTION2,'L':GameAction.ACTION3,'R':GameAction.ACTION4}
AM = {'ACTION1':GameAction.ACTION1,'ACTION2':GameAction.ACTION2,'ACTION3':GameAction.ACTION3,
      'ACTION4':GameAction.ACTION4,'ACTION6':GameAction.ACTION6}
AH = {'HR':'ACTION4','HL':'ACTION3','HU':'ACTION1','HD':'ACTION2'}
AV = {'VD':'ACTION2','VU':'ACTION1','VL':'ACTION3','VR':'ACTION4'}
CHARS = '0123456789abcdef'

def get_blocks(game):
    lv = game._levels[game._current_level_index]
    bl = []
    for s in lv._sprites:
        if hasattr(s, 'name') and s.name == 'elmjchdqcn' and s.y < 54:
            cs = set()
            for r in s.pixels:
                for px in r:
                    if px != -1 and px != -2: cs.add(int(px))
            bl.append((s.x, s.y, max(cs) if cs else 0))
    return tuple(sorted(bl))

def click_cage(env, game, cage_name):
    lv = game._levels[game._current_level_index]
    for s in lv._sprites:
        if hasattr(s, 'tags') and 'sys_click' in s.tags and s.y < 54:
            cs = {int(px) for r in s.pixels for px in r if px != -1}
            if cage_name == 'cage15' and 15 in cs:
                return env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
            elif cage_name == 'cage6' and 6 in cs:
                return env.step(GameAction.ACTION6, data={'x': s.x+2, 'y': s.y+2})
    return None

def setup_l8():
    arcade = arc_agi.Arcade()
    env = arcade.make("sk48-41055498", render_mode=None)
    g = env._game; obs = env.reset()
    for l in range(1,6):
        for c in SOLUTIONS[l]: obs = env.step(GA[c], data={})
    for i in L6_SEQ:
        if i[0]=='C': obs = env.step(GameAction.ACTION6, data={'x':i[1],'y':i[2]})
        else: obs = env.step(AM[i[1]], data={})
    cur = 'H'
    for a in L7_ABS:
        r = a[0]
        if r != cur: click_cage(env, g, 'cage15' if r=='V' else 'cage6'); cur = r
        obs = env.step(AM[(AH if r=='H' else AV)[a]], data={})
    return env, g, obs

# Print the initial grid for L8 to see segments
env, g, obs = setup_l8()
grid = np.array(obs.frame[-1], dtype=np.int64)

print("Initial L8 grid (rows 0-52, cols 0-53):")
print("    " + "".join(f"{c%10}" for c in range(54)))
for r in range(53):
    row = "".join(CHARS[grid[r,c]] if 0 <= grid[r,c] < 16 else '?' for c in range(54))
    print(f" {r:2d}: {row}")

# Count color-6 cells at y=26 (H-rack row) to see segments
print("\nH-rack row (y=26):")
for c in range(54):
    v = grid[26, c]
    if v > 0:
        print(f"  x={c}: color {v}")

print("\nV-rack column (x=29):")
for r in range(54):
    v = grid[29, r]
    if v > 0:
        print(f"  y={r}: color {v}")

# Test: try HL at start (shrink H). If hns=0, this should be no-op.
# If hns=1, should shrink to 0.
print("\n=== Test: HL at start ===")
env, g, obs = setup_l8()
obs_before = obs
obs = env.step(AM['ACTION3'], data={})  # HL
grid2 = np.array(obs.frame[-1], dtype=np.int64)
diff = np.where(grid != grid2)
if len(diff[0]) == 0:
    print("HL: no change (hns might be 0 or 1 with min=1)")
else:
    print(f"HL: {len(diff[0])} pixels changed")
    for r, c in zip(diff[0][:10], diff[1][:10]):
        print(f"  ({c},{r}): {grid[r,c]} -> {grid2[r,c]}")

# Test: VU at start (shrink V)
print("\n=== Test: VU at start ===")
env, g, obs = setup_l8()
click_cage(env, g, 'cage15')  # switch to V
obs = env.step(AM['ACTION1'], data={})  # VU
grid3 = np.array(obs.frame[-1], dtype=np.int64)
grid_initial = np.array(setup_l8()[2].frame[-1], dtype=np.int64)
# Compare with initial (accounting for cage switch)
print(f"After VU: blocks={get_blocks(g)}")
