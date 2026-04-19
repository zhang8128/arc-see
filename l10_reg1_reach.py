"""Targeted BFS: can reg1 reach any cell at row >= 5?"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque
from l7_sim import load_init
from l7_search import moves


def goal(s):
    r1 = s.pieces.get('reg1')
    return r1 is not None and r1[1] >= 5


def bfs(cap=5_000_000):
    s0 = load_init('/tmp/l10_init.json')
    frontier = deque([s0])
    seen = {s0.sig(): (None, None)}
    depth = {s0.sig(): 0}
    md = 0
    t = time.time()
    while frontier and len(seen) < cap:
        s = frontier.popleft()
        d = depth[s.sig()]
        if d > md:
            md = d
            print(f'd={d} seen={len(seen):,} t={time.time()-t:.0f}s')
        if goal(s):
            path = []
            sig = s.sig()
            while seen[sig][0] is not None:
                prev, mv = seen[sig]
                path.append(mv)
                sig = prev
            return s, list(reversed(path))
        for mv, ns in moves(s):
            if ns.sig() not in seen:
                seen[ns.sig()] = (s.sig(), mv)
                depth[ns.sig()] = d + 1
                frontier.append(ns)
    return None, None


if __name__ == '__main__':
    got, path = bfs()
    if got:
        print(f'reg1 at {got.pieces["reg1"]} in {len(path)} moves')
        print(f'pieces: {got.pieces}')
    else:
        print('reg1 cannot reach row >= 5 in 5M states')
