"""DFS from post-opener state, prune on unreachable configurations.
Goal: find a longer cycle that reduces piece count further."""
import copy, sys, time
from pathlib import Path
from collections import defaultdict, deque
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52


def piece_count(g):
    return sum(1 for item in g.env._game.ikhhdzfmarl._sorted_cache
               if getattr(item[1], 'name', '') == 'fozwvlovdui')


def g_snap(g):
    return (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))


def g_restore(g, snap):
    g.env._game = copy.deepcopy(snap[0])
    g.obs = copy.deepcopy(snap[1])
    g._cached_frame = None


def all_pos(pix, c):
    ys, xs = np.where(pix == c)
    return set(zip(xs.tolist(), ys.tolist()))


def find_e_clusters(pix):
    unassigned = all_pos(pix, 14)
    clusters = []
    while unassigned:
        seed = next(iter(unassigned))
        c = {seed}
        unassigned.discard(seed)
        q = deque([seed])
        while q:
            a, b = q.popleft()
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nb = (a+dx, b+dy)
                if nb in unassigned:
                    unassigned.discard(nb)
                    c.add(nb)
                    q.append(nb)
        clusters.append(c)
    return clusters


def cluster_center(cluster):
    xs = [x for x, y in cluster]
    ys = [y for x, y in cluster]
    return (sum(xs)//len(xs), sum(ys)//len(ys))


def find_red_clusters(pix):
    unassigned = all_pos(pix, 2)
    clusters = []
    while unassigned:
        seed = next(iter(unassigned))
        c = {seed}
        unassigned.discard(seed)
        q = deque([seed])
        while q:
            a, b = q.popleft()
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx == 0 and dy == 0: continue
                    nb = (a+dx, b+dy)
                    if nb in unassigned:
                        unassigned.discard(nb)
                        c.add(nb)
                        q.append(nb)
        clusters.append(c)
    return clusters


def sprite_state_tuple(g):
    d = []
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        name = getattr(sp, 'name', '')
        if not name or name in ('dgxfozncuiz', 'kraubslpehi', 'kraubslpehi-<', 'kraubslpehi-up'):
            continue
        d.append((name, sp.x, sp.y))
    return tuple(sorted(d))


def find_moves(g):
    base = g_snap(g)
    base_key = sprite_state_tuple(g)
    pix0 = g.pixels()
    moves = []
    for a in [1, 2, 3, 4]:
        g_restore(g, base)
        try:
            g.action(a)
            if sprite_state_tuple(g) != base_key:
                moves.append(('A', a))
        except Exception:
            pass
    e_clusters = find_e_clusters(pix0)
    for c in e_clusters:
        cx, cy = cluster_center(c)
        g_restore(g, base)
        try:
            g.click(cx, cy)
        except Exception:
            continue
        pix_sel = g.pixels()
        red_clusters = find_red_clusters(pix_sel)
        for rc in red_clusters:
            rx, ry = cluster_center(rc)
            moves.append(('C', (cx, cy), (rx, ry)))
    g_restore(g, base)
    return moves


def apply_move(g, move):
    if move[0] == 'A':
        g.action(move[1])
    else:
        src, dst = move[1], move[2]
        g.click(*src)
        pix_sel = g.pixels()
        red_clusters = find_red_clusters(pix_sel)
        if red_clusters:
            best = min(red_clusters, key=lambda rc: abs(cluster_center(rc)[0] - dst[0]) + abs(cluster_center(rc)[1] - dst[1]))
            bx, by = cluster_center(best)
            g.click(bx, by)
        else:
            g.click(*dst)


def apply_seq(g, seq):
    for step in seq:
        apply_move(g, step)


def dfs(g, path, seen, max_depth, best_state, t0, time_limit):
    if time.time() - t0 > time_limit:
        return
    if len(path) > max_depth:
        return

    pc = piece_count(g)
    lvl = g.level()
    if lvl > 3:
        print(f'*** WIN! path-len={len(path)} path={path}', flush=True)
        best_state['win'] = path
        return
    if pc < best_state['pc']:
        best_state['pc'] = pc
        best_state['path'] = list(path)
        print(f'  [{len(path)}] new best pc={pc}: {path[-5:] if len(path)>5 else path}', flush=True)

    if 'win' in best_state:
        return

    moves = find_moves(g)
    base = g_snap(g)
    for move in moves:
        g_restore(g, base)
        try:
            apply_move(g, move)
        except Exception:
            continue
        key = sprite_state_tuple(g)
        if key in seen and seen[key] <= len(path) + 1:
            continue
        seen[key] = len(path) + 1
        path.append(move)
        dfs(g, path, seen, max_depth, best_state, t0, time_limit)
        path.pop()
        if 'win' in best_state:
            return
    g_restore(g, base)


def main():
    OPENER = [
        ('A', 3),
        ('C', (13, 25), (25, 25)),
        ('C', (25, 25), (37, 25)),
        ('C', (37, 25), (49, 25)),
        ('A', 4), ('A', 4), ('A', 4), ('A', 4),
        ('C', (19, 25), (31, 25)),
    ]
    g = LF52(up_to_level=4, verbose=False)
    apply_seq(g, OPENER)
    print(f'After opener: pc={piece_count(g)}', flush=True)

    seen = {sprite_state_tuple(g): 0}
    best = {'pc': piece_count(g), 'path': []}
    t0 = time.time()
    dfs(g, [], seen, max_depth=25, best_state=best, t0=t0, time_limit=300)
    print(f'\nDone. best pc={best["pc"]} len={len(best["path"])}', flush=True)
    print(f'path: {best["path"]}', flush=True)


if __name__ == '__main__':
    main()
