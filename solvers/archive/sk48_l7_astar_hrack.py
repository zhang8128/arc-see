#!/usr/bin/env python3
"""SK48 L7 — A* to find H-rack solution only (9,14,9 at hry=26).

The V-rack can be anywhere. Just get the H-rack loaded correctly.
Uses v1 model (exact position matching — confirmed to match game for CELL-aligned tiles).
"""

import heapq
import time

CELL = 6
H_RX = 11
V_BY = 8
FXM = 11; FXX = 53; FYM = 8; FYX = 50
MAX_S = 8

def inf(x, y):
    return FXM <= x <= FXX - CELL and FYM <= y <= FYX - CELL

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
    m.add(idx)
    return True

def domv(t, sl, dx, dy, perp, hry, hns, vrx, vns, w):
    m = set()
    for sx, sy in sl:
        for cx, cy in ((sx, sy), (sx + dx, sy + dy)):
            ti = tat(t, cx, cy)
            if ti >= 0 and ti not in m:
                if not push(t, ti, dx, dy, m, hry, hns, vrx, vns, w):
                    if perp: return None
    r = list(t)
    for i in m:
        r[i] = (t[i][0] + dx, t[i][1] + dy, t[i][2])
    return tuple(r)

def chkw(hry, hns, vrx, vns, t):
    """Win: H=9,14,9 at hry=20 + V=8,14,8 at vrx=17.
    V_BY=8. e at intersection (17,20) = H slot 1 = V vjfbwggsd[1].
    V-rack with vns>=4: segments at y=8,14,20,26. No block at y=8 (cage interior).
    vjfbwggsd = [block@(vrx,14), block@(vrx,20), block@(vrx,26)] → 8,14,8.
    """
    if hns < 3 or vns < 4: return False
    if hry != 20 or vrx != 17: return False
    # H-rack: 9@(11,20), 14@(17,20), 9@(23,20)
    h0 = tat(t, H_RX, 20)
    h1 = tat(t, H_RX + CELL, 20)
    h2 = tat(t, H_RX + 2*CELL, 20)
    if not (h0 >= 0 and t[h0][2] == 9 and
            h1 >= 0 and t[h1][2] == 14 and
            h2 >= 0 and t[h2][2] == 9): return False
    # V-rack: 8@(17,14), 14@(17,20), 8@(17,26)
    v0 = tat(t, 17, 14)
    v1 = tat(t, 17, 20)
    v2 = tat(t, 17, 26)
    return (v0 >= 0 and t[v0][2] == 8 and
            v1 >= 0 and t[v1][2] == 14 and
            v2 >= 0 and t[v2][2] == 8)

def heur(hry, hns, vrx, vns, t):
    h = 0
    # Target: e@(17,20) shared. H: 9@(11,20), 9@(23,20). V: 8@(17,14), 8@(17,26).
    TH = 20  # target hry
    TV = 17  # target vrx

    for tx in [H_RX, H_RX + 2*CELL]:  # 9s at (11,20) and (23,20)
        ti = tat(t, tx, TH)
        if ti < 0 or t[ti][2] != 9:
            best = 99
            for bx, by, bc in t:
                if bc == 9:
                    best = min(best, abs(bx - tx) // CELL + abs(by - TH) // CELL)
            h += best

    for ty in [14, 26]:  # 8s at (17,14) and (17,26)
        ti = tat(t, TV, ty)
        if ti < 0 or t[ti][2] != 8:
            best = 99
            for bx, by, bc in t:
                if bc == 8:
                    best = min(best, abs(bx - TV) // CELL + abs(by - ty) // CELL)
            h += best

    # e → (17,20) once
    ti = tat(t, TV, TH)
    if ti < 0 or t[ti][2] != 14:
        best = 99
        for bx, by, bc in t:
            if bc == 14:
                best = min(best, abs(bx - TV) // CELL + abs(by - TH) // CELL)
        h += best

    h += abs(hry - TH) // CELL + abs(vrx - TV) // CELL
    h += max(0, 3 - hns) + max(0, 4 - vns)
    h += max(0, 3 - hns) + max(0, 3 - vns)
    return h

def mkey(hry, hns, vrx, vns, t):
    return (hry, hns, vrx, vns, frozenset((tx, ty, tc) for tx, ty, tc in t))

def succs(hry, hns, vrx, vns, t):
    hsl = [(H_RX + i * CELL, hry) for i in range(hns)]
    vsl = [(vrx, V_BY + i * CELL) for i in range(vns)]
    out = []
    if hns < MAX_S:
        nx = H_RX + CELL * hns
        if inf(nx, hry):
            nt = domv(t, hsl, CELL, 0, False, hry, hns, vrx, vns, 'H')
            if nt is not None: out.append((hry, hns+1, vrx, vns, nt, 'HR'))
    if hns > 1:
        nt = domv(t, hsl[1:], -CELL, 0, False, hry, hns, vrx, vns, 'H')
        if nt is not None: out.append((hry, hns-1, vrx, vns, nt, 'HL'))
    ny = hry - CELL
    if ny >= FYM:
        nt = domv(t, hsl, 0, -CELL, True, hry, hns, vrx, vns, 'H')
        if nt is not None: out.append((ny, hns, vrx, vns, nt, 'HU'))
    ny = hry + CELL
    if ny + CELL <= FYX:
        nt = domv(t, hsl, 0, CELL, True, hry, hns, vrx, vns, 'H')
        if nt is not None: out.append((ny, hns, vrx, vns, nt, 'HD'))
    if vns < MAX_S:
        ny = V_BY + CELL * vns
        if inf(vrx, ny):
            nt = domv(t, vsl, 0, CELL, False, hry, hns, vrx, vns, 'V')
            if nt is not None: out.append((hry, hns, vrx, vns+1, nt, 'VD'))
    if vns > 1:
        nt = domv(t, vsl[1:], 0, -CELL, False, hry, hns, vrx, vns, 'V')
        if nt is not None: out.append((hry, hns, vrx, vns-1, nt, 'VU'))
    nx = vrx - CELL
    if nx >= FXM:
        nt = domv(t, vsl, -CELL, 0, True, hry, hns, vrx, vns, 'V')
        if nt is not None: out.append((hry, hns, nx, vns, nt, 'VL'))
    nx = vrx + CELL
    if nx + CELL <= FXX:
        nt = domv(t, vsl, CELL, 0, True, hry, hns, vrx, vns, 'V')
        if nt is not None: out.append((hry, hns, nx, vns, nt, 'VR'))
    return out

def solve():
    t0 = ((23, 20, 8), (29, 20, 9), (23, 26, 9), (29, 26, 8), (35, 32, 14))
    s0 = (26, 1, 29, 1, t0)
    h0 = heur(*s0)
    pq = [(h0, 0, s0, [])]
    vis = {}
    mx = 63  # baseline
    it = 0
    t_start = time.time()
    print(f"Target: H=9,14,9 @y=26 + V=8,_,8 @x=29 (V_BY={V_BY})")
    print(f"V-rack target: 8@(29,{V_BY}), 8@(29,{V_BY+2*CELL})")
    print(f"Initial heuristic: {h0}")

    while pq:
        f, g, (hry, hns, vrx, vns, t), path = heapq.heappop(pq)
        if g >= mx: continue
        sk = mkey(hry, hns, vrx, vns, t)
        if sk in vis and vis[sk] <= g: continue
        vis[sk] = g
        it += 1
        if it % 500000 == 0:
            elapsed = time.time() - t_start
            print(f"  i={it} f={f} g={g} vis={len(vis)} t={elapsed:.0f}s", flush=True)
        if it > 150000000: break

        for nhry, nhns, nvrx, nvns, nt, a in succs(hry, hns, vrx, vns, t):
            ng = g + 1
            nsk = mkey(nhry, nhns, nvrx, nvns, nt)
            if nsk in vis and vis[nsk] <= ng: continue
            if chkw(nhry, nhns, nvrx, nvns, nt):
                npath = path + [a]
                elapsed = time.time() - t_start
                print(f"\n*** H-RACK COMPLETE at depth {ng}! ***")
                print(f"  Path: {' '.join(npath)}")
                print(f"  Tiles: {nt}")
                print(f"  State: hry={nhry} hns={nhns} vrx={nvrx} vns={nvns}")
                print(f"  i={it}, vis={len(vis)}, t={elapsed:.1f}s")
                return npath
            nh = heur(nhry, nhns, nvrx, nvns, nt)
            if ng + nh < mx:
                heapq.heappush(pq, (ng + nh, ng, (nhry, nhns, nvrx, nvns, nt), path + [a]))

    elapsed = time.time() - t_start
    print(f"\nNo solution (i={it}, vis={len(vis)}, t={elapsed:.0f}s)")

if __name__ == '__main__':
    solve()
