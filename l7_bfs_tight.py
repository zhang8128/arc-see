"""Tighter BFS: encode state as bytes for ~60% memory savings. Target 30M+ states."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time, struct
from collections import deque

from l7_sim import load_init, Sim
from l7_search import moves


def encode(s):
    """Pack state into bytes. Each (x,y) pair is 2 bytes (x, y)."""
    parts = []
    # Pieces: sort by id, pack (x, y) each
    for pid, p in s.piece_pos:
        parts.append(bytes([p[0], p[1]]))
    # Vehicles: already sorted
    for v in s.vehicle_pos:
        parts.append(bytes([v[0], v[1]]))
    # DGX
    for d in s.dgx_pos:
        parts.append(bytes([d[0], d[1]]))
    return b''.join(parts)


def bfs(cap):
    s0 = load_init()
    frontier = deque([s0])
    seen = {encode(s0)}
    md = 0
    t = time.time()
    win = None
    last_print = 0
    while frontier:
        s = frontier.popleft()
        if s.foz_count() < 3:
            print(f'WIN state: {s.pieces}')
            win = s
            break
        if len(seen) > cap:
            print(f'cap hit')
            break
        for mv, ns in moves(s):
            e = encode(ns)
            if e not in seen:
                seen.add(e)
                frontier.append(ns)
        if len(seen) - last_print > 500000:
            last_print = len(seen)
            print(f'seen={len(seen):,}, frontier={len(frontier):,}, t={time.time()-t:.0f}s')
    return win


if __name__ == '__main__':
    win = bfs(cap=40_000_000)
    if win:
        print('FOUND WIN')
    else:
        print('no win')
