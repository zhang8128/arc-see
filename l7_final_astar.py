"""A* from post-bridge state toward reg1 reaching (22, 5) and win."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time, heapq
from l7_sim import load_init
from l7_search import moves
from l7_final import state_after_plan

GOAL = (22, 5)


def heuristic(s):
    if s.foz_count() < 3:
        return 0
    # Distance from reg1 to (22, 5)
    r1 = s.pieces.get('reg1')
    if r1 == (22, 5):
        # Need V at (22, 4) no DGX
        if (22, 4) in s.vehicle_pos and (22, 4) not in s.dgx_pos:
            return 1
        return 3
    # Distance
    dx = abs(r1[0] - GOAL[0])
    dy = abs(r1[1] - GOAL[1])
    return 4 + max(dx, dy)


def astar(start, cap=5_000_000):
    pq = [(heuristic(start), 0, 0, start)]
    counter = 1
    best_g = {start.sig(): 0}
    best_h = heuristic(start)
    t = time.time()
    n_exp = 0
    while pq:
        f, g, _, s = heapq.heappop(pq)
        if len(best_g) > cap:
            print('cap')
            break
        if s.foz_count() < 3:
            return s, g
        n_exp += 1
        h = heuristic(s)
        if h < best_h:
            best_h = h
            print(f'new best h={best_h} at g={g}. pieces={s.pieces}, vehicles={s.vehicle_pos}, DGX-on-V={sorted(set(s.dgx_pos)&set(s.vehicle_pos))}')
        if n_exp % 100000 == 0:
            print(f'exp={n_exp:,} seen={len(best_g):,} f={f} g={g} best_h={best_h} t={time.time()-t:.0f}s')
        for mv, ns in moves(s):
            ng = g + 1
            nsig = ns.sig()
            if nsig not in best_g or ng < best_g[nsig]:
                best_g[nsig] = ng
                heapq.heappush(pq, (ng + heuristic(ns), ng, counter, ns))
                counter += 1
    return None, -1


if __name__ == '__main__':
    s = state_after_plan()
    print(f'start h={heuristic(s)} pieces={s.pieces}')
    result, depth = astar(s, cap=10_000_000)
    if result:
        print(f'WIN at g={depth}! pieces={result.pieces}')
    else:
        print('no win')
