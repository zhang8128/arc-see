"""BFS from chain-9 for the pre-win state:
  reg1 at (22, 5), reg2 at (22, 6), vehicle at (22, 4) without DGX.
From this state, chain reg2 UP via reg1 pivot consumes reg1. WIN.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque

from l7_sim import load_init, Sim
from l7_search import moves
from l7_search_deep import at_chain9

DN = {(0,-1):'U',(0,1):'D',(-1,0):'L',(1,0):'R'}


def pre_win(s):
    pieces = dict(s.piece_pos)
    if pieces.get('reg1') != (22, 5):
        return False
    if pieces.get('reg2') != (22, 6):
        return False
    veh_set = set(s.vehicle_pos)
    if (22, 4) not in veh_set:
        return False
    if (22, 4) in s.dgx_pos:
        return False
    # And the reg2 chain UP must pass: target (22,4) valid, pivot (22,5)=reg1 valid
    # target (22, 4) has track + vehicle = len 2 with hup2 → valid. Good.
    return True


def bfs(start, goal_fn, cap, label):
    frontier = deque([start])
    seen = {start.sig(): (None, None, 0)}
    md = 0
    t = time.time()
    while frontier and len(seen) < cap:
        s = frontier.popleft()
        d = seen[s.sig()][2]
        if d > md:
            md = d
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


# Weaker goals — incremental progress
def reg1_at_22_5(s):
    return dict(s.piece_pos).get('reg1') == (22, 5)

def any_piece_at_22_5(s):
    return any(p == (22, 5) for _, p in s.piece_pos)


if __name__ == '__main__':
    s = at_chain9()
    print('From chain-9:')
    print(f'  pieces={s.pieces}')

    print()
    print('=== Any piece at (22, 5) ===')
    got, path = bfs(s, any_piece_at_22_5, cap=15_000_000, label='any_22_5')
    if got:
        print(f'REACHED in {len(path)} moves')
        print(f'  final state: {got.pieces}')
        for m in path[:30]:
            print(f'    {m}')
    else:
        print('unreached')
