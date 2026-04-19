#!/usr/bin/env python3
"""SK48 L8 — Determine initial hns/vns by testing edge cases."""

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

# Test A: VU then VD — does VU destroy the initial segment?
print("=== Test A: VU then VD (on V-rack) ===")
env, g = setup_l8()
click_cage(env, g, 'cage15')  # switch to V
print(f"Initial: {get_blocks(g)}")
env.step(AM['ACTION1'], data={})  # VU
print(f"After VU: {get_blocks(g)}")
env.step(AM['ACTION2'], data={})  # VD
print(f"After VU VD: {get_blocks(g)}")
env.step(AM['ACTION2'], data={})  # VD
print(f"After VU VD VD: {get_blocks(g)}")

# Test B: Many VUs then VDs — find the maximum shrink
print("\n=== Test B: Many VUs ===")
env, g = setup_l8()
click_cage(env, g, 'cage15')
for i in range(5):
    env.step(AM['ACTION1'], data={})  # VU
    print(f"After VU x{i+1}: {get_blocks(g)}")

# Test C: VD 7 times (to max), then VU
print("\n=== Test C: VD to max ===")
env, g = setup_l8()
click_cage(env, g, 'cage15')
for i in range(8):
    env.step(AM['ACTION2'], data={})  # VD
    print(f"After VD x{i+1}: {get_blocks(g)}")

# Test D: HR, then HL to find where H-rack really starts
print("\n=== Test D: HR max extend on H ===")
env, g = setup_l8()
for i in range(8):
    env.step(AM['ACTION4'], data={})  # HR
    print(f"After HR x{i+1}: {get_blocks(g)}")

# Test E: Critical — HR from scratch, how many to push block at (17,26)?
# Already know: HR x1 = no push, HR x2 = push.
# Now: does the FIRST HR add a segment at (11,26)?
# Test by doing HR then HU — if there's a segment at (11,26), HU should try to move it
print("\n=== Test E: HR then HU on H ===")
env, g = setup_l8()
env.step(AM['ACTION4'], data={})  # HR
print(f"After HR: {get_blocks(g)}")
env.step(AM['ACTION1'], data={})  # HU (move rack up)
print(f"After HR HU: {get_blocks(g)}")
# Try extending at new position
env.step(AM['ACTION4'], data={})  # HR at new y
print(f"After HR HU HR: {get_blocks(g)}")
