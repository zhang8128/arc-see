"""BP35 L2 hard solver with crusher simulation."""
import sys, re, time
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


def bfs_l2(grid, ppos, gpos, max_depth, click_range_x=5, click_range_y=8,
           max_states=10000000, stop_at_sec=600):
    """L2-focused BFS: only drop DOWN (no going back up) via gravity monotonicity."""
    queue = deque([(grid, ppos[0], ppos[1], True, [], 0)])
    visited = {make_key(grid, ppos[0], ppos[1], True)}
    states = 0
    t0 = time.time()
    best_y = ppos[1]  # track deepest y reached
    while queue:
        elapsed = time.time() - t0
        if elapsed > stop_at_sec:
            print(f'  Timeout {states}st best_y={best_y}'); return None
        g, px, py, gu, path, depth = queue.popleft()
        states += 1
        if py < best_y:
            best_y = py
            print(f'  NEW best_y={best_y} at depth={depth}, {states}st {elapsed:.0f}s')
        if states % 500000 == 0:
            print(f'  {states} st d={depth} q={len(queue)} best_y={best_y} {elapsed:.0f}s')
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


# L2 is the blocker. Try with very wide search.
lvl = 2
baseline = BASELINES[lvl-1]
grid, ppos, gpos = parse_grid(ALL_GRIDS[lvl])
clickable = sum(1 for v in grid.values() if v in CLICKABLE)
print(f'L{lvl} (bl={baseline}): P={ppos} G={gpos} clicks={clickable}')

# Escalating range
for rng_x, rng_y, time_limit in [(3, 5, 120), (5, 8, 300), (8, 15, 600)]:
    print(f'\nTrying range ({rng_x},{rng_y}), time_limit={time_limit}s')
    sol = bfs_l2(grid, ppos, gpos, max_depth=baseline + 10,
                 click_range_x=rng_x, click_range_y=rng_y,
                 stop_at_sec=time_limit, max_states=10000000)
    if sol:
        print(f'\n*** L{lvl} SOLVED ({len(sol)}): {" ".join(sol)}')
        import json
        with open('/tmp/bp35_l2_sol.json', 'w') as f:
            json.dump(sol, f)
        print(f'Saved to /tmp/bp35_l2_sol.json')
        break
else:
    print(f'\nL{lvl} still not solved after all attempts')
