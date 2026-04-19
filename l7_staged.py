"""Staged BFS: small sub-goals instead of end-to-end.
Stage A: from chain-9, reach any piece at (14, 5) or (14, 6)
       → enables chain R through DGX(15,5) or DGX(15,6) to (16, *).
Stage B: from there, reach (18, 5) or (18, 6) via next DGX.
Stage C: continue toward col 22 / consume reg2.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque

from l7_sim import load_init, Sim
from l7_search import moves
from l7_search_deep import at_chain9

DIR_NAMES = {(0,-1):'U',(0,1):'D',(-1,0):'L',(1,0):'R'}


def bfs_from(start, goal_fn, max_states, label=''):
    frontier = deque([start])
    seen = {start.sig(): (None, None, 0)}
    max_d = 0
    t = time.time()
    while frontier and len(seen) < max_states:
        s = frontier.popleft()
        d = seen[s.sig()][2]
        if d > max_d:
            max_d = d
            print(f'  [{label}] d={d} states={len(seen):,} t={time.time()-t:.0f}s')
        if goal_fn(s):
            path = []
            sig = s.sig()
            while seen[sig][0] is not None:
                prev, mv, _ = seen[sig]
                path.append(mv)
                sig = prev
            return s, list(reversed(path))
        for mv, ns in moves(s):
            if ns.sig() not in seen:
                seen[ns.sig()] = (s.sig(), mv, d+1)
                frontier.append(ns)
    return None, None


def goal_piece_at(pos):
    def check(s):
        return any(p == pos for _, p in s.piece_pos)
    return check


def goal_piece_at_any(positions):
    pset = set(positions)
    def check(s):
        return any(p in pset for _, p in s.piece_pos)
    return check


if __name__ == '__main__':
    s = at_chain9()
    print('Chain 9 start:')
    print(f'  pieces={s.pieces}')
    print(f'  DGX: {s.dgx_pos}')
    print(f'  vehicles: {s.vehicle_pos}')
    print()

    # Stage A1: reach (14, 5)
    print('=== Stage A1: piece at (14, 5) ===')
    end, path = bfs_from(s, goal_piece_at((14, 5)), max_states=3_000_000, label='A1')
    if end:
        print(f'REACHED in {len(path)} moves. pieces={end.pieces}')
        stage_a_end = end
    else:
        print('not reached')

    print()
    print('=== Stage A2: piece at (14, 6) ===')
    end, path = bfs_from(s, goal_piece_at((14, 6)), max_states=3_000_000, label='A2')
    if end:
        print(f'REACHED in {len(path)} moves. pieces={end.pieces}')
    else:
        print('not reached')

    print()
    print('=== Stage A3: piece at any of {(14,5),(14,6),(16,5),(16,6),(18,5),(18,6)} ===')
    end, path = bfs_from(s, goal_piece_at_any([(14,5),(14,6),(16,5),(16,6),(18,5),(18,6)]), max_states=5_000_000, label='A3')
    if end:
        print(f'REACHED in {len(path)} moves. pieces={end.pieces}')
    else:
        print('not reached')
