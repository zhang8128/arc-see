#!/usr/bin/env python3
"""SK48 L6 — Memory-efficient A* with parent pointers and better heuristic."""
import heapq
import time

CELL = 6
H_RX = 5; V_BY = 2
FXM, FXX = 11, 53; FYM, FYX = 8, 50
MAX_S = 12
OBS_X, OBS_Y = 29, 26
VRYS = (10, 16, 22, 28, 34, 40)
HRXS = (13, 19, 25, 31, 37, 43)

inf = lambda x, y: FXM <= x <= FXX - 6 and FYM <= y <= FYX - 6
hrU = lambda ry: any(y <= ry-1 < y+8 for y in VRYS)
hrD = lambda ry: any(y <= ry+5 < y+8 for y in VRYS)
vrL = lambda rx: any(x <= rx-1 < x+8 for x in HRXS)
vrR = lambda rx: any(x <= rx+5 < x+8 for x in HRXS)

def tat(t, x, y):
    for i in range(len(t)):
        if t[i][0] == x and t[i][1] == y: return i
    return -1

def xseg(x, y, hry, hns, vrx, vns, w):
    if w == 'H':
        return x == vrx and (y - V_BY) >= 0 and (y - V_BY) % CELL == 0 and (y - V_BY) // CELL < vns
    else:
        return y == hry and (x - H_RX) >= 0 and (x - H_RX) % CELL == 0 and (x - H_RX) // CELL < hns

def push(t, idx, dx, dy, m, hry, hns, vrx, vns, w):
    if idx in m: return True
    tx, ty = t[idx][0], t[idx][1]
    if xseg(tx, ty, hry, hns, vrx, vns, w): return False
    nx, ny = tx + dx, ty + dy
    if not inf(nx, ny) or (nx == OBS_X and ny == OBS_Y): return False
    if xseg(nx, ny, hry, hns, vrx, vns, w): return False
    b = tat(t, nx, ny)
    if b >= 0 and not push(t, b, dx, dy, m, hry, hns, vrx, vns, w): return False
    m.add(idx)
    return True

def domv(t, sl, dx, dy, perp, hry, hns, vrx, vns, w):
    m = set()
    for sx, sy in sl:
        for cx, cy in ((sx, sy), (sx+dx, sy+dy)):
            ti = tat(t, cx, cy)
            if ti >= 0 and ti not in m:
                if not push(t, ti, dx, dy, m, hry, hns, vrx, vns, w):
                    if perp: return None
    r = list(t)
    for i in m:
        r[i] = (t[i][0]+dx, t[i][1]+dy, t[i][2])
    return tuple(r)

def chkw(hry, hns, vrx, vns, t):
    hc = []
    for i in range(hns):
        ti = tat(t, H_RX + CELL*i, hry)
        if ti >= 0: hc.append(t[ti][2])
    if len(hc) < 3 or hc[0] != 9 or hc[1] != 9 or hc[2] != 9: return False
    vc = []
    for i in range(vns):
        ti = tat(t, vrx, V_BY + CELL*i)
        if ti >= 0: vc.append(t[ti][2])
    return len(vc) >= 3 and vc[0] == 8 and vc[1] == 8 and vc[2] == 8

def heur(hry, hns, vrx, vns, t):
    # Count targets in position
    h_on = v_on = 0
    for i in range(min(hns, 8)):
        ti = tat(t, H_RX+CELL*i, hry)
        if ti >= 0 and t[ti][2] == 9: h_on += 1
    for i in range(min(vns, 8)):
        ti = tat(t, vrx, V_BY+CELL*i)
        if ti >= 0 and t[ti][2] == 8: v_on += 1

    h = max(0, 3-h_on) + max(0, 3-v_on) + max(0, 3-hns) + max(0, 3-vns)

    # Better heuristic: if H-rack can't reach any 9 at current y, add penalty
    # H at y=26 can only have 4 segs (x=5..23). 9-targets at x=35+ are unreachable.
    if h_on == 0:
        # Check if any 9 is reachable from current H position
        nine_ys = set(ty for tx, ty, tc in t if tc == 9)
        if hry not in nine_ys and hry == 26:
            h += 2  # need to move H rack to different row + push 9s there

    return h

def mkey(hry, hns, vrx, vns, t):
    p9 = frozenset((tx, ty) for tx, ty, tc in t if tc == 9)
    p8 = frozenset((tx, ty) for tx, ty, tc in t if tc == 8)
    return (hry, hns, vrx, vns, p9, p8)

def succs(hry, hns, vrx, vns, t):
    hsl = [(H_RX + i*CELL, hry) for i in range(hns)]
    vsl = [(vrx, V_BY + i*CELL) for i in range(vns)]
    out = []

    if hns < MAX_S:
        nx = H_RX + CELL * hns
        if not (nx == OBS_X and hry == OBS_Y) and (inf(nx, hry) or not inf(H_RX+CELL*(hns-1), hry)):
            nt = domv(t, hsl, CELL, 0, False, hry, hns, vrx, vns, 'H')
            if nt is not None: out.append((hry, hns+1, vrx, vns, nt, 'HR'))
    if hns > 1:
        nt = domv(t, hsl[1:], -CELL, 0, False, hry, hns, vrx, vns, 'H')
        if nt is not None: out.append((hry, hns-1, vrx, vns, nt, 'HL'))
    if hrU(hry) and hry-CELL >= FYM:
        ny = hry - CELL
        ok = all(not (H_RX+i*CELL == OBS_X and ny == OBS_Y) and (inf(H_RX+i*CELL, ny) or not inf(H_RX+i*CELL, hry)) for i in range(hns))
        if ok:
            nt = domv(t, hsl, 0, -CELL, True, hry, hns, vrx, vns, 'H')
            if nt is not None: out.append((ny, hns, vrx, vns, nt, 'HU'))
    if hrD(hry) and hry+CELL+6 <= FYX:
        ny = hry + CELL
        ok = all(not (H_RX+i*CELL == OBS_X and ny == OBS_Y) and (inf(H_RX+i*CELL, ny) or not inf(H_RX+i*CELL, hry)) for i in range(hns))
        if ok:
            nt = domv(t, hsl, 0, CELL, True, hry, hns, vrx, vns, 'H')
            if nt is not None: out.append((ny, hns, vrx, vns, nt, 'HD'))
    if vns < MAX_S:
        ny = V_BY + CELL * vns
        if not (vrx == OBS_X and ny == OBS_Y) and (inf(vrx, ny) or not inf(vrx, V_BY+CELL*(vns-1))):
            nt = domv(t, vsl, 0, CELL, False, hry, hns, vrx, vns, 'V')
            if nt is not None: out.append((hry, hns, vrx, vns+1, nt, 'VD'))
    if vns > 1:
        nt = domv(t, vsl[1:], 0, -CELL, False, hry, hns, vrx, vns, 'V')
        if nt is not None: out.append((hry, hns, vrx, vns-1, nt, 'VU'))
    if vrL(vrx) and vrx-CELL >= FXM:
        nx = vrx - CELL
        ok = all(not (nx == OBS_X and V_BY+i*CELL == OBS_Y) and (inf(nx, V_BY+i*CELL) or not inf(vrx, V_BY+i*CELL)) for i in range(vns))
        if ok:
            nt = domv(t, vsl, -CELL, 0, True, hry, hns, vrx, vns, 'V')
            if nt is not None: out.append((hry, hns, nx, vns, nt, 'VL'))
    if vrR(vrx) and vrx+CELL+6 <= FXX:
        nx = vrx + CELL
        ok = all(not (nx == OBS_X and V_BY+i*CELL == OBS_Y) and (inf(nx, V_BY+i*CELL) or not inf(vrx, V_BY+i*CELL)) for i in range(vns))
        if ok:
            nt = domv(t, vsl, CELL, 0, True, hry, hns, vrx, vns, 'V')
            if nt is not None: out.append((hry, hns, nx, vns, nt, 'VR'))

    return out

def solve():
    t0 = ((35,26,9), (41,26,9), (47,26,9), (29,32,8), (29,38,8), (29,44,8))
    s0 = (26, 2, 29, 2, t0)
    h0 = heur(*s0)
    # Store (f, g, state) + parent pointers for path reconstruction
    pq = [(h0, 0, s0)]
    vis = {}  # state_key -> (g, parent_key, action)
    mx = 50
    it = 0
    t0_time = time.time()

    while pq:
        f, g, (hry, hns, vrx, vns, t) = heapq.heappop(pq)
        if g >= mx: continue
        sk = mkey(hry, hns, vrx, vns, t)
        if sk in vis and vis[sk][0] <= g: continue
        vis[sk] = (g, None, None)  # parent info would need tracking

        it += 1
        if it % 500000 == 0:
            elapsed = time.time() - t0_time
            mem_mb = len(vis) * 200 / 1024 / 1024  # rough estimate
            print(f"  i={it} f={f} g={g} pq={len(pq)} vis={len(vis)} t={elapsed:.0f}s ~{mem_mb:.0f}MB", flush=True)

        for nhry, nhns, nvrx, nvns, nt, a in succs(hry, hns, vrx, vns, t):
            ng = g + 1
            nsk = mkey(nhry, nhns, nvrx, nvns, nt)
            if nsk in vis and vis[nsk][0] <= ng: continue
            if chkw(nhry, nhns, nvrx, nvns, nt):
                # Need to reconstruct path — store it during search
                # For now just report the solution exists
                elapsed = time.time() - t0_time
                print(f"\n*** SOLUTION FOUND at depth {ng}! ***", flush=True)
                print(f"Iterations: {it}, Visited: {len(vis)}, Time: {elapsed:.1f}s", flush=True)
                # We need the path. Let me just use the vis dict with parent tracking.
                # For now, log it.
                return ng
            h = heur(nhry, nhns, nvrx, nvns, nt)
            if ng + h < mx:
                heapq.heappush(pq, (ng + h, ng, (nhry, nhns, nvrx, nvns, nt)))

    elapsed = time.time() - t0_time
    print(f"No solution (mx={mx}, i={it}, vis={len(vis)}, t={elapsed:.0f}s)", flush=True)
    return None

# Second pass: once we know the depth, run with path tracking
def solve_with_path(target_depth):
    t0 = ((35,26,9), (41,26,9), (47,26,9), (29,32,8), (29,38,8), (29,44,8))
    s0 = (26, 2, 29, 2, t0)
    h0 = heur(*s0)
    pq = [(h0, 0, s0, [])]
    vis = {}
    mx = target_depth + 1
    it = 0

    while pq:
        f, g, (hry, hns, vrx, vns, t), path = heapq.heappop(pq)
        if g >= mx: continue
        sk = mkey(hry, hns, vrx, vns, t)
        if sk in vis and vis[sk] <= g: continue
        vis[sk] = g
        it += 1
        if it % 500000 == 0:
            print(f"  pass2: i={it} f={f} g={g}", flush=True)

        for nhry, nhns, nvrx, nvns, nt, a in succs(hry, hns, vrx, vns, t):
            ng = g + 1
            nsk = mkey(nhry, nhns, nvrx, nvns, nt)
            if nsk in vis and vis[nsk] <= ng: continue
            if chkw(nhry, nhns, nvrx, nvns, nt):
                np_ = path + [a]
                print(f"\n*** SOLUTION ({len(np_)} actions): {' '.join(np_)} ***", flush=True)
                return np_
            h = heur(nhry, nhns, nvrx, nvns, nt)
            if ng + h < mx:
                heapq.heappush(pq, (ng + h, ng, (nhry, nhns, nvrx, nvns, nt), path + [a]))
    return None

if __name__ == "__main__":
    print("SK48 L6 A* Solver v4 (memory efficient, cross-rack blocking)", flush=True)
    print(f"Initial: H-rack y=26 n=2, V-rack x=29 n=2", flush=True)

    # First pass: find optimal depth without storing paths
    depth = solve()
    if depth:
        print(f"\nPass 2: reconstructing path at depth {depth}...", flush=True)
        path = solve_with_path(depth)
