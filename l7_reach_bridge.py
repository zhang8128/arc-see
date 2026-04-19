"""Search from chain-9 for state reg1@(14,2) + red@(14,3) or variants that
enable the bridge plan."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque

from l7_sim import load_init, Sim
from l7_search import moves
from l7_search_deep import at_chain9


def bfs_target(start, goal_fn, cap, label=''):
    frontier = deque([start])
    seen = {start.sig(): (None, None, 0)}
    t = time.time()
    md = 0
    while frontier and len(seen) < cap:
        s = frontier.popleft()
        d = seen[s.sig()][2]
        if d > md:
            md = d
            if md % 2 == 0:
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


if __name__ == '__main__':
    s0 = at_chain9()
    print(f'chain-9 start: pieces={s0.pieces}, vehicles={s0.vehicle_pos}')

    # Goal: reg1 and red both at col >= 13
    def goal_both_col13(s):
        pieces = dict(s.piece_pos)
        if 'reg1' not in pieces or 'red' not in pieces:
            return False
        return pieces['reg1'][0] >= 13 and pieces['red'][0] >= 13

    # Goal: reg1 at (14, 2) co-located with vehicle (loaded)
    def goal_reg1_14_2(s):
        pieces = dict(s.piece_pos)
        return pieces.get('reg1') == (14, 2) and (14, 2) in s.vehicle_pos

    # Goal: red at (14, 3)
    def goal_red_14_3(s):
        return dict(s.piece_pos).get('red') == (14, 3)

    def goal_bridge_seed(s):
        pieces = dict(s.piece_pos)
        if pieces.get('red') != (14, 3):
            return False
        if pieces.get('reg1') != (14, 2):
            return False
        return (14, 2) in s.vehicle_pos

    def goal_weak_seed(s):
        """red at (14,3) + reg1 anywhere col >= 11"""
        pieces = dict(s.piece_pos)
        return pieces.get('red') == (14, 3) and pieces.get('reg1', (0, 0))[0] >= 11

    print()
    print('=== Seed: reg1@(14,2) loaded + red@(14,3) ===')
    end, path = bfs_target(s0, goal_bridge_seed, cap=10_000_000, label='seed')
    if end:
        print(f'REACHED in {len(path)} moves:')
        for i, m in enumerate(path):
            print(f'  {i}: {m}')
        print(f'pieces={end.pieces}, vehicles={end.vehicle_pos}')
    else:
        print('no. Trying weaker seed.')
        end, path = bfs_target(s0, goal_weak_seed, cap=10_000_000, label='weak')
        if end:
            print(f'WEAK SEED REACHED in {len(path)}: pieces={end.pieces}, vehicles={end.vehicle_pos}')
        else:
            print('still no')
