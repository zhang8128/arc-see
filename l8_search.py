"""BFS from L8 init for reg+reg consumption (foz drops from 6 to 5)."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque
from l7_sim import load_init
from l7_search import moves


def goal(s):
    # L8 win: total foz drops by 1 (consumption). Count pieces.
    return len(s.piece_pos) < 6


def bfs(cap=5_000_000):
    s0 = load_init('/tmp/l8_init.json')
    frontier = deque([s0])
    seen = {s0.sig(): (None, None, 0)}
    md = 0
    t = time.time()
    while frontier and len(seen) < cap:
        s = frontier.popleft()
        d = seen[s.sig()][2]
        if d > md:
            md = d
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
    s0 = load_init('/tmp/l8_init.json')
    print(f'init pieces: {s0.pieces}')
    got, path = bfs()
    if got:
        print(f'WIN in {len(path)} moves, final pieces={got.pieces}')
        for i, m in enumerate(path):
            print(f'  {i}: {m}')
    else:
        print('no win')
