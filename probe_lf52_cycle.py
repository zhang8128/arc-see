"""After the 9-action opener (reaches 4 pieces), see if a second cycle works.
Opener: A3, 3 merges to load v1, A4x4, chain pivot merge -> 4 pieces.
Then: descend? load another vehicle? explore all available moves."""
import copy, sys
from pathlib import Path
from collections import defaultdict, deque
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52, render_png


def sprite_map(g):
    d = defaultdict(list)
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        d[getattr(sp, 'name', '')].append((sp.x, sp.y))
    return d


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
    pix0 = g.pixels()
    moves = []
    for a in [1, 2, 3, 4]:
        g_restore(g, base)
        try:
            before = sprite_state_tuple(g)
            g.action(a)
            after = sprite_state_tuple(g)
            if before != after:
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


def sprite_state_tuple(g):
    d = []
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        name = getattr(sp, 'name', '')
        if not name or name in ('dgxfozncuiz', 'kraubslpehi', 'kraubslpehi-<', 'kraubslpehi-up'):
            continue
        d.append((name, sp.x, sp.y))
    return tuple(sorted(d))


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


def main():
    # 9-action opener
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
    pc = piece_count(g)
    sm = sprite_map(g)
    print(f'After opener: pc={pc}, foz={sorted(sm["fozwvlovdui"])}')
    render_png(g.pixels(), label='post-opener').save('/tmp/lf52_frames/L4_opener.png')

    # Enumerate moves from this state
    moves = find_moves(g)
    print(f'Moves available: {len(moves)}')
    for m in moves:
        print(f'  {m}')

    # Iterate: for each move, check if pc decreases
    base = g_snap(g)
    print()
    print('=== For each move, report new pc + state ===')
    for move in moves:
        g_restore(g, base)
        try:
            apply_move(g, move)
            pc2 = piece_count(g)
            sm2 = sprite_map(g)
            print(f'  {move}: pc={pc2} foz={sorted(sm2["fozwvlovdui"])}')
        except Exception as e:
            print(f'  {move}: ERROR {e}')


if __name__ == '__main__':
    main()
