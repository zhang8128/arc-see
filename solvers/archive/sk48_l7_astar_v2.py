#!/usr/bin/env python3
"""SK48 L7 — Pure-Python A* v2 with area-based collision.

Key fix: tiles occupy a 6x6 area (CELL x CELL). The rack scan column
at vrx occupies x=vrx to vrx+1 (2 pixels wide). A tile at position (tx,ty)
spans tx to tx+5. Collision occurs when the scan overlaps the tile.

For V-rack movement (VL/VR): scan at vrx, tile at tx.
  Overlap if tx <= vrx+1 AND vrx <= tx+5
  Simplified: abs(vrx - tx) < CELL (within 6 of each other)

But the L6 model used exact position matching (tile at tx==vrx).
The game pushes tiles that are NEAR the rack, not just exactly on it.

From the game trace observations:
- Tiles at x=29 get pushed by V-rack at vrx=29 ✓ (exact match)
- Tiles at x=23 get pushed by V-rack at vrx=29 during VL (sweep pushes)
- Tiles at x=35 get pushed by V-rack at vrx=29 during VR

The push happens during MOVEMENT: when the rack sweeps from old to new position,
all tiles in the sweep path get pushed. This is different from the L6 model
which only pushes tiles at exact segment positions.

For VL (move V-rack left by CELL): vrx_old → vrx_new = vrx_old - CELL
  Tiles between vrx_new and vrx_old (exclusive) get pushed left.
  A tile at tx is pushed if vrx_new <= tx < vrx_old
  (The rack sweeps through these positions)

For VR: tiles at vrx_old < tx <= vrx_new get pushed right.

For VD (extend V down): new segment at y = V_BY + vns*CELL
  Tiles at that y-position (within CELL range) get pushed down.

Similarly for H-rack:
  HR: tiles at x = H_RX + hns*CELL get pushed right
  HL: tiles in the retracted range get pushed left
  HU/HD: tiles between old and new hry get pushed up/down

Let me implement a sweep-based push model.
"""

import heapq
import time

CELL = 6
H_RX = 11
V_BY = 8
FXM = 11
FXX = 53
FYM = 8
FYX = 50
MAX_S = 8


def inf(x, y):
    return FXM <= x <= FXX - CELL and FYM <= y <= FYX - CELL


def tat(t, x, y):
    for i in range(len(t)):
        if t[i][0] == x and t[i][1] == y:
            return i
    return -1


def tat_near(t, x, y, axis='x', threshold=CELL):
    """Find tile near (x,y). For V-rack push, match tiles at same y but near x."""
    for i in range(len(t)):
        if axis == 'x':  # V-rack: match by y exactly, x within range
            if t[i][1] == y and abs(t[i][0] - x) < threshold:
                return i
        else:  # H-rack: match by x exactly, y within range
            if t[i][0] == x and abs(t[i][1] - y) < threshold:
                return i
    return -1


def push_tile(t, idx, dx, dy, moved, max_x=FXX, max_y=FYX):
    """Push tile recursively, cascading to any tile at destination."""
    if idx in moved:
        return True
    tx, ty = t[idx][0], t[idx][1]
    nx, ny = tx + dx, ty + dy
    if not inf(nx, ny):
        return False
    # Check if destination has a tile
    dest = tat(t, nx, ny)
    if dest >= 0 and dest not in moved:
        if not push_tile(t, dest, dx, dy, moved):
            return False
    moved[idx] = (nx, ny)
    return True


def apply_moves(t, moved):
    """Apply all moves to create new tile tuple."""
    r = list(t)
    for i, (nx, ny) in moved.items():
        r[i] = (nx, ny, t[i][2])
    return tuple(r)


def do_h_extend(hry, hns, vrx, vns, t):
    """HR: extend H-rack right. Push tile at the new segment position."""
    new_x = H_RX + CELL * hns
    if not inf(new_x, hry):
        return None
    # Check cross-rack: can't extend into V-rack segment
    if new_x == vrx:
        for i in range(vns):
            if hry == V_BY + i * CELL:
                return None
    moved = {}
    ti = tat(t, new_x, hry)
    if ti >= 0:
        if not push_tile(t, ti, CELL, 0, moved):
            return None
    return (hry, hns + 1, vrx, vns, apply_moves(t, moved), 'HR')


def do_h_shrink(hry, hns, vrx, vns, t):
    """HL: shrink H-rack left. Push tiles from the retracting area leftward."""
    if hns <= 1:
        return None
    # The rightmost segment retracts. Tiles at segments get pushed left.
    moved = {}
    # Push tiles at each segment position (except slot 0) leftward
    for i in range(1, hns):
        sx = H_RX + i * CELL
        ti = tat(t, sx, hry)
        if ti >= 0 and ti not in moved:
            if not push_tile(t, ti, -CELL, 0, moved):
                pass  # Non-blocking for HL
    return (hry, hns - 1, vrx, vns, apply_moves(t, moved), 'HL')


def do_h_up(hry, hns, vrx, vns, t):
    """HU: move H-rack up. Tiles on the rack travel with it. Tiles above get pushed."""
    new_hry = hry - CELL
    if new_hry < FYM:
        return None
    moved = {}
    # Tiles AT rack positions move with the rack (travel)
    # Tiles at the DESTINATION positions get pushed up (cascade)
    for i in range(hns):
        sx = H_RX + i * CELL
        # Tile on the rack (at current position)
        ti_cur = tat(t, sx, hry)
        # Tile at destination
        ti_dest = tat(t, sx, new_hry)
        if ti_dest >= 0 and ti_dest not in moved:
            # Push destination tile up
            if not push_tile(t, ti_dest, 0, -CELL, moved):
                return None  # Blocked
        if ti_cur >= 0 and ti_cur not in moved:
            # Move rack tile with rack
            moved[ti_cur] = (sx, new_hry)
    return (new_hry, hns, vrx, vns, apply_moves(t, moved), 'HU')


def do_h_down(hry, hns, vrx, vns, t):
    """HD: move H-rack down."""
    new_hry = hry + CELL
    if new_hry + CELL > FYX:
        return None
    moved = {}
    for i in range(hns):
        sx = H_RX + i * CELL
        ti_dest = tat(t, sx, new_hry)
        if ti_dest >= 0 and ti_dest not in moved:
            if not push_tile(t, ti_dest, 0, CELL, moved):
                return None
        ti_cur = tat(t, sx, hry)
        if ti_cur >= 0 and ti_cur not in moved:
            moved[ti_cur] = (sx, new_hry)
    return (new_hry, hns, vrx, vns, apply_moves(t, moved), 'HD')


def do_v_extend(hry, hns, vrx, vns, t):
    """VD: extend V-rack down."""
    new_y = V_BY + CELL * vns
    if not inf(vrx, new_y):
        return None
    moved = {}
    ti = tat(t, vrx, new_y)
    if ti >= 0:
        if not push_tile(t, ti, 0, CELL, moved):
            return None
    return (hry, hns, vrx, vns + 1, apply_moves(t, moved), 'VD')


def do_v_shrink(hry, hns, vrx, vns, t):
    """VU: shrink V-rack up."""
    if vns <= 1:
        return None
    moved = {}
    for i in range(1, vns):
        sy = V_BY + i * CELL
        ti = tat(t, vrx, sy)
        if ti >= 0 and ti not in moved:
            if not push_tile(t, ti, 0, -CELL, moved):
                pass
    return (hry, hns, vrx, vns - 1, apply_moves(t, moved), 'VU')


def do_v_left(hry, hns, vrx, vns, t):
    """VL: move V-rack left. SWEEP push: all tiles in sweep path get pushed."""
    new_vrx = vrx - CELL
    if new_vrx < FXM:
        return None
    moved = {}
    # Sweep from vrx-1 down to new_vrx. Any tile in the V-rack's y-range gets pushed.
    for i in range(vns):
        sy = V_BY + i * CELL
        # Find tiles in the sweep range at this y
        # Sweep: tiles with tx in [new_vrx, vrx) get pushed left
        for ti in range(len(t)):
            if ti in moved:
                continue
            tx, ty, tc = t[ti]
            if ty == sy and new_vrx <= tx < vrx:
                if not push_tile(t, ti, -CELL, 0, moved):
                    return None  # V-rack movement is blocked
    # Also push tiles exactly at vrx (they travel with the rack)
    for i in range(vns):
        sy = V_BY + i * CELL
        ti = tat(t, vrx, sy)
        if ti >= 0 and ti not in moved:
            moved[ti] = (new_vrx, sy)
    return (hry, hns, new_vrx, vns, apply_moves(t, moved), 'VL')


def do_v_right(hry, hns, vrx, vns, t):
    """VR: move V-rack right. SWEEP push."""
    new_vrx = vrx + CELL
    if new_vrx + CELL > FXX:
        return None
    moved = {}
    for i in range(vns):
        sy = V_BY + i * CELL
        for ti in range(len(t)):
            if ti in moved:
                continue
            tx, ty, tc = t[ti]
            if ty == sy and vrx < tx <= new_vrx:
                if not push_tile(t, ti, CELL, 0, moved):
                    return None
    for i in range(vns):
        sy = V_BY + i * CELL
        ti = tat(t, vrx, sy)
        if ti >= 0 and ti not in moved:
            moved[ti] = (new_vrx, sy)
    return (hry, hns, new_vrx, vns, apply_moves(t, moved), 'VR')


def succs(hry, hns, vrx, vns, t):
    out = []
    for fn in [do_h_extend, do_h_shrink, do_h_up, do_h_down,
               do_v_extend, do_v_shrink, do_v_left, do_v_right]:
        result = fn(hry, hns, vrx, vns, t)
        if result is not None:
            out.append(result)
    return out


def chkw(hry, hns, vrx, vns, t):
    """Win: H-rack has 9,14,9 at slots 0-2, V-rack has 8,14,8 at slots 0-2.
    Both racks at original positions."""
    if hry != 26 or vrx != 29:
        return False
    if hns < 3 or vns < 3:
        return False
    # H-rack
    h0 = tat(t, H_RX, hry)
    h1 = tat(t, H_RX + CELL, hry)
    h2 = tat(t, H_RX + 2*CELL, hry)
    if h0 < 0 or t[h0][2] != 9: return False
    if h1 < 0 or t[h1][2] != 14: return False
    if h2 < 0 or t[h2][2] != 9: return False
    # V-rack
    v0 = tat(t, vrx, V_BY)
    v1 = tat(t, vrx, V_BY + CELL)
    v2 = tat(t, vrx, V_BY + 2*CELL)
    if v0 < 0 or t[v0][2] != 8: return False
    if v1 < 0 or t[v1][2] != 14: return False
    if v2 < 0 or t[v2][2] != 8: return False
    return True


def chkw_partial(hry, hns, vrx, vns, t):
    """Relaxed win: just 9s and 8s, no e required, racks at original pos."""
    if hry != 26 or vrx != 29:
        return False
    if hns < 3 or vns < 3:
        return False
    h0 = tat(t, H_RX, hry)
    h2 = tat(t, H_RX + 2*CELL, hry)
    v0 = tat(t, vrx, V_BY)
    v2 = tat(t, vrx, V_BY + 2*CELL)
    return (h0 >= 0 and t[h0][2] == 9 and h2 >= 0 and t[h2][2] == 9 and
            v0 >= 0 and t[v0][2] == 8 and v2 >= 0 and t[v2][2] == 8)


def heur(hry, hns, vrx, vns, t):
    h = 0
    # H-rack targets
    for tx, tc in [(H_RX, 9), (H_RX+CELL, 14), (H_RX+2*CELL, 9)]:
        ti = tat(t, tx, 26)  # target hry=26
        if ti < 0 or t[ti][2] != tc:
            best = 99
            for bx, by, bc in t:
                if bc == tc:
                    d = abs(bx - tx) // CELL + abs(by - 26) // CELL
                    best = min(best, d)
            h += best
    # V-rack targets
    for ty, tc in [(V_BY, 8), (V_BY+CELL, 14), (V_BY+2*CELL, 8)]:
        ti = tat(t, 29, ty)  # target vrx=29
        if ti < 0 or t[ti][2] != tc:
            best = 99
            for bx, by, bc in t:
                if bc == tc:
                    d = abs(bx - 29) // CELL + abs(by - ty) // CELL
                    best = min(best, d)
            h += best
    # Rack position penalty
    h += abs(hry - 26) // CELL + abs(vrx - 29) // CELL
    h += max(0, 3 - hns) + max(0, 3 - vns)
    return h


def mkey(hry, hns, vrx, vns, t):
    return (hry, hns, vrx, vns, frozenset((tx, ty, tc) for tx, ty, tc in t))


def solve():
    t0 = ((23, 20, 8), (29, 20, 9), (23, 26, 9), (29, 26, 8), (35, 32, 14))
    s0 = (26, 1, 29, 1, t0)
    h0 = heur(*s0)
    pq = [(h0, 0, s0, [])]
    vis = {}
    mx = 63
    it = 0
    t_start = time.time()

    print(f"Initial heuristic: {h0}")
    print(f"Tiles: {t0}")

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
        if it > 10000000:
            break

        for nhry, nhns, nvrx, nvns, nt, a in succs(hry, hns, vrx, vns, t):
            ng = g + 1
            nsk = mkey(nhry, nhns, nvrx, nvns, nt)
            if nsk in vis and vis[nsk] <= ng:
                continue

            # Check both win conditions
            if chkw(nhry, nhns, nvrx, nvns, nt):
                npath = path + [a]
                elapsed = time.time() - t_start
                print(f"\n*** FULL WIN at depth {ng}! ***")
                print(f"  Path: {' '.join(npath)}")
                print(f"  i={it}, vis={len(vis)}, t={elapsed:.1f}s")
                return npath

            if chkw_partial(nhry, nhns, nvrx, nvns, nt):
                npath = path + [a]
                elapsed = time.time() - t_start
                print(f"\n*** PARTIAL WIN (no e) at depth {ng} ***")
                print(f"  Path: {' '.join(npath)}")
                print(f"  Tiles: {nt}")
                # Don't return — keep searching for full win

            nh = heur(nhry, nhns, nvrx, nvns, nt)
            if ng + nh < mx:
                heapq.heappush(pq, (ng + nh, ng, (nhry, nhns, nvrx, nvns, nt), path + [a]))

    elapsed = time.time() - t_start
    print(f"\nSearch complete: i={it}, vis={len(vis)}, t={elapsed:.0f}s")
    return None


if __name__ == '__main__':
    solve()
