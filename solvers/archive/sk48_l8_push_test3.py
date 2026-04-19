#!/usr/bin/env python3
"""SK48 L8 — Isolated push tests: HR vs VD mechanics."""

import copy
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
    return env, g

# Test 1: HR only (no VD first), starting on H-rack
print("=== Test 1: HR only (start on H-rack) ===")
env, g = setup_l8()
print(f"Initial: {get_blocks(g)}")
# H-rack is default active
obs = env.step(AM['ACTION4'], data={})  # HR
print(f"After HR x1: {get_blocks(g)}")
obs = env.step(AM['ACTION4'], data={})  # HR
print(f"After HR x2: {get_blocks(g)}")

# Test 2: VD only (start on V-rack)
print("\n=== Test 2: VD only (switch to V first) ===")
env, g = setup_l8()
print(f"Initial: {get_blocks(g)}")
click_cage(env, g, 'cage15')  # switch to V
obs = env.step(AM['ACTION2'], data={})  # VD
print(f"After VD x1: {get_blocks(g)}")
obs = env.step(AM['ACTION2'], data={})  # VD
print(f"After VD x2: {get_blocks(g)}")

# Test 3: HR directly (no cage switch, start on H by default)
print("\n=== Test 3: HR directly on H (check if H is really active) ===")
env, g = setup_l8()
# Check which cage is active by looking at rack colors
lv = g._levels[g._current_level_index]
for s in lv._sprites:
    if hasattr(s, 'name') and s.name in ('ejlpqgojjt', 'udbuodqlxv') and s.y < 54:
        cs = {int(px) for row in s.pixels for px in row if px != -1 and px != -2}
        print(f"  {s.name} at ({s.x},{s.y}) colors={cs}")
# Do one HR
obs = env.step(AM['ACTION4'], data={})
print(f"After HR: {get_blocks(g)}")

# Test 4: HU (move H rack up), then HR — see if targets matter
print("\n=== Test 4: HU then HR ===")
env, g = setup_l8()
obs = env.step(AM['ACTION1'], data={})  # HU
print(f"After HU: {get_blocks(g)}")
obs = env.step(AM['ACTION4'], data={})  # HR
print(f"After HU HR: {get_blocks(g)}")

# Test 5: Move block 8 somewhere else, then HR into empty space
print("\n=== Test 5: HD to move H-rack away from block 8, then HR ===")
env, g = setup_l8()
obs = env.step(AM['ACTION2'], data={})  # HD (hry 26→32)
print(f"After HD: {get_blocks(g)}")
obs = env.step(AM['ACTION4'], data={})  # HR (extend at y=32, no target)
print(f"After HD HR: {get_blocks(g)}")
obs = env.step(AM['ACTION1'], data={})  # HU (hry 32→26, push targets?)
print(f"After HD HR HU: {get_blocks(g)}")

# Test 6: VR (move V-rack right), does it push?
print("\n=== Test 6: VR (lateral move) ===")
env, g = setup_l8()
click_cage(env, g, 'cage15')  # switch to V
obs = env.step(AM['ACTION2'], data={})  # VD (extend, push 9 from (29,14) to (29,20))
print(f"After VD: {get_blocks(g)}")
obs = env.step(AM['ACTION4'], data={})  # VR (move vrx 29→35)
print(f"After VD VR: {get_blocks(g)}")

# Test 7: HL (shrink H-rack) - does it push?
print("\n=== Test 7: HR HR then HL ===")
env, g = setup_l8()
obs = env.step(AM['ACTION4'], data={})  # HR
print(f"After HR: {get_blocks(g)}")
obs = env.step(AM['ACTION4'], data={})  # HR (should push 8 to 23)
print(f"After HR HR: {get_blocks(g)}")
obs = env.step(AM['ACTION3'], data={})  # HL (shrink)
print(f"After HR HR HL: {get_blocks(g)}")
obs = env.step(AM['ACTION3'], data={})  # HL (shrink back to 1)
print(f"After HR HR HL HL: {get_blocks(g)}")
