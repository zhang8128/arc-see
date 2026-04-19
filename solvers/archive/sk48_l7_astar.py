#!/usr/bin/env python3
"""SK48 L7 — Pure-Python A* solver adapted from L6.

Sprite analysis:
  Block sprites ('elmjchdqcn'):
    (23,20,8), (29,20,9), (23,26,9), (29,26,8), (35,32,14)
  These are at (x,y) positions. Grid shows blocks at:
    8@(24,21), 9@(30,21), 9@(24,27), 8@(30,27), e@(36,33)
  So sprite pos = grid_pos - (1,1)? Actually sprite x=23 → grid col 24.
  Each block is ~6x6 sprite but 4x4 visible.

Key geometry (sprite coordinates):
  CELL = 6
  H-rack: extends rightward. Segments at x = H_RX + i*CELL
  V-rack: extends downward. Segments at y = V_BY + i*CELL

  H_RX = 11 (first H-rack segment x — scan sprites at x=11 in target area)
  V_BY = 8 (first V-rack segment y — scan starts at y=8)

  H-rack moves: y = 20, 26, 32, 38, 44 (initial y=20 for cage interior)
  V-rack moves: x = 13, 19, 25, 31, 37, 43 (initial x=29 for cage interior)

  Field bounds: x=11..52, y=8..49

Tiles (sprite coords): (23,20,8), (29,20,9), (23,26,9), (29,26,8), (35,32,14)

Target:
  H-rack: 9@x=11, 14@x=17, 9@x=23 at y=hry
  V-rack: 8@y=V_BY, 14@y=V_BY+6, 8@y=V_BY+12 at x=vrx

Actually, from the target area sprites:
  Left rack target sprites: 9@(11,56), 14@(17,56), 9@(23,56)
  Right rack target sprites: 8@(41,56), 14@(47,56), 8@(53,56)

So target H-rack slots at x=11, 17, 23 (spacing 6=CELL) with colors 9,14,9
And target V-rack slots at x=41, 47, 53 — but these are HORIZONTAL display.
For V-rack: slots at y = V_BY + i*6 with colors 8,14,8.

WIN: H-rack has 9,14,9 at first 3 slots. V-rack has 8,14,8 at first 3 slots.
"""

import heapq
import time

CELL = 6

# H-rack parameters
H_RX = 11  # First H-rack slot x position (from target sprite at x=11)

# V-rack parameters
V_BY = 8   # First V-rack slot y position

# Field bounds (sprite coordinates)
FXM = 11
FXX = 53
FYM = 8
FYX = 50

# Max segments per rack
MAX_S = 8

# No obstacle in L7 (was OBS_X=29, OBS_Y=26 in L6)
OBS_X = None
OBS_Y = None

# Valid rack positions (where racks can move to, based on scan markers)
# H-rack Y positions: cage6 interior y, moving in CELL increments
# From sprite data: scan column markers at y=10,16,22,28,34,40
# H-rack valid ys = starting from initial y=20 stepping by CELL
HRYS = tuple(range(8, 50, CELL))   # 8,14,20,26,32,38,44

# V-rack X positions: cage15 interior x, moving in CELL increments
# From sprite data: scan row markers at x=13,19,25,31,37,43
VRXS = tuple(range(13, 50, CELL))  # 13,19,25,31,37,43

# Cross-rack segment positions for blocking
# H-rack segment x positions
def hrx_positions():
    return tuple(H_RX + i * CELL for i in range(MAX_S))

# V-rack segment y positions
def vby_positions():
    return tuple(V_BY + i * CELL for i in range(MAX_S))

HRXP = hrx_positions()  # 11,17,23,29,35,41,47,53
VBYP = vby_positions()  # 8,14,20,26,32,38,44,50


def inf(x, y):
    """Check if position is in field."""
    return FXM <= x <= FXX - 6 and FYM <= y <= FYX - 6


def tat(t, x, y):
    """Find tile at position (x,y)."""
    for i in range(len(t)):
        if t[i][0] == x and t[i][1] == y:
            return i
    return -1


def xseg(x, y, hry, hns, vrx, vns, w):
    """Check if (x,y) is on the OPPOSING rack's segment.
    w='H' means we're doing an H-rack operation, so check V-rack segments.
    w='V' means we're doing a V-rack operation, so check H-rack segments."""
    if w == 'H':
        # Check V-rack segments
        if x == vrx and (y - V_BY) >= 0 and (y - V_BY) % CELL == 0 and (y - V_BY) // CELL < vns:
            return True
    else:
        # Check H-rack segments
        if y == hry and (x - H_RX) >= 0 and (x - H_RX) % CELL == 0 and (x - H_RX) // CELL < hns:
            return True
    return False


def push(t, idx, dx, dy, m, hry, hns, vrx, vns, w):
    """Try to push tile at index idx in direction (dx,dy)."""
    if idx in m:
        return True
    tx, ty = t[idx][0], t[idx][1]
    # Can't push if on cross-rack segment
    if xseg(tx, ty, hry, hns, vrx, vns, w):
        return False
    nx, ny = tx + dx, ty + dy
    if not inf(nx, ny):
        return False
    if OBS_X is not None and nx == OBS_X and ny == OBS_Y:
        return False
    if xseg(nx, ny, hry, hns, vrx, vns, w):
        return False
    # Check if destination is occupied
    b = tat(t, nx, ny)
    if b >= 0 and not push(t, b, dx, dy, m, hry, hns, vrx, vns, w):
        return False
    m.add(idx)
    return True


def domv(t, sl, dx, dy, perp, hry, hns, vrx, vns, w):
    """Do move: push tiles from segment positions in direction (dx,dy)."""
    m = set()
    for sx, sy in sl:
        for cx, cy in ((sx, sy), (sx + dx, sy + dy)):
            ti = tat(t, cx, cy)
            if ti >= 0 and ti not in m:
                if not push(t, ti, dx, dy, m, hry, hns, vrx, vns, w):
                    if perp:
                        return None
    r = list(t)
    for i in m:
        r[i] = (t[i][0] + dx, t[i][1] + dy, t[i][2])
    return tuple(r)


def chkw(hry, hns, vrx, vns, t):
    """Check win condition.
    Try multiple interpretations:
    1. Full: H=9,14,9 V=8,14,8
    2. Partial: H has 9 at slots 0,2 AND V has 8 at slots 0,2 (e optional)
    3. H-only: just H-rack complete
    """
    # H-rack check: 9 at slot 0 and slot 2
    h0 = tat(t, H_RX, hry)
    h2 = tat(t, H_RX + 2 * CELL, hry)
    h_ok = (h0 >= 0 and t[h0][2] == 9 and h2 >= 0 and t[h2][2] == 9 and hns >= 3)

    # V-rack check: 8 at slot 0 and slot 2
    v0 = tat(t, vrx, V_BY)
    v2 = tat(t, vrx, V_BY + 2 * CELL)
    v_ok = (v0 >= 0 and t[v0][2] == 8 and v2 >= 0 and t[v2][2] == 8 and vns >= 3)

    # Try multiple win conditions to find the right one

    # Condition 1: Full win with e at both racks, original positions
    h1 = tat(t, H_RX + CELL, hry)
    v1 = tat(t, vrx, V_BY + CELL)
    h_full = h_ok and h1 >= 0 and t[h1][2] == 14
    v_full = v_ok and v1 >= 0 and t[v1][2] == 14
    if h_full and v_full and hry == 26 and vrx == 29:
        return True

    # Condition 2: H-rack has 9,14,9 (original pos) + V-rack has 8,_,8 (original pos)
    if h_full and v_ok and hry == 26 and vrx == 29:
        return True

    # Condition 3: Both racks at original pos, 9s and 8s only (no e)
    if h_ok and v_ok and hry == 26 and vrx == 29:
        return True

    # Condition 4: H has 9,14,9 anywhere + V has 8,14,8 anywhere
    if h_full and v_full:
        return True

    # Condition 5: Just 9s and 8s at correct positions, any rack position
    if h_ok and v_ok:
        return True

    return False


def heur(hry, hns, vrx, vns, t):
    """Heuristic: count moves needed to place 9s on H-rack and 8s on V-rack."""
    h = 0

    # H-rack: need 9 at slot 0 (x=H_RX) and slot 2 (x=H_RX+2*CELL) at y=hry
    for slot_x in [H_RX, H_RX + 2 * CELL]:
        ti = tat(t, slot_x, hry)
        if ti < 0 or t[ti][2] != 9:
            # Find nearest 9 tile
            min_dist = 999
            for tx, ty, tc in t:
                if tc == 9:
                    dist = abs(tx - slot_x) // CELL + abs(ty - hry) // CELL
                    min_dist = min(min_dist, dist)
            h += min_dist

    # V-rack: need 8 at slot 0 (y=V_BY) and slot 2 (y=V_BY+2*CELL) at x=vrx
    for slot_y in [V_BY, V_BY + 2 * CELL]:
        ti = tat(t, vrx, slot_y)
        if ti < 0 or t[ti][2] != 8:
            min_dist = 999
            for tx, ty, tc in t:
                if tc == 8:
                    dist = abs(tx - vrx) // CELL + abs(ty - slot_y) // CELL
                    min_dist = min(min_dist, dist)
            h += min_dist

    # Rack size penalty
    h += max(0, 3 - hns) + max(0, 3 - vns)

    # Rack position penalty: must return to original positions
    h += abs(hry - 26) // CELL + abs(vrx - 29) // CELL

    return h


def mkey(hry, hns, vrx, vns, t):
    """State key for visited set."""
    pos = frozenset((tx, ty, tc) for tx, ty, tc in t)
    return (hry, hns, vrx, vns, pos)


def succs(hry, hns, vrx, vns, t):
    """Generate successor states."""
    hsl = [(H_RX + i * CELL, hry) for i in range(hns)]
    vsl = [(vrx, V_BY + i * CELL) for i in range(vns)]
    out = []

    # HR: extend H-rack right
    if hns < MAX_S:
        nx = H_RX + CELL * hns
        if inf(nx, hry):
            nt = domv(t, hsl, CELL, 0, False, hry, hns, vrx, vns, 'H')
            if nt is not None:
                out.append((hry, hns + 1, vrx, vns, nt, 'HR'))

    # HL: shrink H-rack left
    if hns > 1:
        nt = domv(t, hsl[1:], -CELL, 0, False, hry, hns, vrx, vns, 'H')
        if nt is not None:
            out.append((hry, hns - 1, vrx, vns, nt, 'HL'))

    # HU: move H-rack up
    ny = hry - CELL
    if ny >= FYM:
        nt = domv(t, hsl, 0, -CELL, True, hry, hns, vrx, vns, 'H')
        if nt is not None:
            out.append((ny, hns, vrx, vns, nt, 'HU'))

    # HD: move H-rack down
    ny = hry + CELL
    if ny + 6 <= FYX:
        nt = domv(t, hsl, 0, CELL, True, hry, hns, vrx, vns, 'H')
        if nt is not None:
            out.append((ny, hns, vrx, vns, nt, 'HD'))

    # VD: extend V-rack down
    if vns < MAX_S:
        ny = V_BY + CELL * vns
        if inf(vrx, ny):
            nt = domv(t, vsl, 0, CELL, False, hry, hns, vrx, vns, 'V')
            if nt is not None:
                out.append((hry, hns, vrx, vns + 1, nt, 'VD'))

    # VU: shrink V-rack up
    if vns > 1:
        nt = domv(t, vsl[1:], 0, -CELL, False, hry, hns, vrx, vns, 'V')
        if nt is not None:
            out.append((hry, hns, vrx, vns - 1, nt, 'VU'))

    # VL: move V-rack left
    nx = vrx - CELL
    if nx >= FXM:
        nt = domv(t, vsl, -CELL, 0, True, hry, hns, vrx, vns, 'V')
        if nt is not None:
            out.append((hry, hns, nx, vns, nt, 'VL'))

    # VR: move V-rack right
    nx = vrx + CELL
    if nx + 6 <= FXX:
        nt = domv(t, vsl, CELL, 0, True, hry, hns, vrx, vns, 'V')
        if nt is not None:
            out.append((hry, hns, nx, vns, nt, 'VR'))

    return out


def solve():
    """A* search for L7 solution."""
    # Initial tiles (sprite coordinates)
    t0 = (
        (23, 20, 8),   # upper-left 8
        (29, 20, 9),   # upper-right 9
        (23, 26, 9),   # lower-left 9
        (29, 26, 8),   # lower-right 8
        (35, 32, 14),  # e block
    )
    # Initial state
    hry0 = 26  # H-rack y (cage6 interior top in sprite coords = 26?)
    hns0 = 1   # H-rack initial segments
    vrx0 = 29  # V-rack x (cage15 interior in sprite coords)
    vns0 = 1   # V-rack initial segments

    s0 = (hry0, hns0, vrx0, vns0, t0)
    h0 = heur(*s0)

    # A* priority queue
    pq = [(h0, 0, s0, [])]
    vis = {}
    mx = 63  # baseline
    it = 0
    t_start = time.time()

    print(f"Initial state: hry={hry0}, hns={hns0}, vrx={vrx0}, vns={vns0}")
    print(f"Tiles: {t0}")
    print(f"Initial heuristic: {h0}")
    print(f"Target H-rack: 9@{H_RX}, 14@{H_RX+CELL}, 9@{H_RX+2*CELL} at y=hry")
    print(f"Target V-rack: 8@y={V_BY}, 14@y={V_BY+CELL}, 8@y={V_BY+2*CELL} at x=vrx")

    while pq:
        f, g, (hry, hns, vrx, vns, t), path = heapq.heappop(pq)
        if g >= mx:
            continue
        sk = mkey(hry, hns, vrx, vns, t)
        if sk in vis and vis[sk] <= g:
            continue
        vis[sk] = g

        it += 1
        if it % 100000 == 0:
            elapsed = time.time() - t_start
            print(f"  i={it} f={f} g={g} pq={len(pq)} vis={len(vis)} t={elapsed:.0f}s", flush=True)

        for nhry, nhns, nvrx, nvns, nt, a in succs(hry, hns, vrx, vns, t):
            ng = g + 1
            nsk = mkey(nhry, nhns, nvrx, nvns, nt)
            if nsk in vis and vis[nsk] <= ng:
                continue
            if chkw(nhry, nhns, nvrx, nvns, nt):
                elapsed = time.time() - t_start
                npath = path + [a]
                print(f"\n*** SOLUTION FOUND at depth {ng}! ***")
                print(f"  Path: {' '.join(npath)}")
                print(f"  Iterations: {it}, Visited: {len(vis)}, Time: {elapsed:.1f}s")
                return npath

            h = heur(nhry, nhns, nvrx, nvns, nt)
            if ng + h < mx:
                heapq.heappush(pq, (ng + h, ng, (nhry, nhns, nvrx, nvns, nt), path + [a]))

    elapsed = time.time() - t_start
    print(f"\nNo solution found (mx={mx}, i={it}, vis={len(vis)}, t={elapsed:.0f}s)")
    return None


if __name__ == '__main__':
    path = solve()
    if path:
        print(f"\nSolution ({len(path)} steps): {' '.join(path)}")
        # Map to game actions
        action_map = {
            'HU': 'ACTION1 (up)',
            'HD': 'ACTION2 (down)',
            'HL': 'ACTION3 (eject left)',
            'HR': 'ACTION4 (extend right)',
            'VD': 'ACTION2 after click (extend V down)',
            'VU': 'ACTION1 after click (eject V up)',
            'VL': 'ACTION3 after click (move V left)',
            'VR': 'ACTION4 after click (move V right)',
        }
        for a in path:
            print(f"  {a} = {action_map.get(a, a)}")
