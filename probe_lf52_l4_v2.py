"""After load, explore the second vehicle (sub-panel vehicle) mechanics.
Can it move A1/A2 up/down? Can we load/unload it? Drive it to sub-panel piece?"""
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52, render_png


def all_pos(pix, c):
    ys, xs = np.where(pix == c)
    return set(zip(xs.tolist(), ys.tolist()))


def group_pos(positions, max_dist=1):
    unassigned = set(positions)
    clusters = []
    while unassigned:
        seed = next(iter(unassigned))
        cluster = [seed]
        unassigned.remove(seed)
        frontier = [seed]
        while frontier:
            cx, cy = frontier.pop()
            for dx in range(-max_dist, max_dist + 1):
                for dy in range(-max_dist, max_dist + 1):
                    if dx == 0 and dy == 0:
                        continue
                    nb = (cx + dx, cy + dy)
                    if nb in unassigned:
                        unassigned.remove(nb)
                        cluster.append(nb)
                        frontier.append(nb)
        clusters.append(cluster)
    return clusters


def centers(positions, max_dist=1):
    return sorted((sum(p[0] for p in c)//len(c), sum(p[1] for p in c)//len(c), len(c))
                  for c in group_pos(positions, max_dist))


def g_snap(g):
    return (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))


def g_restore(g, snap):
    g.env._game = copy.deepcopy(snap[0])
    g.obs = copy.deepcopy(snap[1])
    g._cached_frame = None


def apply_seq(g, seq):
    for step in seq:
        if step[0] == 'C':
            g.click(*step[1])
            g.click(*step[2])
        else:
            g.action(step[1])


def summary(g, label):
    pix = g.pixels()
    e = centers(all_pos(pix, 14))
    b = centers(all_pos(pix, 11))
    c_big = [c for c in centers(all_pos(pix, 12)) if c[2] >= 4]
    sev = centers(all_pos(pix, 7))
    print(f'{label:40s} e={e} b={b} c_big={c_big}')


def main():
    g = LF52(up_to_level=4, verbose=False)
    apply_seq(g, [
        ('C', (13, 25), (25, 25)),
        ('C', (25, 25), (37, 25)),
        ('A', 3),
        ('C', (37, 25), (49, 25)),
    ])
    loaded = g_snap(g)
    summary(g, 'Just loaded')

    # Sequences of A-actions to drive sub-panel vehicle
    print('\n--- Drive sub-panel vehicle (vehicle 2 at 43, 49) ---')
    for seq_name, seq in [
        ('A1', [1]), ('A1x2', [1, 1]), ('A1x3', [1, 1, 1]),
        ('A2', [2]), ('A2x2', [2, 2]), ('A2x3', [2, 2, 2]),
        ('A3', [3]), ('A3x2', [3, 3]),
        ('A4', [4]), ('A4x2', [4, 4]),
        ('A3x2+A2', [3, 3, 2]),
        ('A3+A2x2', [3, 2, 2]),
        ('A1+A3', [1, 3]),
        ('A2+A3', [2, 3]),
        ('A2+A4', [2, 4]),
        ('A4+A2', [4, 2]),
    ]:
        g_restore(g, loaded)
        for a in seq:
            g.action(a)
        summary(g, f'Loaded + {seq_name}')

    # Try clicking the SUB-PANEL PIECE after different sequences
    print('\n--- Try click sub-panel piece after various drives ---')
    for seq_name, seq in [
        ('base', []),
        ('A3', [3]), ('A3x2', [3, 3]), ('A3x3', [3, 3, 3]),
        ('A4', [4]),
        ('A3+A2', [3, 2]), ('A3x2+A2', [3, 3, 2]),
        ('A2', [2]), ('A2x2', [2, 2]),
    ]:
        g_restore(g, loaded)
        for a in seq:
            g.action(a)
        # Find sub-panel piece (look for e-cluster around row 61)
        pix = g.pixels()
        e_c = centers(all_pos(pix, 14))
        sub_pieces = [c for c in e_c if c[1] > 50]
        if sub_pieces:
            sc = sub_pieces[0]
            g.click(sc[0], sc[1])
            pix_sel = g.pixels()
            red = centers(all_pos(pix_sel, 2), max_dist=2)
            print(f'  {seq_name}: sub-piece at {sc}, click → red={red}')
        else:
            print(f'  {seq_name}: no sub-piece in viewport, e={e_c}')


if __name__ == '__main__':
    main()
