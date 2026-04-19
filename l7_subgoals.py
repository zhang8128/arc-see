"""Focused sub-goal searches to identify structural reachability."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque

from l7_sim import load_init
from l7_search import moves


def bfs(goal_fn, max_states=5_000_000, verbose=False):
    s0 = load_init()
    frontier = deque([s0])
    seen = {s0.sig(): (None, None, 0)}
    max_depth = 0
    tstart = time.time()
    while frontier:
        s = frontier.popleft()
        d = seen[s.sig()][2]
        if d > max_depth:
            max_depth = d
            if verbose:
                print(f'  depth {d}, {len(seen)} states, {time.time()-tstart:.0f}s')
        if goal_fn(s):
            return s, reconstruct(s, seen)
        if len(seen) > max_states:
            return None, []
        for mv, ns in moves(s):
            if ns.sig() not in seen:
                seen[ns.sig()] = (s.sig(), mv, d + 1)
                frontier.append(ns)
    return None, []


def reconstruct(end, seen):
    path = []
    sig = end.sig()
    while seen[sig][0] is not None:
        prev, mv, _ = seen[sig]
        path.append(mv)
        sig = prev
    return list(reversed(path))


def goal_dgx_at(pos):
    return lambda s: pos in s.dgx_pos


def goal_piece_at(pid, pos):
    return lambda s: s.pieces.get(pid) == pos


def goal_any_piece_at(pos):
    return lambda s: any(p == pos for _, p in s.piece_pos)


if __name__ == '__main__':
    cases = [
        ('DGX at (22,4)', goal_dgx_at((22, 4))),
        ('DGX at (22,3)', goal_dgx_at((22, 3))),
        ('DGX at (21,2)', goal_dgx_at((21, 2))),
        ('any piece at (22,3)', goal_any_piece_at((22, 3))),
        ('any piece at (22,5)', goal_any_piece_at((22, 5))),
        ('any piece at (22,4)', goal_any_piece_at((22, 4))),
        ('any piece at (17,2)', goal_any_piece_at((17, 2))),
    ]
    for label, gf in cases:
        t0 = time.time()
        got, path = bfs(gf, max_states=500_000)
        if got:
            print(f'{label}: REACHED in {len(path)} moves ({time.time()-t0:.0f}s)')
        else:
            print(f'{label}: UNREACHED ({time.time()-t0:.0f}s)')
