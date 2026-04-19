"""Multi-stage L10 solver:
  Stage A: reg1 reaches (4, 9).
  Stage B: From stage A state, blue6 no longer co-located with V at (8, 9).
  Stage C: From stage B, chain reg1 R via reg2 pivot. Win.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from collections import deque
from l7_sim import load_init
from l7_search import moves


def bfs(start, goal_fn, cap, label):
    frontier = deque([start])
    seen = {start.sig(): (None, None)}
    depth = {start.sig(): 0}
    t = time.time()
    md = 0
    while frontier and len(seen) < cap:
        s = frontier.popleft()
        d = depth[s.sig()]
        if d > md:
            md = d
            if md % 2 == 0:
                print(f'[{label}] d={d} seen={len(seen):,} t={time.time()-t:.0f}s')
        if goal_fn(s):
            path = []
            sig = s.sig()
            while seen[sig][0] is not None:
                prev, mv = seen[sig]
                path.append(mv)
                sig = prev
            return s, list(reversed(path)), d
        for mv, ns in moves(s):
            if ns.sig() not in seen:
                seen[ns.sig()] = (s.sig(), mv)
                depth[ns.sig()] = d + 1
                frontier.append(ns)
    return None, None, -1


def goal_stageA(s):
    # Need: one reg at (4, 9), the other still at (6, 9)
    r1 = s.pieces.get('reg1')
    r2 = s.pieces.get('reg2')
    if r1 == (4, 9) and r2 == (6, 9):
        return True
    if r2 == (4, 9) and r1 == (6, 9):
        return True
    return False


def goal_stageB(s):
    # (8, 9) has V but no blue
    if (8, 9) not in s.vehicle_pos:
        return False
    for pid, p in s.piece_pos:
        if p == (8, 9) and 'blue' in pid:
            return False
    # Also reg at (4, 9) still
    if s.pieces.get('reg1') != (4, 9) and s.pieces.get('reg2') != (4, 9):
        return False
    # reg2 at (6, 9) still (or swap)
    return s.pieces.get('reg2') == (6, 9) or s.pieces.get('reg1') == (6, 9)


def goal_win(s):
    return len(s.piece_pos) < 12


if __name__ == '__main__':
    s = load_init('/tmp/l10_init.json')
    print(f'init: {s.pieces}')

    print()
    print('=== Stage A: reg at (4, 9) ===')
    s1, p1, d1 = bfs(s, goal_stageA, 10_000_000, 'A')
    if s1:
        print(f'A: {len(p1)} moves. pieces={s1.pieces}')
    else:
        print('A unreached')
        sys.exit()

    print()
    print('=== Stage B: V at (8,9) no blue, reg at (4,9), reg2 at (6,9) ===')
    s2, p2, d2 = bfs(s1, goal_stageB, 5_000_000, 'B')
    if s2:
        print(f'B: {len(p2)} moves. pieces={s2.pieces}')
    else:
        print('B unreached')
        sys.exit()

    print()
    print('=== Stage C: win ===')
    s3, p3, d3 = bfs(s2, goal_win, 3_000_000, 'C')
    if s3:
        print(f'C: WIN in {len(p3)} moves')
        print(f'Total: {len(p1)+len(p2)+len(p3)} moves')
        with open('/tmp/l10_path.py', 'w') as f:
            f.write(f'PATH = {list(p1+p2+p3)!r}\n')
    else:
        print('C unreached')
