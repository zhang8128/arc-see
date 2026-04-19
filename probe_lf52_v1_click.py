"""Explore clicks on vehicle 1 (loaded at 19, 25) and vehicle 2 (empty at 43, 49) after load."""
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


def probe_click(g, snap, cx, cy, label):
    g_restore(g, snap)
    pix_before = g.pixels()
    g.click(cx, cy)
    pix_after = g.pixels()
    red = centers(all_pos(pix_after, 2), max_dist=2)
    diff = int((pix_before != pix_after).sum())
    if red or diff > 3:
        print(f'  {label:30s} click({cx:2d},{cy:2d}): diff={diff} red={red}')


def main():
    g = LF52(up_to_level=4, verbose=False)
    apply_seq(g, [
        ('C', (13, 25), (25, 25)),
        ('C', (25, 25), (37, 25)),
        ('A', 3),
        ('C', (37, 25), (49, 25)),
    ])
    loaded = g_snap(g)
    render_png(g.pixels(), label='just loaded').save('/tmp/lf52_frames/L4_just_loaded.png')

    # Probe vehicle 1 (loaded at 19, 25) click
    print('--- Vehicle 1 (loaded) clicks ---')
    for cx in range(16, 24):
        for cy in range(22, 29):
            probe_click(g, loaded, cx, cy, 'v1')

    # Probe vehicle 2 (empty at 43, 49)
    print('\n--- Vehicle 2 (empty) clicks ---')
    for cx in range(40, 48):
        for cy in range(45, 54):
            probe_click(g, loaded, cx, cy, 'v2')

    # Probe free e-piece at (49, 25)
    print('\n--- Free e-piece (49, 25) clicks ---')
    for cx in range(47, 52):
        for cy in range(23, 28):
            probe_click(g, loaded, cx, cy, 'free-e')

    # After A4 or A3, re-probe vehicle clicks
    print('\n--- After A4: click everything ---')
    g_restore(g, loaded)
    g.action(4)
    a4_snap = g_snap(g)
    for cx in [19, 25, 37, 43, 49]:
        for cy in [25, 49, 61]:
            probe_click(g, a4_snap, cx, cy, 'A4 state')

    print('\n--- After A3: click everything ---')
    g_restore(g, loaded)
    g.action(3)
    a3_snap = g_snap(g)
    # Vehicle 2 moved to (37, 49)
    for cx in [19, 25, 37, 43, 49, 7]:
        for cy in [25, 49, 61]:
            probe_click(g, a3_snap, cx, cy, 'A3 state')


if __name__ == '__main__':
    main()
