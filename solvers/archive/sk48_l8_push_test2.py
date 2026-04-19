#!/usr/bin/env python3
"""SK48 L8 — Detailed push mechanics investigation."""

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

def dump_sprites(game, label=""):
    lv = game._levels[game._current_level_index]
    blocks = []
    segments = []
    racks = []
    cages = []
    for s in lv._sprites:
        if not hasattr(s, 'name'): continue
        if s.y >= 54: continue  # Skip reference area
        cs = set()
        for r in s.pixels:
            for px in r:
                if px != -1 and px != -2: cs.add(int(px))
        name = s.name
        if name == 'elmjchdqcn':
            blocks.append((s.x, s.y, max(cs) if cs else 0))
        elif name == 'opqqwmrfcn':
            segments.append((s.x, s.y, cs))
        elif name in ('ejlpqgojjt', 'udbuodqlxv'):
            racks.append((name, s.x, s.y, cs))
        elif hasattr(s, 'tags') and 'sys_click' in s.tags:
            cages.append((s.x, s.y, cs))
    if label:
        print(f"\n=== {label} ===")
    print(f"  Blocks: {sorted(blocks)}")
    print(f"  Racks: {racks}")
    # Only show segments if any
    if segments:
        print(f"  Segments ({len(segments)}): {sorted(segments)[:10]}...")
    else:
        # Check ALL sprites for opqqwmrfcn including y>=54
        all_segs = []
        for s in lv._sprites:
            if hasattr(s, 'name') and s.name == 'opqqwmrfcn':
                all_segs.append((s.x, s.y))
        print(f"  Segments: none visible (all_segs={len(all_segs)} total)")

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

dump_sprites(g, "L8 initial")

# Now let's understand the segment sprites better
lv = g._levels[g._current_level_index]
print("\n--- ALL sprite names in L8 ---")
names = {}
for s in lv._sprites:
    if not hasattr(s, 'name'): continue
    n = s.name
    if n not in names: names[n] = []
    names[n].append((s.x, s.y))
for n in sorted(names):
    positions = sorted(names[n])
    if len(positions) <= 6:
        print(f"  {n}: {positions}")
    else:
        print(f"  {n}: ({len(positions)} sprites) {positions[:3]}...{positions[-3:]}")

# Check the internal state of the rack
print("\n--- Rack internal state ---")
for s in lv._sprites:
    if hasattr(s, 'name') and s.name in ('ejlpqgojjt', 'udbuodqlxv') and s.y < 54:
        print(f"  {s.name} at ({s.x},{s.y})")
        # Check for any useful attributes
        for attr in dir(s):
            if attr.startswith('_'): continue
            if attr in ('pixels', 'tags', 'name'): continue
            try:
                v = getattr(s, attr)
                if callable(v): continue
                if isinstance(v, (int, float, str, bool, list, tuple)):
                    print(f"    .{attr} = {v}")
            except: pass

# Step-by-step test with rack state
print("\n\n=== STEP-BY-STEP HR TEST ===")
print("Starting on H-rack. Current cage: H")
dump_sprites(g, "Before any HR")

# First do VD to push 9 down (matches abstract step 0)
click_cage(env, g, 'cage15')
obs = env.step(AM['ACTION2'], data={})
dump_sprites(g, "After VD")

# Switch to H and extend
click_cage(env, g, 'cage6')

for i in range(6):
    obs = env.step(AM['ACTION4'], data={})
    dump_sprites(g, f"After HR x{i+1}")

    # Also check all opqqwmrfcn sprites
    lv = g._levels[g._current_level_index]
    visible_segs = [(s.x, s.y) for s in lv._sprites
                   if hasattr(s, 'name') and s.name == 'opqqwmrfcn' and s.y < 54]
    all_segs = [(s.x, s.y) for s in lv._sprites
               if hasattr(s, 'name') and s.name == 'opqqwmrfcn']
    print(f"  visible segs: {sorted(visible_segs)}, all segs: {len(all_segs)}")
