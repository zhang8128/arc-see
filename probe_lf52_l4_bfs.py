"""Small BFS from L4 init: at each state, enumerate all e-piece click positions,
for each that gives red hints, click the hint, and see if we can reach lvl=4.
"""
import copy
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52, render_png


def all_pos(pix, c):
    ys, xs = np.where(pix == c)
    return set(zip(xs.tolist(), ys.tolist()))


def group_pos(positions):
    unassigned = set(positions)
    clusters = []
    while unassigned:
        seed = next(iter(unassigned))
        cluster = [seed]
        unassigned.remove(seed)
        frontier = [seed]
        while frontier:
            cx, cy = frontier.pop()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nb = (cx + dx, cy + dy)
                if nb in unassigned:
                    unassigned.remove(nb)
                    cluster.append(nb)
                    frontier.append(nb)
        clusters.append(cluster)
    return clusters


def centers(positions):
    return sorted((sum(p[0] for p in c)//len(c), sum(p[1] for p in c)//len(c), len(c))
                  for c in group_pos(positions))


def g_snap(g):
    return (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))


def g_restore(g, snap):
    g.env._game = copy.deepcopy(snap[0])
    g.obs = copy.deepcopy(snap[1])
    g._cached_frame = None


def state_key(g):
    """A hashable state signature — just use pixel tuple."""
    return tuple(map(tuple, g.pixels()))


def find_moves(g):
    """Return list of (click1, click2) pairs that advance state.
    For each e-piece center, click it; if red hints appear, each red cluster is a move.
    Also include A-actions as (('A', n),) tuples.
    """
    base = g_snap(g)
    pix0 = g.pixels()
    moves = []

    # A-actions
    for a in [1, 2, 3, 4]:
        g_restore(g, base)
        try:
            g.action(a)
            if int((g.pixels() != pix0).sum()) > 5:
                moves.append(('A', a))
        except Exception:
            pass

    # Click-click moves
    e_clusters = centers(all_pos(pix0, 14))
    for cx, cy, sz in e_clusters:
        g_restore(g, base)
        try:
            g.click(cx, cy)
        except Exception:
            continue
        pix_after_sel = g.pixels()
        red = centers(all_pos(pix_after_sel, 2))
        for rx, ry, rsz in red:
            moves.append(('C', (cx, cy), (rx, ry)))

    g_restore(g, base)
    return moves


def apply_move(g, move):
    if move[0] == 'A':
        g.action(move[1])
    else:
        g.click(*move[1])
        g.click(*move[2])


def main():
    t0 = time.time()
    g = LF52(up_to_level=4, verbose=False)
    init_snap = g_snap(g)
    init_key = state_key(g)

    # Frontier: list of (snapshot, path)
    frontier = [(init_snap, [])]
    seen = {init_key}

    MAX_DEPTH = 3
    depth = 0

    while frontier and depth < MAX_DEPTH:
        depth += 1
        new_frontier = []
        print(f'--- Depth {depth} ---')
        for snap, path in frontier:
            g_restore(g, snap)
            moves = find_moves(g)
            print(f'  Path {path}: {len(moves)} moves: {moves}')
            for move in moves:
                g_restore(g, snap)
                try:
                    apply_move(g, move)
                except Exception as e:
                    continue
                lvl = g.level()
                new_state = g_snap(g)
                key = state_key(g)
                if lvl > 3:
                    print(f'  *** WIN! path={path + [move]} lvl={lvl}')
                    return path + [move]
                if key not in seen:
                    seen.add(key)
                    new_frontier.append((new_state, path + [move]))
        frontier = new_frontier
        elapsed = time.time() - t0
        print(f'  depth {depth}: {len(frontier)} new states, elapsed {elapsed:.1f}s')

    print(f'\nNo win found in {MAX_DEPTH} depth levels')


if __name__ == '__main__':
    main()
