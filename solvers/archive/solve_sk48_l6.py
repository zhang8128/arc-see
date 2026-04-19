#!/usr/bin/env python3
"""SK48 L6 Solver — Two-phase BFS.
Phase 1: Find states where v-rack has [8,8,8]
Phase 2: From those states, find states where h-rack also has [9,9,9]
"""
import sys, time
from collections import deque

CELL = 6
H_RX = 5
V_BY = 2
FXM, FXX = 11, 53
FYM, FYX = 8, 50
MAX_S = 12
OBS = frozenset([(29, 26)])

# Pre-compute ramp accessibility
def _ramp_check(pos, ramps, offset, size):
    return any(r <= pos + offset < r + size for r in ramps)

VRYS = (10, 16, 22, 28, 34, 40)
HRXS = (13, 19, 25, 31, 37, 43)
# h-rack y positions: 8, 14, 20, 26, 32, 38, 44 (from 8 step 6)
# v-rack x positions: 11, 17, 23, 29, 35, 41, 47 (from 11 step 6)
# But also consider y=2 for v-rack base which starts at 2
_HYS = list(range(2, 60, CELL))  # all possible y values
_VXS = list(range(5, 60, CELL))  # all possible x values
H_CAN_UP = frozenset(y for y in _HYS if _ramp_check(y, VRYS, -1, 8))
H_CAN_DN = frozenset(y for y in _HYS if _ramp_check(y, VRYS, 5, 8))
V_CAN_LT = frozenset(x for x in _VXS if _ramp_check(x, HRXS, -1, 8))
V_CAN_RT = frozenset(x for x in _VXS if _ramp_check(x, HRXS, 5, 8))

def inf(x, y): return FXM <= x and x + 6 <= FXX and FYM <= y and y + 6 <= FYX

def push_chain(tmap, x, y, dx, dy, moved):
    if (x, y) not in tmap: return True
    idx = tmap[(x, y)]
    if idx in moved: return True
    nx, ny = x + dx, y + dy
    if not inf(nx, ny) or (nx, ny) in OBS: return False
    if (nx, ny) in tmap and tmap[(nx, ny)] not in moved:
        if not push_chain(tmap, nx, ny, dx, dy, moved): return False
    moved[idx] = (nx, ny)
    return True

def do_move(t, tmap, sl, dx, dy, perp):
    moved = {}
    for sx, sy in sl:
        for cx, cy in ((sx, sy), (sx+dx, sy+dy)):
            if (cx, cy) in tmap and tmap[(cx, cy)] not in moved:
                if not push_chain(tmap, cx, cy, dx, dy, moved):
                    if perp: return None
    if not moved: return t
    r = list(t)
    for idx, (nx, ny) in moved.items():
        tc = t[idx][2]
        r[idx] = (nx, ny, tc)
    return tuple(r)

def make_tmap(t):
    return {(tx, ty): i for i, (tx, ty, tc) in enumerate(t)}

def chk_v(vrx, vns, t, tmap):
    vc = []
    for i in range(vns):
        k = (vrx, V_BY + CELL*i)
        if k in tmap: vc.append(t[tmap[k]][2])
    return len(vc) >= 3 and vc[0] == 8 and vc[1] == 8 and vc[2] == 8

def chk_h(hry, hns, t, tmap):
    hc = []
    for i in range(hns):
        k = (H_RX + CELL*i, hry)
        if k in tmap: hc.append(t[tmap[k]][2])
    return len(hc) >= 3 and hc[0] == 9 and hc[1] == 9 and hc[2] == 9

def chk_both(hry, hns, vrx, vns, t, tmap):
    return chk_h(hry, hns, t, tmap) and chk_v(vrx, vns, t, tmap)

def succs(hry, hns, vrx, vns, t, tmap):
    hsl = [(H_RX + i * CELL, hry) for i in range(hns)]
    vsl = [(vrx, V_BY + i * CELL) for i in range(vns)]
    out = []

    if hns < MAX_S:
        nx = H_RX + CELL * hns
        if (nx, hry) not in OBS and (inf(nx, hry) or not inf(H_RX+CELL*(hns-1), hry)):
            nt = do_move(t, tmap, hsl, CELL, 0, False)
            if nt is not None: out.append((hry, hns+1, vrx, vns, nt, 'HR'))

    if hns > 1:
        nt = do_move(t, tmap, hsl[1:], -CELL, 0, False)
        if nt is not None: out.append((hry, hns-1, vrx, vns, nt, 'HL'))

    if hry in H_CAN_UP and hry - CELL >= FYM:
        ny = hry - CELL
        if all((H_RX+i*CELL, ny) not in OBS and (inf(H_RX+i*CELL, ny) or not inf(H_RX+i*CELL, hry)) for i in range(hns)):
            nt = do_move(t, tmap, hsl, 0, -CELL, True)
            if nt is not None: out.append((ny, hns, vrx, vns, nt, 'HU'))

    if hry in H_CAN_DN and hry + CELL + 6 <= FYX:
        ny = hry + CELL
        if all((H_RX+i*CELL, ny) not in OBS and (inf(H_RX+i*CELL, ny) or not inf(H_RX+i*CELL, hry)) for i in range(hns)):
            nt = do_move(t, tmap, hsl, 0, CELL, True)
            if nt is not None: out.append((ny, hns, vrx, vns, nt, 'HD'))

    if vns < MAX_S:
        ny = V_BY + CELL * vns
        if (vrx, ny) not in OBS and (inf(vrx, ny) or not inf(vrx, V_BY+CELL*(vns-1))):
            nt = do_move(t, tmap, vsl, 0, CELL, False)
            if nt is not None: out.append((hry, hns, vrx, vns+1, nt, 'VD'))

    if vns > 1:
        nt = do_move(t, tmap, vsl[1:], 0, -CELL, False)
        if nt is not None: out.append((hry, hns, vrx, vns-1, nt, 'VU'))

    if vrx in V_CAN_LT and vrx - CELL >= FXM:
        nx = vrx - CELL
        if all((nx, V_BY+i*CELL) not in OBS and (inf(nx, V_BY+i*CELL) or not inf(vrx, V_BY+i*CELL)) for i in range(vns)):
            nt = do_move(t, tmap, vsl, -CELL, 0, True)
            if nt is not None: out.append((hry, hns, nx, vns, nt, 'VL'))

    if vrx in V_CAN_RT and vrx + CELL + 6 <= FXX:
        nx = vrx + CELL
        if all((nx, V_BY+i*CELL) not in OBS and (inf(nx, V_BY+i*CELL) or not inf(vrx, V_BY+i*CELL)) for i in range(vns)):
            nt = do_move(t, tmap, vsl, CELL, 0, True)
            if nt is not None: out.append((hry, hns, nx, vns, nt, 'VR'))

    return out


def make_key(hry, hns, vrx, vns, t):
    pos9 = frozenset((tx, ty) for tx, ty, tc in t if tc == 9)
    pos8 = frozenset((tx, ty) for tx, ty, tc in t if tc == 8)
    return (hry, hns, vrx, vns, pos9, pos8)


def solve():
    t0 = ((35,26,9), (41,26,9), (47,26,9), (29,32,8), (29,38,8), (29,44,8))
    s0 = (26, 2, 29, 2, t0)
    tmap0 = make_tmap(t0)

    print("Phase 1: BFS to find any state where BOTH racks match...")
    q = deque([(s0, [])])
    vis = {make_key(*s0)}
    mx = 50
    it = 0
    start = time.time()

    while q:
        (hry, hns, vrx, vns, t), path = q.popleft()
        if len(path) >= mx:
            continue
        it += 1
        if it % 200000 == 0:
            print(f"  i={it} d={len(path)} q={len(q)} v={len(vis)} t={time.time()-start:.1f}s")

        tmap = make_tmap(t)
        for nhry, nhns, nvrx, nvns, nt, a in succs(hry, hns, vrx, vns, t, tmap):
            sk = make_key(nhry, nhns, nvrx, nvns, nt)
            if sk in vis: continue
            vis.add(sk)
            np_ = path + [a]
            ntmap = make_tmap(nt)

            if chk_both(nhry, nhns, nvrx, nvns, nt, ntmap):
                elapsed = time.time() - start
                print(f"\n*** SOLUTION ({len(np_)} actions, {elapsed:.1f}s): {' '.join(np_)} ***")
                print(f"Iterations: {it}, States: {len(vis)}")
                return np_

            q.append(((nhry, nhns, nvrx, nvns, nt), np_))

    elapsed = time.time() - start
    print(f"No solution (mx={mx}, it={it}, vis={len(vis)}, {elapsed:.1f}s)")
    return None


if __name__ == "__main__":
    print("SK48 L6 Solver (optimized BFS)")
    path = solve()
    if path:
        # Verify with engine
        sys.path.insert(0, 'environment_files/sk48/41055498')
        from sk48 import Sk48
        from arcengine import GameAction
        from arcengine.enums import ActionInput

        g = Sk48()
        g._current_level_index = 5
        g.on_set_level(g._levels[5])

        am = {'U': GameAction.ACTION1, 'D': GameAction.ACTION2, 'L': GameAction.ACTION3, 'R': GameAction.ACTION4}
        cur = 'H'
        acts = []

        for m in path:
            rk, d = m[0], m[1]
            if rk != cur:
                for r in g.xpmcmtbcv.keys():
                    if r != g.vzvypfsnt:
                        ai = ActionInput(id=GameAction.ACTION6, data={'x': r.x+2, 'y': r.y+2})
                        g.perform_action(ai)
                        for _ in range(200):
                            if g.is_action_complete: break
                            g.step()
                        acts.append('SWITCH')
                        break
                cur = rk
            ai = ActionInput(id=am[d])
            g.perform_action(ai)
            for _ in range(200):
                if g.is_action_complete: break
                g.step()
            acts.append(am[d].name)

        win = g.gvtmoopqgy()
        print(f"\nEngine verify: {'WIN' if win else 'FAIL'}")
        print(f"Actions: {acts}")
        print(f"Count: {len(acts)}, Budget remaining: {g.qiercdohl}")
