#!/usr/bin/env python3
"""SK48 L8 — Trace abstract vs game engine to find divergence."""

import numpy as np, copy
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
L8_ABS = "VD HR HR HL VD VR VD VL VD VD VD VU VU VU HR HR HR HR HR HL HL VU HL VD HL VU".split()

GA = {'U':GameAction.ACTION1,'D':GameAction.ACTION2,'L':GameAction.ACTION3,'R':GameAction.ACTION4}
AM = {'ACTION1':GameAction.ACTION1,'ACTION2':GameAction.ACTION2,'ACTION3':GameAction.ACTION3,
      'ACTION4':GameAction.ACTION4,'ACTION6':GameAction.ACTION6}
AH = {'HR':'ACTION4','HL':'ACTION3','HU':'ACTION1','HD':'ACTION2'}
AV = {'VD':'ACTION2','VU':'ACTION1','VL':'ACTION3','VR':'ACTION4'}
CELL = 6; H_RX = 11; V_BY = 8; FXM = 11; FXX = 53; FYM = 8; FYX = 50; MAX_S = 8

# ---- Abstract model (from sk48_l8_astar.py) ----
def inf(x, y): return FXM <= x <= FXX - CELL and FYM <= y <= FYX - CELL
def tat(t, x, y):
    for i in range(len(t)):
        if t[i][0] == x and t[i][1] == y: return i
    return -1

def xseg(x, y, hry, hns, vrx, vns, w):
    if w == 'H':
        if x == vrx and (y - V_BY) >= 0 and (y - V_BY) % CELL == 0 and (y - V_BY) // CELL < vns:
            return True
    else:
        if y == hry and (x - H_RX) >= 0 and (x - H_RX) % CELL == 0 and (x - H_RX) // CELL < hns:
            return True
    return False

def push(t, idx, dx, dy, m, hry, hns, vrx, vns, w):
    if idx in m: return True
    tx, ty = t[idx][0], t[idx][1]
    if xseg(tx, ty, hry, hns, vrx, vns, w): return False
    nx, ny = tx + dx, ty + dy
    if not inf(nx, ny): return False
    if xseg(nx, ny, hry, hns, vrx, vns, w): return False
    b = tat(t, nx, ny)
    if b >= 0 and not push(t, b, dx, dy, m, hry, hns, vrx, vns, w): return False
    m.add(idx); return True

def domv(t, sl, dx, dy, perp, hry, hns, vrx, vns, w):
    m = set()
    for sx, sy in sl:
        for cx, cy in ((sx, sy), (sx+dx, sy+dy)):
            ti = tat(t, cx, cy)
            if ti >= 0 and ti not in m:
                if not push(t, ti, dx, dy, m, hry, hns, vrx, vns, w):
                    if perp: return None
    r = list(t)
    for i in m: r[i] = (t[i][0]+dx, t[i][1]+dy, t[i][2])
    return tuple(r)

def abstract_step(hry, hns, vrx, vns, t, action):
    hsl = [(H_RX+i*CELL, hry) for i in range(hns)]
    vsl = [(vrx, V_BY+i*CELL) for i in range(vns)]
    if action == 'HR':
        if hns >= MAX_S: return None
        nx = H_RX+CELL*hns
        if not inf(nx, hry): return None
        nt = domv(t, hsl, CELL, 0, False, hry, hns, vrx, vns, 'H')
        if nt is None: return None
        return (hry, hns+1, vrx, vns, nt)
    elif action == 'HL':
        if hns <= 1: return None
        nt = domv(t, hsl[1:], -CELL, 0, False, hry, hns, vrx, vns, 'H')
        if nt is None: return None
        return (hry, hns-1, vrx, vns, nt)
    elif action == 'HU':
        ny = hry - CELL
        if ny < FYM: return None
        nt = domv(t, hsl, 0, -CELL, True, hry, hns, vrx, vns, 'H')
        if nt is None: return None
        return (ny, hns, vrx, vns, nt)
    elif action == 'HD':
        ny = hry + CELL
        if ny+CELL > FYX: return None
        nt = domv(t, hsl, 0, CELL, True, hry, hns, vrx, vns, 'H')
        if nt is None: return None
        return (ny, hns, vrx, vns, nt)
    elif action == 'VD':
        if vns >= MAX_S: return None
        ny = V_BY+CELL*vns
        if not inf(vrx, ny): return None
        nt = domv(t, vsl, 0, CELL, False, hry, hns, vrx, vns, 'V')
        if nt is None: return None
        return (hry, hns, vrx, vns+1, nt)
    elif action == 'VU':
        if vns <= 1: return None
        nt = domv(t, vsl[1:], 0, -CELL, False, hry, hns, vrx, vns, 'V')
        if nt is None: return None
        return (hry, hns, vrx, vns-1, nt)
    elif action == 'VL':
        nx = vrx - CELL
        if nx < FXM: return None
        nt = domv(t, vsl, -CELL, 0, True, hry, hns, vrx, vns, 'V')
        if nt is None: return None
        return (hry, hns, nx, vns, nt)
    elif action == 'VR':
        nx = vrx + CELL
        if nx+CELL > FXX: return None
        nt = domv(t, vsl, CELL, 0, True, hry, hns, vrx, vns, 'V')
        if nt is None: return None
        return (hry, hns, nx, vns, nt)
    return None

# ---- Game engine ----
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

def get_rack_info(game):
    """Extract hry, hns, vrx, vns from game state."""
    lv = game._levels[game._current_level_index]
    h_segs = []
    v_segs = []
    for s in lv._sprites:
        if hasattr(s, 'name') and s.name == 'opqqwmrfcn' and s.y < 54:
            # Determine rack by checking orientation
            # H-rack segments have same y, V-rack segments have same x
            h_segs.append((s.x, s.y))
            # We'll classify after collecting all
    # Actually let's check by looking at the rack sprite (ejlpqgojjt/udbuodqlxv)
    for s in lv._sprites:
        if hasattr(s, 'name'):
            if s.name == 'ejlpqgojjt' and s.y < 54:
                hry = s.y
            elif s.name == 'udbuodqlxv' and s.y < 54:
                vrx = s.x
    # Count segments by position
    hns = 0; vns = 0
    for s in lv._sprites:
        if hasattr(s, 'name') and s.name == 'opqqwmrfcn' and s.y < 54:
            # Check if on h-rack row or v-rack column
            pass  # This is complex, let's use a simpler approach

    # Count segments from sprite pixels - actually just count visible segments
    # Simpler: look at the ledwmfklzk attribute
    for s in lv._sprites:
        if hasattr(s, 'name') and s.y < 54:
            if s.name == 'ejlpqgojjt':
                # H-rack: count segments
                hns_list = [s2 for s2 in lv._sprites
                           if hasattr(s2, 'name') and s2.name == 'opqqwmrfcn'
                           and s2.y == s.y and s2.y < 54]
                hns = len(hns_list)
            elif s.name == 'udbuodqlxv':
                vns_list = [s2 for s2 in lv._sprites
                           if hasattr(s2, 'name') and s2.name == 'opqqwmrfcn'
                           and s2.x == s.x and s2.y < 54]
                vns = len(vns_list)
    return hry, hns, vrx, vns

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

# ---- Setup ----
arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)
g = env._game
obs = env.reset()

# Replay to L8
for lvl in range(1, 6):
    for c in SOLUTIONS[lvl]: obs = env.step(GA[c], data={})
for item in L6_SEQ:
    if item[0] == 'C': obs = env.step(GameAction.ACTION6, data={'x': item[1], 'y': item[2]})
    else: obs = env.step(AM[item[1]], data={})
cur = 'H'
for a in L7_ABS:
    r = a[0]
    if r != cur:
        click_cage(env, g, 'cage15' if r == 'V' else 'cage6'); cur = r
    obs = env.step(AM[(AH if r == 'H' else AV)[a]], data={})

print(f"At level {g._current_level_index} (L8)")
print(f"Initial blocks (game): {get_blocks(g)}")

# ---- Trace both models ----
t0 = ((29, 14, 9), (29, 38, 14), (17, 26, 8), (41, 26, 12))
abs_state = (26, 1, 29, 1, t0)  # hry, hns, vrx, vns, tiles

game_copy = copy.deepcopy(g)
env._game = game_copy
game_cur_rack = 'H'  # starts on H rack

print(f"\nAbstract init: hry={abs_state[0]} hns={abs_state[1]} vrx={abs_state[2]} vns={abs_state[3]}")
print(f"Abstract tiles: {abs_state[4]}")

for step_i, action in enumerate(L8_ABS):
    # Abstract step
    result = abstract_step(*abs_state, action)
    if result is None:
        print(f"\nStep {step_i}: {action} — ABSTRACT BLOCKED!")
        break
    abs_state = result

    # Game step
    rack = action[0]
    if rack != game_cur_rack:
        click_cage(env, game_copy, 'cage15' if rack == 'V' else 'cage6')
        game_cur_rack = rack
    am = AH if rack == 'H' else AV
    obs = env.step(AM[am[action]], data={})

    game_blocks = get_blocks(game_copy)
    abs_tiles = abs_state[4]
    abs_blocks = tuple(sorted(abs_tiles))

    match = abs_blocks == game_blocks
    marker = "" if match else " *** DIVERGENCE ***"

    print(f"\nStep {step_i}: {action}")
    print(f"  Abstract: hry={abs_state[0]} hns={abs_state[1]} vrx={abs_state[2]} vns={abs_state[3]} tiles={abs_blocks}")
    print(f"  Game:     blocks={game_blocks}{marker}")

    if not match:
        print(f"\n  FIRST DIVERGENCE at step {step_i} ({action})!")
        print(f"  Abstract expected: {abs_blocks}")
        print(f"  Game actual:       {game_blocks}")
        break
