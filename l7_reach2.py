"""Enumerate all positions any piece can reach via full BFS."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque, defaultdict

from l7_sim import load_init
from l7_search import moves


def all_reachable(max_states=2_000_000):
    s0 = load_init()
    frontier = deque([s0])
    seen = {s0.sig()}
    piece_cells = defaultdict(set)
    start = time.time()
    while frontier:
        s = frontier.popleft()
        for pid, p in s.piece_pos:
            piece_cells[pid].add(p)
        if len(seen) >= max_states:
            break
        for mv, ns in moves(s):
            if ns.sig() not in seen:
                seen.add(ns.sig())
                frontier.append(ns)
    elapsed = time.time() - start
    return piece_cells, len(seen), elapsed


if __name__ == '__main__':
    piece_cells, n, el = all_reachable(max_states=3_000_000)
    print(f'Explored {n} states in {el:.1f}s')
    for pid in ('reg1', 'reg2', 'red'):
        cells = sorted(piece_cells.get(pid, set()))
        print(f'{pid}: {len(cells)} cells')
        for p in cells:
            print(f'  {p}')
