"""Beam search: at each depth keep only top-K states by heuristic.

Doesn't guarantee optimal but explores deeper than BFS for same memory.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time

from l7_sim import load_init, Sim
from l7_search import moves
from l7_search_deep import at_chain9

GOAL = (22, 5)


def heuristic(s):
    """Lower is closer to win. Priorities:
    1. foz_count<3 (win): 0
    2. reg piece at (22, 5): 1
    3. any reg close to (22, 5): chebyshev/2
    4. plus penalty for pieces far from (22, 5)
    """
    if s.foz_count() < 3:
        return 0
    regs = [p for pid, p in s.piece_pos if 'reg' in pid]
    if any(p == (22, 5) for p in regs):
        return 1
    # Both regs' avg distance; prefer one very close
    dists = [max(abs(p[0]-GOAL[0]), abs(p[1]-GOAL[1])) for p in regs]
    return 2 + min(dists)  # weight on closeness of best piece


def beam_search(start, K=5000, max_depth=200):
    frontier = [start]
    seen = {start.sig()}
    best_h = heuristic(start)
    best_state = start
    best_path = []
    paths = {start.sig(): []}
    t = time.time()
    for depth in range(max_depth):
        new_frontier = []
        new_paths = {}
        for s in frontier:
            for mv, ns in moves(s):
                if ns.sig() in seen:
                    continue
                seen.add(ns.sig())
                new_frontier.append(ns)
                new_paths[ns.sig()] = paths[s.sig()] + [mv]
                if ns.foz_count() < 3:
                    return ns, new_paths[ns.sig()]
        # Keep top-K by heuristic
        new_frontier.sort(key=heuristic)
        new_frontier = new_frontier[:K]
        paths = {s.sig(): new_paths[s.sig()] for s in new_frontier}
        frontier = new_frontier
        if frontier:
            best_in_beam = frontier[0]
            h = heuristic(best_in_beam)
            if h < best_h:
                best_h = h
                best_state = best_in_beam
                best_path = paths[best_in_beam.sig()]
                print(f'  depth {depth} best h={h} pieces={best_in_beam.pieces}')
        if depth % 10 == 0:
            h0 = heuristic(frontier[0]) if frontier else -1
            print(f'  depth {depth}: |beam|={len(frontier)}, best_h={h0}, seen={len(seen):,}, t={time.time()-t:.0f}s')
        if not frontier:
            break
    return best_state, best_path


if __name__ == '__main__':
    s = at_chain9()
    print(f'Start h={heuristic(s)}')
    end, path = beam_search(s, K=10000, max_depth=150)
    if end.foz_count() < 3:
        print(f'WIN in {len(path)} moves')
        for m in path:
            print(f'  {m}')
    else:
        print(f'Best state: pieces={end.pieces}, h={heuristic(end)}')
        print(f'Path len: {len(path)}')
