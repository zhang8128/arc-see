"""BFS starting from verified chain-9 state. If a win exists within the
remaining branches, finding from this late point is much smaller.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque
from dataclasses import replace

from l7_sim import load_init, Sim
from l7_search import moves

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}


def at_chain9():
    """Return sim state matching engine after chain 9."""
    VERIFIED = [
        ('A', [3, 3, 1, 1, 3, 3, 3]),
        ('C', 'reg1', D),
        ('A', [4, 4, 4, 2, 2, 3, 3, 2]),
        ('C', 'reg1', D),
        ('A', [1, 4, 4, 1, 1, 4, 4, 4]),
        ('C', 'red', D),
        ('A', [3, 3, 3, 2, 2, 4, 4, 4, 2]),
        ('C', 'red', D),
        ('A', [1, 3, 3, 3, 1, 1, 3, 3, 3, 4, 4, 4, 2, 2, 3, 3, 3, 2]),
        ('C', 'reg1', R),
        ('C', 'reg1', R),
        ('C', 'reg1', R),
        ('C', 'red', R),
        ('C', 'reg1', R),
        ('A', [2, 3, 2, 2, 4, 4, 2]),
        ('C', 'red', R),
    ]
    s = load_init()
    for kind, *args in VERIFIED:
        if kind == 'A':
            for a in args[0]:
                s = s.do_action(A_DIR[a])
        else:
            pid, d = args
            s = s.do_chain(pid, d)
    return s


def bfs(start: Sim, goal_fn, max_states=5_000_000, verbose=True):
    frontier = deque([start])
    seen = {start.sig(): (None, None, 0)}
    tstart = time.time()
    max_depth_seen = 0
    while frontier:
        s = frontier.popleft()
        d = seen[s.sig()][2]
        if d > max_depth_seen:
            max_depth_seen = d
            if verbose:
                print(f'depth {d} seen; {len(seen)} states; {time.time()-tstart:.1f}s')
        if goal_fn(s):
            return s, reconstruct(s, seen)
        if len(seen) > max_states:
            print(f'cap hit {max_states}')
            break
        for mv, ns in moves(s):
            if ns.sig() not in seen:
                seen[ns.sig()] = (s.sig(), mv, d + 1)
                frontier.append(ns)
    print(f'Exhausted. Final depth: {max_depth_seen}, {len(seen)} states')
    return None, []


def reconstruct(end, seen):
    mv_list = []
    sig = end.sig()
    while seen[sig][0] is not None:
        prev, mv, _ = seen[sig]
        mv_list.append(mv)
        sig = prev
    return list(reversed(mv_list))


if __name__ == '__main__':
    s = at_chain9()
    print('At chain9:')
    print(f'  pieces={s.pieces}')
    print(f'  vehicles={s.vehicle_pos}')
    print(f'  DGX cells: {len(s.dgx_pos)}')
    print()
    print('=== Goal 1: reg piece at (22,5) (consumption-adjacent) ===')
    got, path = bfs(s, lambda st: any(p == (22, 5) for pid, p in st.piece_pos if 'red' not in pid))
    if got:
        print(f'FOUND in {len(path)} moves from chain9')
        for m in path:
            print(f'  {m}')
    print()
    print('=== Goal 2: foz_count < 3 (WIN) ===')
    got, path = bfs(s, lambda st: st.foz_count() < 3)
    if got:
        print(f'WIN in {len(path)} moves from chain9')
        for m in path:
            print(f'  {m}')
