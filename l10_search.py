"""BFS from L10 init for reg+reg consumption."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque
from l7_sim import load_init
from l7_search import moves


def goal(s):
    # L10 win: ddaguepwkt == 1. total_foz - 10 blues = 1, so total = 11.
    # Start with 12 pieces. One consumption → 11.
    return len(s.piece_pos) < 12


def bfs(cap=50_000_000):
    s0 = load_init('/tmp/l10_init.json')
    frontier = deque([s0])
    seen = {s0.sig(): (None, None, 0)}
    md = 0
    t = time.time()
    while frontier and len(seen) < cap:
        s = frontier.popleft()
        d = seen[s.sig()][2]
        if d > md:
            md = d
            if md % 2 == 0:
                print(f'd={d} seen={len(seen):,} t={time.time()-t:.0f}s')
        if goal(s):
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
    s0 = load_init('/tmp/l10_init.json')
    print(f'init pieces: {s0.pieces}')
    print(f'vehicles: {s0.vehicle_pos}')
    got, path = bfs()
    if got:
        print(f'Goal in {len(path)} moves, final: {got.pieces}')
    else:
        print('no goal')
