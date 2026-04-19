#!/usr/bin/env python3
"""SK48 L6 — Pure Python A* solver.

H-rack (5,26) needs [9,9,9], V-rack ref (29,2) needs [8,8,8].
Obstacle at (29,26). No permanent segment blocking.
"""
import heapq

CELL = 6
H_RX = 5; V_BY = 2
FXM, FXX = 11, 53; FYM, FYX = 8, 50
MAX_S = 12
OBS = frozenset([(29, 26)])
VRYS = (10, 16, 22, 28, 34, 40)
HRXS = (13, 19, 25, 31, 37, 43)

def inf(x, y): return FXM <= x and x + 6 <= FXX and FYM <= y and y + 6 <= FYX
def hrU(ry): return any(y <= ry-1 < y+8 for y in VRYS)
def hrD(ry): return any(y <= ry+5 < y+8 for y in VRYS)
def vrL(rx): return any(x <= rx-1 < x+8 for x in HRXS)
def vrR(rx): return any(x <= rx+5 < x+8 for x in HRXS)

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

def chkw(hry, hns, vrx, vns, t):
    hc = []
    for i in range(hns):
        ti = tat(t, H_RX + CELL*i, hry)
        if ti >= 0: hc.append(t[ti][2])
    if len(hc) < 3 or tuple(hc[:3]) != (9,9,9): return False
    vc = []
    for i in range(vns):
        ti = tat(t, vrx, V_BY + CELL*i)
        if ti >= 0: vc.append(t[ti][2])
    return len(vc) >= 3 and tuple(vc[:3]) == (8,8,8)

def mkey(hry, hns, vrx, vns, t):
    p9 = frozenset((tx, ty) for tx, ty, tc in t if tc == 9)
    p8 = frozenset((tx, ty) for tx, ty, tc in t if tc == 8)
    return (hry, hns, vrx, vns, p9, p8)

def heur(hry, hns, vrx, vns, t):
    h_on = 0
    for i in range(hns):
        ti = tat(t, H_RX+CELL*i, hry)
        if ti >= 0 and t[ti][2] == 9: h_on += 1
    v_on = 0
    for i in range(vns):
        ti = tat(t, vrx, V_BY+CELL*i)
        if ti >= 0 and t[ti][2] == 8: v_on += 1
    return max(0, 3-h_on) + max(0, 3-v_on) + max(0, 3-hns) + max(0, 3-vns)

def succs(hry, hns, vrx, vns, t):
    hsl = [(H_RX + i*CELL, hry) for i in range(hns)]
    vsl = [(vrx, V_BY + i*CELL) for i in range(vns)]
    out = []

    # H-RIGHT (extend)
    if hns < MAX_S:
        nx = H_RX + CELL * hns
        if (nx, hry) not in OBS and (inf(nx, hry) or not inf(H_RX+CELL*(hns-1), hry)):
            nt = domv(t, hsl, CELL, 0, False)
            if nt is not None: out.append((hry, hns+1, vrx, vns, nt, 'HR'))
    # H-LEFT (shrink)
    if hns > 1:
        nt = domv(t, hsl[1:], -CELL, 0, False)
        if nt is not None: out.append((hry, hns-1, vrx, vns, nt, 'HL'))
    # H-UP
    if hrU(hry) and hry-CELL >= FYM:
        ny = hry - CELL
        if all((H_RX+i*CELL, ny) not in OBS and (inf(H_RX+i*CELL, ny) or not inf(H_RX+i*CELL, hry)) for i in range(hns)):
            nt = domv(t, hsl, 0, -CELL, True)
            if nt is not None: out.append((ny, hns, vrx, vns, nt, 'HU'))
    # H-DOWN
    if hrD(hry) and hry+CELL+6 <= FYX:
        ny = hry + CELL
        if all((H_RX+i*CELL, ny) not in OBS and (inf(H_RX+i*CELL, ny) or not inf(H_RX+i*CELL, hry)) for i in range(hns)):
            nt = domv(t, hsl, 0, CELL, True)
            if nt is not None: out.append((ny, hns, vrx, vns, nt, 'HD'))

    # V-DOWN (extend)
    if vns < MAX_S:
        ny = V_BY + CELL * vns
        if (vrx, ny) not in OBS and (inf(vrx, ny) or not inf(vrx, V_BY+CELL*(vns-1))):
            nt = domv(t, vsl, 0, CELL, False)
            if nt is not None: out.append((hry, hns, vrx, vns+1, nt, 'VD'))
    # V-UP (shrink)
    if vns > 1:
        nt = domv(t, vsl[1:], 0, -CELL, False)
        if nt is not None: out.append((hry, hns, vrx, vns-1, nt, 'VU'))
    # V-LEFT
    if vrL(vrx) and vrx-CELL >= FXM:
        nx = vrx - CELL
        if all((nx, V_BY+i*CELL) not in OBS and (inf(nx, V_BY+i*CELL) or not inf(vrx, V_BY+i*CELL)) for i in range(vns)):
            nt = domv(t, vsl, -CELL, 0, True)
            if nt is not None: out.append((hry, hns, nx, vns, nt, 'VL'))
    # V-RIGHT
    if vrR(vrx) and vrx+CELL+6 <= FXX:
        nx = vrx + CELL
        if all((nx, V_BY+i*CELL) not in OBS and (inf(nx, V_BY+i*CELL) or not inf(vrx, V_BY+i*CELL)) for i in range(vns)):
            nt = domv(t, vsl, CELL, 0, True)
            if nt is not None: out.append((hry, hns, nx, vns, nt, 'VR'))

    return out

def solve():
    t0 = ((35,26,9), (41,26,9), (47,26,9), (29,32,8), (29,38,8), (29,44,8))
    s0 = (26, 2, 29, 2, t0)
    h0 = heur(*s0)
    pq = [(h0, 0, s0, [])]
    vis = {}
    mx = 55
    it = 0

    while pq:
        f, g, (hry, hns, vrx, vns, t), path = heapq.heappop(pq)
        if g >= mx: continue
        sk = mkey(hry, hns, vrx, vns, t)
        if sk in vis and vis[sk] <= g: continue
        vis[sk] = g
        it += 1
        if it % 500000 == 0:
            print(f"  i={it} f={f} g={g} pq={len(pq)} vis={len(vis)}")

        for nhry, nhns, nvrx, nvns, nt, a in succs(hry, hns, vrx, vns, t):
            ng = g + 1
            nsk = mkey(nhry, nhns, nvrx, nvns, nt)
            if nsk in vis and vis[nsk] <= ng: continue
            if chkw(nhry, nhns, nvrx, nvns, nt):
                np_ = path + [a]
                print(f"\n*** SOLUTION ({len(np_)} actions): {' '.join(np_)} ***")
                print(f"Iterations: {it}, Visited: {len(vis)}")
                return np_
            h = heur(nhry, nhns, nvrx, nvns, nt)
            if ng + h < mx:
                heapq.heappush(pq, (ng + h, ng, (nhry, nhns, nvrx, nvns, nt), path + [a]))

    print(f"No solution (mx={mx}, it={it}, vis={len(vis)})")
    return None

if __name__ == "__main__":
    print("SK48 L6 Fast Solver")
    print(f"Initial: H-rack y=26 n=2, V-rack x=29 n=2")
    solve()
