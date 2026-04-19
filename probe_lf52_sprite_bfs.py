"""BFS over L4 state, using sprite-level world coordinates as state key.
Much smaller than pixel state space, should find win if one exists.
"""
import copy
import sys
import time
from pathlib import Path
from collections import defaultdict, deque
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52


def sprite_state(g):
    """Return a hashable tuple of sprite name+position."""
    d = []
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        name = getattr(sp, 'name', '')
        if not name:
            continue  # skip no-name sprites (likely decoration)
        if name in ('dgxfozncuiz', 'kraubslpehi', 'kraubslpehi-<', 'kraubslpehi-up'):
            continue  # skip walls/goal-markers that don't move
        d.append((name, sp.x, sp.y))
    return tuple(sorted(d))


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
    """Group e-cells with orthogonal adjacency."""
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
    """Red hint clusters (chebyshev distance 2 to merge cross patterns)."""
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


def find_moves(g):
    """Enumerate all valid moves. A-actions and (click-cluster, click-red-cluster) pairs."""
    base = g_snap(g)
    pix0 = g.pixels()
    moves = []

    # A-actions
    for a in [1, 2, 3, 4]:
        g_restore(g, base)
        try:
            g.action(a)
            if sprite_state(g) != sprite_state_from(base[0]):
                moves.append(('A', a))
        except Exception:
            pass

    # Click-click moves
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


def sprite_state_from(game):
    d = []
    for item in game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        name = getattr(sp, 'name', '')
        if not name:
            continue
        if name in ('dgxfozncuiz', 'kraubslpehi', 'kraubslpehi-<', 'kraubslpehi-up'):
            continue
        d.append((name, sp.x, sp.y))
    return tuple(sorted(d))


def apply_move(g, move):
    if move[0] == 'A':
        g.action(move[1])
    else:
        src, dst = move[1], move[2]
        g.click(*src)
        # Re-find closest red cluster center (cluster center may have shifted 1-2 pixels)
        pix_sel = g.pixels()
        red_clusters = find_red_clusters(pix_sel)
        if red_clusters:
            best = min(red_clusters, key=lambda rc: abs(cluster_center(rc)[0] - dst[0]) + abs(cluster_center(rc)[1] - dst[1]))
            bx, by = cluster_center(best)
            g.click(bx, by)
        else:
            g.click(*dst)


def bfs_main(max_depth=20):
    t0 = time.time()
    g = LF52(up_to_level=4, verbose=False)
    init_pc = piece_count(g)
    print(f'Initial piece count: {init_pc}')

    init_snap = g_snap(g)
    init_key = sprite_state(g)

    frontier = [(init_snap, [])]
    seen = {init_key}
    best_pc = init_pc
    best_path = []

    for depth in range(1, max_depth + 1):
        new_frontier = []
        for snap, path in frontier:
            g_restore(g, snap)
            moves = find_moves(g)
            for move in moves:
                g_restore(g, snap)
                try:
                    apply_move(g, move)
                except Exception:
                    continue
                lvl = g.level()
                if lvl > 3:
                    print(f'*** WIN at depth {depth}! path-len={len(path)+1}')
                    print(f'  path: {path + [move]}')
                    return path + [move]
                key = sprite_state(g)
                if key not in seen:
                    seen.add(key)
                    new_frontier.append((g_snap(g), path + [move]))
                    pc = piece_count(g)
                    if pc < best_pc:
                        best_pc = pc
                        best_path = path + [move]
                        print(f'  depth {depth}: new best piece_count={pc}, path-len={len(best_path)}', flush=True)
                        print(f'    path: {best_path}', flush=True)

        elapsed = time.time() - t0
        print(f'Depth {depth}: frontier={len(new_frontier)} seen={len(seen)} elapsed={elapsed:.1f}s', flush=True)
        frontier = new_frontier
        if not frontier:
            print('No more moves')
            break

    print(f'\nBest path: pc={best_pc}, len={len(best_path)}')
    print(f'  {best_path}')


if __name__ == '__main__':
    bfs_main(max_depth=15)
