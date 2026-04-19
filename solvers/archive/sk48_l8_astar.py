#!/usr/bin/env python3
"""SK48 L8 — A* solver. 4 blocks, 4 slots, no sharing needed.
Blocks: 9@(29,14), 14@(29,38), 8@(17,26), 12@(41,26)
Target H: 9@(11,hry), 14@(17,hry) — hns≥3
Target V: 8@(vrx,14), 12@(vrx,20) — vns≥3
Default: hry=26, vrx=29
"""

import heapq, time

CELL = 6; H_RX = 11; V_BY = 8
FXM = 11; FXX = 53; FYM = 8; FYX = 50; MAX_S = 8

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

def chkw(hry, hns, vrx, vns, t):
    if hns < 3 or vns < 3: return False
    if hry != 26 or vrx != 29: return False
    # H: 9@(11,26), 14@(17,26)
    h0 = tat(t, 11, 26); h1 = tat(t, 17, 26)
    if h0 < 0 or t[h0][2] != 9 or h1 < 0 or t[h1][2] != 14: return False
    # V: 8@(29,14), 12@(29,20)
    v0 = tat(t, 29, 14); v1 = tat(t, 29, 20)
    return v0 >= 0 and t[v0][2] == 8 and v1 >= 0 and t[v1][2] == 12

def heur(hry, hns, vrx, vns, t):
    h = 0
    # H: 9→(11,26), 14→(17,26)
    for tx, ty, tc in [(11, 26, 9), (17, 26, 14)]:
        ti = tat(t, tx, ty)
        if ti < 0 or t[ti][2] != tc:
            best = 99
            for bx, by, bc in t:
                if bc == tc:
                    best = min(best, abs(bx-tx)//CELL + abs(by-ty)//CELL)
            h += best
    # V: 8→(29,14), 12→(29,20)
    for tx, ty, tc in [(29, 14, 8), (29, 20, 12)]:
        ti = tat(t, tx, ty)
        if ti < 0 or t[ti][2] != tc:
            best = 99
            for bx, by, bc in t:
                if bc == tc:
                    best = min(best, abs(bx-tx)//CELL + abs(by-ty)//CELL)
            h += best
    h += abs(hry-26)//CELL + abs(vrx-29)//CELL
    h += max(0, 3-hns) + max(0, 3-vns)
    return h

def mkey(hry, hns, vrx, vns, t):
    return (hry, hns, vrx, vns, frozenset(t))

def succs(hry, hns, vrx, vns, t):
    hsl = [(H_RX+i*CELL, hry) for i in range(hns)]
    vsl = [(vrx, V_BY+i*CELL) for i in range(vns)]
    out = []
    if hns < MAX_S:
        nx = H_RX+CELL*hns
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
    if ny+CELL <= FYX:
        nt = domv(t, hsl, 0, CELL, True, hry, hns, vrx, vns, 'H')
        if nt is not None: out.append((ny, hns, vrx, vns, nt, 'HD'))
    if vns < MAX_S:
        ny = V_BY+CELL*vns
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
    if nx+CELL <= FXX:
        nt = domv(t, vsl, CELL, 0, True, hry, hns, vrx, vns, 'V')
        if nt is not None: out.append((hry, hns, nx, vns, nt, 'VR'))
    return out

def solve():
    t0 = ((29, 14, 9), (29, 38, 14), (17, 26, 8), (41, 26, 12))
    s0 = (26, 0, 29, 1, t0)
    h0 = heur(*s0)
    pq = [(h0, 0, s0, [])]
    vis = {}; mx = 92; it = 0; t_start = time.time()
    print(f"L8 A*: h0={h0}, tiles={t0}")

    while pq:
        f, g, (hry, hns, vrx, vns, t), path = heapq.heappop(pq)
        if g >= mx: continue
        sk = mkey(hry, hns, vrx, vns, t)
        if sk in vis and vis[sk] <= g: continue
        vis[sk] = g; it += 1
        if it % 500000 == 0:
            elapsed = time.time() - t_start
            print(f"  i={it} f={f} g={g} vis={len(vis)} t={elapsed:.0f}s", flush=True)
        if it > 100000000: break

        for nhry, nhns, nvrx, nvns, nt, a in succs(hry, hns, vrx, vns, t):
            ng = g + 1
            nsk = mkey(nhry, nhns, nvrx, nvns, nt)
            if nsk in vis and vis[nsk] <= ng: continue
            if chkw(nhry, nhns, nvrx, nvns, nt):
                npath = path + [a]
                elapsed = time.time() - t_start
                print(f"\n*** SOLUTION at depth {ng}! ***")
                print(f"  Path: {' '.join(npath)}")
                print(f"  Tiles: {nt}")
                print(f"  i={it}, vis={len(vis)}, t={elapsed:.1f}s")
                return npath
            nh = heur(nhry, nhns, nvrx, nvns, nt)
            if ng + nh < mx:
                heapq.heappush(pq, (ng+nh, ng, (nhry, nhns, nvrx, nvns, nt), path+[a]))

    elapsed = time.time() - t_start
    print(f"\nNo solution (i={it}, vis={len(vis)}, t={elapsed:.0f}s)")

if __name__ == '__main__':
    solve()
