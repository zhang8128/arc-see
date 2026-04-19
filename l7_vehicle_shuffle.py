"""From h=3 state, BFS just A-actions to find config where V at (22, 4) without DGX.
Pieces stay fixed (all on hup cells). Only vehicles/DGXs move."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque
from dataclasses import replace
from l7_sim import load_init, Sim
from l7_final_astar import heuristic

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}
DN = {U:'U',D:'D',L:'L',R:'R'}


def setup():
    """Replay to h=3 state via my plan + A* result path."""
    # Actually the h=3 state had reg1 @ (22, 5). Let me re-derive that state from sim.
    # I'll execute the PLAN + needed moves from A*.
    # From A* output at h=3:
    # pieces=reg1 (22, 5), red (18, 5), reg2 (22, 6)
    # vehicles=((6, 6), (14, 2), (20, 0), (21, 1), (22, 3), (22, 4))
    # DGX-on-V=[(20, 0), (21, 1), (22, 4)]
    # Synthesize this state directly.
    s = load_init()
    # Replace pieces and vehicles
    pieces = tuple(sorted([
        ('reg1', (22, 5)),
        ('reg2', (22, 6)),
        ('red', (18, 5)),
    ]))
    vehicles = tuple(sorted([(6, 6), (14, 2), (20, 0), (21, 1), (22, 3), (22, 4)]))
    # DGX: static DGXs (hup cells) + mobile at (20, 0), (21, 1), (22, 4)
    static_dgx = {(0, 2), (6, 2), (13, 3), (15, 5), (15, 6), (17, 5), (17, 6), (1, 7), (6, 7), (11, 7), (2, 8), (4, 8)}
    dgx = tuple(sorted(static_dgx | {(20, 0), (21, 1), (22, 4)}))
    s2 = replace(s, piece_pos=pieces, vehicle_pos=vehicles, dgx_pos=dgx)
    return s2


def goal_achieved(s):
    # (22, 4) has V no DGX
    if (22, 4) in s.vehicle_pos and (22, 4) not in s.dgx_pos:
        return True
    return False


def shuffle_bfs(s, cap=2_000_000):
    frontier = deque([s])
    seen = {(s.vehicle_pos, s.dgx_pos)}
    parent = {(s.vehicle_pos, s.dgx_pos): (None, None)}
    t = time.time()
    n = 0
    while frontier and len(seen) < cap:
        st = frontier.popleft()
        n += 1
        if n % 100000 == 0:
            print(f'{n}/{len(seen):,} t={time.time()-t:.0f}s')
        if goal_achieved(st):
            # Reconstruct path
            path = []
            key = (st.vehicle_pos, st.dgx_pos)
            while parent[key][0] is not None:
                prev, mv = parent[key]
                path.append(mv)
                key = prev
            return st, list(reversed(path))
        for d in [U, D, L, R]:
            ns = st.do_action(d)
            key = (ns.vehicle_pos, ns.dgx_pos)
            if key not in seen:
                seen.add(key)
                parent[key] = ((st.vehicle_pos, st.dgx_pos), ('A', d))
                frontier.append(ns)
    return None, None


if __name__ == '__main__':
    s0 = setup()
    print(f'Start: V at (22, 4)? {(22, 4) in s0.vehicle_pos}, DGX there? {(22, 4) in s0.dgx_pos}')
    result, path = shuffle_bfs(s0)
    if result:
        print(f'FOUND in {len(path)} A-actions:')
        print([f'A{[1,2,3,4][[U,D,L,R].index(m[1])]}' for m in path])
        print(f'Final V-pos: {result.vehicle_pos}')
        print(f'Final DGX: {result.dgx_pos}')
        print(f'  (22,4) V? {(22, 4) in result.vehicle_pos}, DGX? {(22, 4) in result.dgx_pos}')
    else:
        print('no')
