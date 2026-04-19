"""Multi-stage planner:
Stage 1: post-bridge → reg1 loaded on vehicle (any R-vehicle, no DGX) at (18, 4).
Stage 2: from there → reg1 at (22, 5) + V at (22, 4) no DGX.
Stage 3: chain reg2 U for win.

Each stage uses its own focused BFS with appropriate heuristic.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time, heapq
from collections import deque
from l7_sim import load_init, Sim
from l7_search import moves
from l7_final import state_after_plan

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}
DN = {U:'U',D:'D',L:'L',R:'R'}


def bfs_stage(start, goal_fn, cap, label):
    frontier = deque([start])
    seen = {start.sig(): (None, None)}
    depth = {start.sig(): 0}
    t = time.time()
    while frontier and len(seen) < cap:
        s = frontier.popleft()
        if goal_fn(s):
            path = []
            sig = s.sig()
            while seen[sig][0] is not None:
                prev, mv = seen[sig]
                path.append(mv)
                sig = prev
            return s, list(reversed(path)), depth[s.sig()]
        for mv, ns in moves(s):
            if ns.sig() not in seen:
                seen[ns.sig()] = (s.sig(), mv)
                depth[ns.sig()] = depth[s.sig()] + 1
                frontier.append(ns)
        if len(seen) % 500_000 == 0:
            print(f'[{label}] seen={len(seen):,} t={time.time()-t:.0f}s')
    print(f'[{label}] EXHAUSTED seen={len(seen):,}')
    return None, None, -1


# Stage 1 goal: reg1 on vehicle at (18, 4) (R-vehicle, any DGX state — we just need reg1 loaded)
def stage1_goal(s):
    r1 = s.pieces.get('reg1')
    return r1 == (18, 4) and (18, 4) in s.vehicle_pos


# Stage 2 goal: reg1 at (22, 5), reg2 unchanged
def stage2_goal(s):
    return s.pieces.get('reg1') == (22, 5)


# Stage 3 goal: foz_count < 3 (win)
def stage3_goal(s):
    return s.foz_count() < 3


if __name__ == '__main__':
    s = state_after_plan()
    print(f'post-bridge: pieces={s.pieces}')

    print('=== Stage 1: reg1 loaded on V at (18, 4) ===')
    s1, path1, d1 = bfs_stage(s, stage1_goal, 3_000_000, 'stage1')
    print(f'Stage 1: {len(path1)} moves')

    print()
    print('=== Stage 2: reg1 at (22, 5) ===')
    s2, path2, d2 = bfs_stage(s1, stage2_goal, 8_000_000, 'stage2')
    if s2:
        print(f'Stage 2: {len(path2)} moves, pieces={s2.pieces}')
        print(f'  vehicles={s2.vehicle_pos}')
        print(f'  DGX-on-V={sorted(set(s2.dgx_pos)&set(s2.vehicle_pos))}')
    else:
        print('stage 2 UNREACHED')
        sys.exit()

    print()
    print('=== Stage 3: WIN (foz_count<3) ===')
    s3, path3, d3 = bfs_stage(s2, stage3_goal, 5_000_000, 'stage3')
    if s3:
        print(f'Stage 3: WIN in {len(path3)} moves!')
        print(f'  final: pieces={s3.pieces}, foz={s3.foz_count()}')
        print()
        print('FULL WIN PATH:')
        for i, m in enumerate(path1):
            print(f'  S1.{i}: {m}')
        for i, m in enumerate(path2):
            print(f'  S2.{i}: {m}')
        for i, m in enumerate(path3):
            print(f'  S3.{i}: {m}')
        print(f'Total extra moves from post-bridge: {len(path1)+len(path2)+len(path3)}')
    else:
        print('WIN UNREACHED')
