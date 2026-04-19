"""Reachability BFS: can any reg piece land at col-22 cells?

If NO piece can reach (22,5), (22,4), or (22,6)→different_pos, the structural
blocker claim is proven and L7 is unsolvable by chains.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque

from l7_sim import load_init, Sim, DIRS
from l7_search import moves


def bfs_reach(goal_fn, max_states=5_000_000, verbose=True):
    s0 = load_init()
    frontier = deque([s0])
    seen = {s0.sig(): 0}
    start = time.time()
    max_depth_seen = 0
    best = None
    while frontier:
        s = frontier.popleft()
        d = seen[s.sig()]
        if goal_fn(s):
            return s, d, seen
        if d > max_depth_seen:
            max_depth_seen = d
            if verbose:
                print(f'depth {d} seen; {len(seen)} states; {time.time()-start:.1f}s')
        if len(seen) > max_states:
            print(f'cap hit at {max_states}')
            break
        for mv, ns in moves(s):
            if ns.sig() not in seen:
                seen[ns.sig()] = d + 1
                frontier.append(ns)
    return None, max_depth_seen, seen


if __name__ == '__main__':
    print('=== Goal: any piece at (22,5) ===')
    s, d, seen = bfs_reach(
        lambda s: any(p == (22, 5) for _, p in s.piece_pos),
        max_states=5_000_000
    )
    if s:
        print(f'REACHED at depth {d}: pieces={s.pieces}')
    else:
        print(f'UNREACHED within {len(seen)} states, max depth {d}')

    print()
    print('=== Goal: reg2 moves off (22,6) ===')
    s, d, seen = bfs_reach(
        lambda s: any(pid.startswith('reg') and s.pieces.get(pid) != (22,6) and s.pieces.get(pid) != (0,1) for pid in s.pieces) and (s.pieces.get('reg2', None) != (22,6)),
        max_states=2_000_000
    )
    if s:
        print(f'REACHED at depth {d}: pieces={s.pieces}')
    else:
        print(f'UNREACHED within {len(seen)} states')
