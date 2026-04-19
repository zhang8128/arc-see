"""A* / priority-queue search: prefer states with fewer pieces, breadth at each piece-count level."""
import copy
import sys
import heapq
import time
from pathlib import Path
from collections import defaultdict, deque
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52


def sprite_state(g):
    d = []
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        name = getattr(sp, 'name', '')
        if not name:
            continue
        if name in ('dgxfozncuiz', 'kraubslpehi', 'kraubslpehi-<', 'kraubslpehi-up'):
            continue
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


def find_moves(g):
    base = g_snap(g)
    base_key = sprite_state(g)
    pix0 = g.pixels()
    moves = []
    for a in [1, 2, 3, 4]:
        g_restore(g, base)
        try:
            g.action(a)
            if sprite_state(g) != base_key:
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


def astar_main(max_iterations=5000, max_pc_band=3):
    """Prioritize (piece_count, path_len). Band-search: only explore states within max_pc_band of best."""
    t0 = time.time()
    g = LF52(up_to_level=4, verbose=False)
    init_pc = piece_count(g)
    print(f'Initial piece count: {init_pc}', flush=True)
    init_snap = g_snap(g)
    init_key = sprite_state(g)

    # Priority queue: (piece_count, path_len, counter, snap, path)
    counter = 0
    pq = [(init_pc, 0, counter, init_snap, [])]
    seen = {init_key: 0}  # state_key -> best path_len seen

    best_pc = init_pc
    best_path = []
    iters = 0

    while pq and iters < max_iterations:
        pc, plen, cnt, snap, path = heapq.heappop(pq)
        if pc > best_pc + max_pc_band:
            continue  # prune
        iters += 1

        g_restore(g, snap)
        moves = find_moves(g)
        for move in moves:
            g_restore(g, snap)
            try:
                apply_move(g, move)
            except Exception:
                continue
            lvl = g.level()
            new_pc = piece_count(g)
            new_path = path + [move]
            if lvl > 3:
                print(f'*** WIN! path-len={len(new_path)}', flush=True)
                print(f'  path: {new_path}', flush=True)
                return new_path
            key = sprite_state(g)
            if key in seen and seen[key] <= len(new_path):
                continue
            seen[key] = len(new_path)
            if new_pc < best_pc:
                best_pc = new_pc
                best_path = new_path
                print(f'  iter {iters}: new best pc={new_pc} len={len(new_path)}', flush=True)
                print(f'    path: {new_path}', flush=True)
            counter += 1
            heapq.heappush(pq, (new_pc, len(new_path), counter, g_snap(g), new_path))

        if iters % 50 == 0:
            elapsed = time.time() - t0
            print(f'iter {iters}: pq={len(pq)} best_pc={best_pc} best_len={len(best_path)} elapsed={elapsed:.1f}s', flush=True)

    elapsed = time.time() - t0
    print(f'\nDone. Iters={iters} best pc={best_pc} len={len(best_path)} elapsed={elapsed:.1f}s', flush=True)
    print(f'Best path: {best_path}', flush=True)


if __name__ == '__main__':
    astar_main(max_iterations=3000, max_pc_band=2)
