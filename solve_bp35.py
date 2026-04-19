"""BP35 — pure-Python A* solver with tight click filter.

Usage:
  uv run python -u solve_bp35.py    # tries all unsolved levels

Approach:
  Pure-Python simulation of BP35 mechanics (no deepcopy of game engine).
  BFS/A* with actions: L, R, CB (click below), + limited remote clicks.
  Remote click filter: blocks within click_range_x/y of the player.

Known solved: L1 (15), L3 (34), L4 (25), L5 (30), L6 (41).
Unsolved: L2 (bl 72, 51 clickables — too wide for BFS), L7-L9 (not attempted).

For L2:
  - Try: (a) IDDFS, (b) meet-in-the-middle (solve from player AND from gem),
    (c) hand-design path by analyzing grid, (d) widen click range to 20+ with patience
  - The 51 clickables break BFS; need problem-specific structure.
"""
import sys, re, time, heapq
from collections import deque
sys.stdout.reconfigure(line_buffering=True)

with open('environment_files/bp35/0a0ad940/bp35.py') as f:
    src = f.read()

ALL_GRIDS = {}
for m in re.finditer(r'"grid(\d+)":\s*qipeamczaw\(\s*\[([^\]]+)\]', src):
    num = int(m.group(1))
    rows = re.findall(r'"([^"]+)"', m.group(2))
    ALL_GRIDS[num] = rows[::-1]

BASELINES = [15, 72, 36, 31, 31, 48, 86, 155, 163]
PASSABLE = {None, 'tog_b', 'crush'}
CLICKABLE = {'break', 'tog_a', 'tog_b', 'gflip'}

def parse_grid(raw):
    grid, ppos, gpos = {}, None, None
    for y, row in enumerate(raw):
        for x, ch in enumerate(row):
            t = {'o':'wall','x':'break','v':'spike','+':'gem','m':'crush',
                 'w':'twall','1':'tog_a','2':'tog_b','g':'gflip','u':'spike'}.get(ch)
            if ch == 'n': ppos = (x, y)
            elif ch == '+': gpos = (x, y); grid[(x,y)] = 'gem'
            elif t: grid[(x,y)] = t
    return grid, ppos, gpos

def fall(g, x, y, gu):
    dy = -1 if gu else 1
    fx, fy = x, y
    while True:
        ny = fy + dy
        t = g.get((fx, ny))
        if t in PASSABLE: fy = ny
        elif t == 'gem': return fx, ny, 'win'
        elif t == 'spike': return fx, fy, 'lose'
        else: return fx, fy, 'ok'

def do_move(g, px, py, gu, dx):
    nx = px + dx
    t = g.get((nx, py))
    if t == 'gem': return g, nx, py, gu, 'win'
    if t not in PASSABLE: return g, px, py, gu, 'noop'
    fx, fy, r = fall(g, nx, py, gu)
    return g, fx, fy, gu, r

def do_click(g, px, py, gu, cx, cy):
    t = g.get((cx, cy))
    if t not in CLICKABLE: return g, px, py, gu, 'noop'
    g = dict(g)
    dy = -1 if gu else 1
    below = (px, py + dy)
    ng = gu
    if t == 'break': del g[(cx, cy)]
    elif t == 'tog_a': g[(cx, cy)] = 'tog_b'
    elif t == 'tog_b':
        g[(cx, cy)] = 'tog_a'
        return g, px, py, gu, 'ok'
    elif t == 'gflip':
        del g[(cx, cy)]
        ng = not gu
    if t == 'gflip' or (cx, cy) == below:
        fx, fy, r = fall(g, px, py, ng)
        return g, fx, fy, ng, r
    return g, px, py, ng, 'ok'

def make_key(g, px, py, gu):
    blocks = tuple(sorted((k,v) for k,v in g.items() if v in CLICKABLE))
    return (px, py, gu, blocks)


def bfs(grid, ppos, gpos, max_depth, click_range_x=4, click_range_y=6, max_states=3000000, stop_at_sec=120):
    queue = deque([(grid, ppos[0], ppos[1], True, [], 0)])
    visited = {make_key(grid, ppos[0], ppos[1], True)}
    states = 0
    t0 = time.time()
    while queue:
        elapsed = time.time() - t0
        if elapsed > stop_at_sec:
            print(f'  Timeout {states}st'); return None
        g, px, py, gu, path, depth = queue.popleft()
        states += 1
        if states % 300000 == 0:
            print(f'  {states} st d={depth} q={len(queue)} {elapsed:.0f}s')
        if states > max_states: return None
        if depth >= max_depth: continue

        dy = -1 if gu else 1
        bx, by = px, py + dy

        for dx, desc in [(-1,'L'),(1,'R')]:
            _, nx, ny, ng, r = do_move(g, px, py, gu, dx)
            if r == 'win': return path + [desc]
            if r not in ('noop','lose'):
                k = make_key(g, nx, ny, ng)
                if k not in visited: visited.add(k); queue.append((g, nx, ny, ng, path+[desc], depth+1))

        g2, nx, ny, ng, r = do_click(g, px, py, gu, bx, by)
        if r == 'win': return path + ['CB']
        if r not in ('noop','lose'):
            k = make_key(g2, nx, ny, ng)
            if k not in visited: visited.add(k); queue.append((g2, nx, ny, ng, path+['CB'], depth+1))

        for (cx, cy), t in g.items():
            if t not in CLICKABLE: continue
            if (cx, cy) == (bx, by): continue
            if abs(cx - px) > click_range_x or abs(cy - py) > click_range_y: continue
            g2, nx, ny, ng, r = do_click(g, px, py, gu, cx, cy)
            if r == 'win': return path + [f'C{cx},{cy}']
            if r not in ('noop','lose'):
                k = make_key(g2, nx, ny, ng)
                if k not in visited: visited.add(k); queue.append((g2, nx, ny, ng, path+[f'C{cx},{cy}'], depth+1))
    return None


# Known solutions
solutions = {
    1: ['R','R','R','R','L','L','CB','C4,12','C4,15','C4,16','L','R','CB','L','L'],
    3: ['R','C5,28','R','R','CB','C4,23','C5,23','L','C3,23','L','L','L','R','R','C5,17','C5,18','R','C6,17','C6,18','R','R','C5,12','C6,12','L','C4,12','L','C3,12','L','L','R','C5,7','R','R','R'],
    4: ['R','R','R','R','L','C5,7','R','L','L','L','L','C3,17','L','R','R','C7,23','C7,24','C3,23','R','C5,23','R','L','L','L','C4,31'],
    5: ['R','R','R','R','C7,9','C8,9','C9,9','C8,12','CB','R','CB','L','L','L','L','L','C3,21','C8,29','L','R','R','R','R','R','R','R','L','L','L','L'],
    6: ['R','R','R','R','R','C6,22','C6,25','C7,25','C4,31','L','L','R','R','L','L','C5,13','L','L','R','R','R','C8,1','L','L','C4,13','L','R','R','CB','L','L','R','R','R','R','L','L','L','L','L','L'],
}
print(f"Pre-solved: {sorted(solutions.keys())}")

# Try unsolved levels
for lvl in [2, 7, 8, 9]:
    if lvl not in ALL_GRIDS: continue
    if lvl in solutions: continue
    baseline = BASELINES[lvl-1]
    grid, ppos, gpos = parse_grid(ALL_GRIDS[lvl])
    clickable = sum(1 for v in grid.values() if v in CLICKABLE)
    print(f'\nL{lvl} (bl={baseline}): P={ppos} G={gpos} clicks={clickable}')

    for rng_x, rng_y in [(3, 4), (5, 6), (8, 10)]:
        print(f'  range ({rng_x},{rng_y})...')
        sol = bfs(grid, ppos, gpos, max_depth=baseline + 10,
                 click_range_x=rng_x, click_range_y=rng_y, stop_at_sec=60)
        if sol:
            solutions[lvl] = sol
            print(f'  L{lvl} SOLVED ({len(sol)}): {" ".join(sol)}')
            break
    else:
        print(f'  L{lvl} TIMEOUT')

print(f'\n{"="*60}')
print(f'Solutions: {sorted(solutions.keys())}')
for k in sorted(solutions.keys()):
    print(f'  L{k}: {len(solutions[k])} steps (bl={BASELINES[k-1]})')

import json
with open('/tmp/bp35_sols.json','w') as f:
    json.dump({str(k): v for k,v in solutions.items()}, f, indent=2)
print(f"\nSaved to /tmp/bp35_sols.json")
