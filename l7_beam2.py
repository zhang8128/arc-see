"""Beam search v2 — smarter heuristic targeting the win setup.

Win requires reg1 (or any mobile reg) at (22, 5) with reg2 at (22, 6)
AND (22, 4) having a vehicle without DGX for the consumption chain.

Heuristic (lower = closer to win):
  win state:  0
  reg1@(22,5) with reg2@(22,6):  1 + distance-of-(22,4)-being-ready
  else: 10 + chebyshev((reg1, (22,5)))/2 + penalty

"Mobile reg" = reg with position != (22, 6). In init there are 2 regs;
after chain-9 reg1 is at (9,8) (mobile), reg2 at (22,6) (orphan).
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time

from l7_sim import load_init, Sim
from l7_search import moves
from l7_search_deep import at_chain9

GOAL = (22, 5)


def heuristic(s):
    if s.foz_count() < 3:
        return 0
    pieces = dict(s.piece_pos)
    # Find "mobile reg" — any reg not at (22, 6)
    mobile_reg_pos = None
    for pid, p in s.piece_pos:
        if 'reg' in pid and p != (22, 6):
            mobile_reg_pos = p
            break
    if mobile_reg_pos is None:
        return 100  # unlikely state
    # reg2 at (22, 6) required
    if (22, 6) not in [p for pid, p in s.piece_pos if 'reg' in pid]:
        return 50  # bad state
    # Check if mobile reg at (22, 5)
    if mobile_reg_pos == (22, 5):
        # Check (22, 4) readiness: has vehicle, no DGX
        if (22, 4) in s.vehicle_pos and (22, 4) not in s.dgx_pos:
            return 1  # ready for win chain
        return 2  # reg1 at (22,5) but (22,4) not ready
    # Mobile reg elsewhere — distance to (22, 5)
    cheby = max(abs(mobile_reg_pos[0] - GOAL[0]), abs(mobile_reg_pos[1] - GOAL[1]))
    # Also penalize if mobile reg at x < 5 (far)
    return 3 + cheby


def beam_search(start, K, max_depth):
    frontier = [start]
    paths = {start.sig(): []}
    seen = {start.sig()}
    best_h = heuristic(start)
    best_s = start
    best_p = []
    t = time.time()
    for depth in range(max_depth):
        cand = []
        for s in frontier:
            for mv, ns in moves(s):
                if ns.sig() in seen:
                    continue
                seen.add(ns.sig())
                cand.append((ns, paths[s.sig()] + [mv]))
                if ns.foz_count() < 3:
                    return ns, paths[s.sig()] + [mv]
        cand.sort(key=lambda x: heuristic(x[0]))
        cand = cand[:K]
        if not cand:
            break
        frontier = [c[0] for c in cand]
        paths = {s.sig(): p for s, p in cand}
        top_h = heuristic(frontier[0])
        if top_h < best_h:
            best_h = top_h
            best_s = frontier[0]
            best_p = paths[frontier[0].sig()]
            print(f'depth {depth} new best h={best_h} pieces={best_s.pieces} path_len={len(best_p)}')
        if depth % 5 == 0:
            print(f'depth {depth}: |beam|={len(frontier)}, h={top_h}, seen={len(seen):,}, t={time.time()-t:.0f}s')
    return best_s, best_p


if __name__ == '__main__':
    s = at_chain9()
    print(f'Start h={heuristic(s)} pieces={s.pieces}')
    end, path = beam_search(s, K=20000, max_depth=200)
    if end.foz_count() < 3:
        print(f'WIN in {len(path)} moves!')
        for m in path:
            print(f'  {m}')
    else:
        print(f'Best: h={heuristic(end)}, pieces={end.pieces}, path len={len(path)}')
