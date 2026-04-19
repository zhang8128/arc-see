#!/usr/bin/env python3
"""SK48 L6 — Side-by-side trace of solver model vs game engine."""

import sys
sys.path.insert(0, 'environment_files/sk48/41055498')

from sk48 import Sk48
from arcengine import GameAction
from arcengine.enums import ActionInput

# ===== SOLVER MODEL (from sk48_l6_fast.py) =====
CELL = 6
H_RX = 5; V_BY = 2
FXM, FXX = 11, 53; FYM, FYX = 8, 50
OBS = frozenset([(29, 26)])
VRYS = (10, 16, 22, 28, 34, 40)
HRXS = (13, 19, 25, 31, 37, 43)

def inf(x, y): return FXM <= x and x + 6 <= FXX and FYM <= y and y + 6 <= FYX

def tat(t, x, y):
    for i, (tx, ty, _) in enumerate(t):
        if tx == x and ty == y: return i
    return -1

def push(t, idx, dx, dy, m):
    if idx in m: return True
    tx, ty, tc = t[idx]
    nx, ny = tx + dx, ty + dy
    if not inf(nx, ny) or (nx, ny) in OBS: return False
    b = tat(t, nx, ny)
    if b >= 0 and not push(t, b, dx, dy, m): return False
    m.add(idx)
    return True

def domv(t, sl, dx, dy, perp):
    m = set()
    for sx, sy in sl:
        for cx, cy in ((sx, sy), (sx+dx, sy+dy)):
            ti = tat(t, cx, cy)
            if ti >= 0 and ti not in m:
                if not push(t, ti, dx, dy, m):
                    if perp: return None
    r = list(t)
    for i in m:
        tx, ty, tc = t[i]
        r[i] = (tx+dx, ty+dy, tc)
    return tuple(r)

def model_step(hry, hns, vrx, vns, t, action):
    hsl = [(H_RX + i*CELL, hry) for i in range(hns)]
    vsl = [(vrx, V_BY + i*CELL) for i in range(vns)]

    if action == 'HR':  # H extend right
        nx = H_RX + CELL * hns
        if (nx, hry) in OBS: return None
        nt = domv(t, hsl, CELL, 0, False)
        return (hry, hns+1, vrx, vns, nt) if nt is not None else None
    elif action == 'HL':  # H shrink left
        if hns <= 1: return None
        nt = domv(t, hsl[1:], -CELL, 0, False)
        return (hry, hns-1, vrx, vns, nt) if nt is not None else None
    elif action == 'HU':  # H move up
        ny = hry - CELL
        nt = domv(t, hsl, 0, -CELL, True)
        return (ny, hns, vrx, vns, nt) if nt is not None else None
    elif action == 'HD':  # H move down
        ny = hry + CELL
        nt = domv(t, hsl, 0, CELL, True)
        return (ny, hns, vrx, vns, nt) if nt is not None else None
    elif action == 'VD':  # V extend down
        ny = V_BY + CELL * vns
        if (vrx, ny) in OBS: return None
        nt = domv(t, vsl, 0, CELL, False)
        return (hry, hns, vrx, vns+1, nt) if nt is not None else None
    elif action == 'VU':  # V shrink up
        if vns <= 1: return None
        nt = domv(t, vsl[1:], 0, -CELL, False)
        return (hry, hns, vrx, vns-1, nt) if nt is not None else None
    elif action == 'VL':  # V move left
        nx = vrx - CELL
        nt = domv(t, vsl, -CELL, 0, True)
        return (hry, hns, nx, vns, nt) if nt is not None else None
    elif action == 'VR':  # V move right
        nx = vrx + CELL
        nt = domv(t, vsl, CELL, 0, True)
        return (hry, hns, nx, vns, nt) if nt is not None else None
    return None

# ===== ENGINE =====
def make_game(level=5):
    g = Sk48()
    g._current_level_index = level
    g.on_set_level(g._levels[level])
    return g

def act(g, action, data=None):
    ai = ActionInput(id=action, data=data or {})
    g.perform_action(ai)
    for _ in range(500):
        if g.is_action_complete: break
        g.step()

def switch_rack(g):
    for rack in g.xpmcmtbcv.keys():
        if rack != g.vzvypfsnt:
            act(g, GameAction.ACTION6, {'x': rack.x + 2, 'y': rack.y + 2})
            return

def get_active_type(g):
    return 'H' if g.vzvypfsnt.rotation == 0 else 'V'

def engine_targets(g):
    """Get play-field targets as solver-format tuple."""
    pts = []
    for t in g.vbelzuaian:
        if t.y < 50:  # play field only
            pts.append((t.x, t.y, int(t.pixels[1,1])))
    return tuple(sorted(pts))

def engine_racks(g):
    """Get rack state."""
    for r, segs in g.mwfajkguqx.items():
        if r.rotation == 0 and r.y < 50:  # H-rack (play field)
            hry = r.y
            hns = len(segs)
        elif r.rotation == 90:  # V-rack
            vrx = r.x
            vns = len(segs)
    return hry, hns, vrx, vns

ACTION_TO_GAME = {
    'HR': ('H', GameAction.ACTION4),
    'HL': ('H', GameAction.ACTION3),
    'HU': ('H', GameAction.ACTION1),
    'HD': ('H', GameAction.ACTION2),
    'VD': ('V', GameAction.ACTION2),
    'VU': ('V', GameAction.ACTION1),
    'VL': ('V', GameAction.ACTION3),
    'VR': ('V', GameAction.ACTION4),
}

# ===== TRACE =====
abstract_sol = "HD HR HR VD VD VR VD HR HL HD HR HL HD HR HR HU HU VU VR VD VU VR VD HR HR HL VD VL VD VD VU HL".split()

# Model initial state
t0 = ((35,26,9), (41,26,9), (47,26,9), (29,32,8), (29,38,8), (29,44,8))
m_hry, m_hns, m_vrx, m_vns, m_t = 26, 2, 29, 2, t0

# Engine
g = make_game()
current_type = get_active_type(g)

print("Step-by-step comparison")
print("=" * 80)

for i, a in enumerate(abstract_sol):
    # Model step
    result = model_step(m_hry, m_hns, m_vrx, m_vns, m_t, a)
    if result is None:
        print(f"Step {i+1}: {a} — MODEL says IMPOSSIBLE!")
        break
    m_hry, m_hns, m_vrx, m_vns, m_t = result

    # Engine step
    needed_type, game_act = ACTION_TO_GAME[a]
    if needed_type != current_type:
        switch_rack(g)
        current_type = get_active_type(g)

    act(g, game_act)

    # Compare
    e_hry, e_hns, e_vrx, e_vns = engine_racks(g)
    e_t = engine_targets(g)
    m_t_sorted = tuple(sorted(m_t))

    rack_match = (m_hry == e_hry and m_hns == e_hns and m_vrx == e_vrx and m_vns == e_vns)
    target_match = (m_t_sorted == e_t)

    if not rack_match or not target_match:
        print(f"\n*** DIVERGENCE at step {i+1}: {a} ***")
        print(f"  Model racks: H=({m_hry},{m_hns}) V=({m_vrx},{m_vns})")
        print(f"  Engine racks: H=({e_hry},{e_hns}) V=({e_vrx},{e_vns})")
        if not target_match:
            print(f"  Model targets:  {m_t_sorted}")
            print(f"  Engine targets: {e_t}")
            # Find specific differences
            m_set = set(m_t_sorted)
            e_set = set(e_t)
            if m_set - e_set:
                print(f"  In model only: {m_set - e_set}")
            if e_set - m_set:
                print(f"  In engine only: {e_set - m_set}")
    else:
        # Brief status
        play_t = {(x,y): c for x,y,c in m_t}
        print(f"Step {i+1}: {a} — H({m_hry},{m_hns}) V({m_vrx},{m_vns}) targets={play_t} ✓")
