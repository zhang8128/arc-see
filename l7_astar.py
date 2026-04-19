"""Heuristic search: prioritize states where a regular piece is closer
to (22, 5).

Heuristic: min chebyshev distance from any reg piece to (22, 5).
(We pick reg because consumption only works with reg-as-pivot/source.)

A* ordering: f = g + h, g = depth, h = admissible underestimate.
Since each chain moves exactly 2 cells, h_cells = ceil(chebyshev/2).
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
import heapq
from collections import defaultdict

from l7_sim import load_init, Sim
from l7_search import moves
from l7_search_deep import at_chain9

GOAL = (22, 5)


def heuristic(s):
    regs = [p for pid, p in s.piece_pos if 'reg' in pid]
    if not regs:
        return 0
    # Min cells to (22,5) from any reg, div 2 (chains move 2 cells)
    dists = [max(abs(p[0]-GOAL[0]), abs(p[1]-GOAL[1])) for p in regs]
    return (min(dists) + 1) // 2


def astar(start, goal_fn, cap):
    pq = [(heuristic(start), 0, 0, start)]
    counter = 1
    best_g = {start.sig(): 0}
    best_h = heuristic(start)
    t = time.time()
    explored = 0
    while pq:
        f, g, _, s = heapq.heappop(pq)
        if len(best_g) > cap:
            print(f'  cap {cap}')
            break
        if goal_fn(s):
            return s, g
        explored += 1
        if explored % 100000 == 0:
            h = heuristic(s)
            print(f'  explored={explored:,} seen={len(best_g):,} f={f} g={g} h={h} best_h={best_h} t={time.time()-t:.0f}s')
        h_now = heuristic(s)
        if h_now < best_h:
            best_h = h_now
            regs = [(pid, p) for pid, p in s.piece_pos if 'reg' in pid]
            closest = min(regs, key=lambda x: max(abs(x[1][0]-GOAL[0]), abs(x[1][1]-GOAL[1])))
            print(f'  new best h={best_h} g={g} closest reg={closest} pieces={s.pieces}')
            print(f'    vehicles={s.vehicle_pos}')
        for mv, ns in moves(s):
            ng = g + 1
            nsig = ns.sig()
            if nsig not in best_g or ng < best_g[nsig]:
                best_g[nsig] = ng
                nh = heuristic(ns)
                heapq.heappush(pq, (ng + nh, ng, counter, ns))
                counter += 1
    return None, -1


if __name__ == '__main__':
    s = at_chain9()
    print(f'Start heuristic: {heuristic(s)}')
    print(f'Pieces: {s.pieces}')
    result, depth = astar(s, lambda st: st.foz_count() < 3, cap=10_000_000)
    if result:
        print(f'WIN at g={depth}. pieces={result.pieces}')
    else:
        print('no win found')
