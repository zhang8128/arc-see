"""From the state where reg1 (18, 6), red (18, 5), reg2 (22, 6):
  BFS for win. Everything upstream is manually confirmed working.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque
from dataclasses import replace
from l7_sim import load_init
from l7_search import moves
from l7_search_deep import at_chain9

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}


def state_after_plan():
    s = at_chain9()
    # chain 9
    s = s.do_chain('reg1', R)
    # Drive V-M with red to (12, 3)
    for a in [1, 3, 3, 1, 1, 4, 1, 1, 4, 4, 4]:
        s = s.do_action(A_DIR[a])
    # red to (14, 3)
    s = s.do_chain('red', R)
    # Drive V-M to (11, 6)
    for a in [3, 3, 3, 2, 2, 4, 4, 2]:
        s = s.do_action(A_DIR[a])
    # reg1 U to (11, 6)
    s = s.do_chain('reg1', U)
    # Drive V-M to (14, 2)
    for a in [1, 3, 3, 1, 1, 4, 4, 1, 1, 4, 4, 4, 2]:
        s = s.do_action(A_DIR[a])
    # Col 14 ladder
    s = s.do_chain('reg1', D)  # (14, 2) → (14, 4)
    s = s.do_chain('red', D)   # (14, 3) → (14, 5)
    s = s.do_chain('reg1', D)  # (14, 4) → (14, 6)
    # East bridges
    s = s.do_chain('reg1', R)  # (14, 6) → (16, 6)
    s = s.do_chain('reg1', R)  # (16, 6) → (18, 6)
    s = s.do_chain('red', R)   # (14, 5) → (16, 5)
    s = s.do_chain('red', R)   # (16, 5) → (18, 5)
    return s


def bfs_win(start, cap=10_000_000):
    frontier = deque([start])
    seen = {start.sig(): (None, None, 0)}
    md = 0
    t = time.time()
    while frontier and len(seen) < cap:
        s = frontier.popleft()
        d = seen[s.sig()][2]
        if d > md:
            md = d
            print(f'd={d} seen={len(seen):,} t={time.time()-t:.0f}s')
        if s.foz_count() < 3:
            path = []
            sig = s.sig()
            while seen[sig][0] is not None:
                prev, mv, _ = seen[sig]
                path.append(mv)
                sig = prev
            return s, list(reversed(path))
        for mv, ns in moves(s):
            if ns.sig() not in seen:
                seen[ns.sig()] = (s.sig(), mv, d + 1)
                frontier.append(ns)
    return None, None


if __name__ == '__main__':
    s = state_after_plan()
    print(f'Starting state: pieces={s.pieces}, vehicles={s.vehicle_pos}')
    print(f'  DGX: {sorted(s.dgx_pos)}')
    got, path = bfs_win(s)
    if got:
        print(f'WIN in {len(path)} additional moves!')
        for i, m in enumerate(path):
            print(f'  {i}: {m}')
    else:
        print('no win')
