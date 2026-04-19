#!/usr/bin/env python3
"""SK48 L8 — Test whether HR extension pushes targets."""

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

def get_segments(game):
    lv = game._levels[game._current_level_index]
    segs = []
    for s in lv._sprites:
        if hasattr(s, 'name') and s.name == 'opqqwmrfcn' and s.y < 54:
            segs.append((s.x, s.y))
    return sorted(segs)

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

arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)
g = env._game; obs = env.reset()

# Replay to L8
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

print(f"Level: {g._current_level_index}")
print(f"Initial blocks: {get_blocks(g)}")
print(f"Initial segments: {get_segments(g)}")

# Test sequence: VD then HR
# VD first
click_cage(env, g, 'cage15')  # switch to V rack
obs = env.step(AM['ACTION2'], data={})  # VD
print(f"\nAfter VD:")
print(f"  blocks: {get_blocks(g)}")
print(f"  segments: {get_segments(g)}")

# Now switch back to H rack and do HR
click_cage(env, g, 'cage6')
obs = env.step(AM['ACTION4'], data={})  # HR
print(f"\nAfter HR:")
print(f"  blocks: {get_blocks(g)}")
print(f"  segments: {get_segments(g)}")

# Do another HR
obs = env.step(AM['ACTION4'], data={})  # HR
print(f"\nAfter HR HR:")
print(f"  blocks: {get_blocks(g)}")
print(f"  segments: {get_segments(g)}")

# Do another HR - this should reach the target at (17,26) if it didn't push before
obs = env.step(AM['ACTION4'], data={})  # HR
print(f"\nAfter HR HR HR:")
print(f"  blocks: {get_blocks(g)}")
print(f"  segments: {get_segments(g)}")

# One more
obs = env.step(AM['ACTION4'], data={})  # HR
print(f"\nAfter HR HR HR HR:")
print(f"  blocks: {get_blocks(g)}")
print(f"  segments: {get_segments(g)}")

# And another
obs = env.step(AM['ACTION4'], data={})  # HR
print(f"\nAfter HR HR HR HR HR:")
print(f"  blocks: {get_blocks(g)}")
print(f"  segments: {get_segments(g)}")
