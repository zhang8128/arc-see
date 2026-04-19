"""Test A1/A2 after correct load sequence. Do they move vehicle vertically?"""
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
    c = centers(all_pos(pix, 12))
    sev = centers(all_pos(pix, 7))
    print(f'{label:30s} lvl={g.level()} e={e} b={b} c={c} 7={sev}')


def main():
    # Load the vehicle correctly
    g = LF52(up_to_level=4, verbose=False)
    apply_seq(g, [
        ('C', (13, 25), (25, 25)),
        ('C', (25, 25), (37, 25)),
        ('A', 3),
        ('C', (37, 25), (49, 25)),  # LOAD
    ])
    summary(g, 'Just loaded')
    loaded = g_snap(g)

    # Test each single A-action
    for a in [1, 2, 3, 4]:
        g_restore(g, loaded)
        g.action(a)
        summary(g, f'Loaded + A{a}')

    # Load + A1 + test clicks
    g_restore(g, loaded)
    g.action(1)
    render_png(g.pixels(), label='loaded + A1').save('/tmp/lf52_frames/L4_load_A1.png')
    summary(g, 'Loaded + A1 (vis)')

    g_restore(g, loaded)
    g.action(2)
    render_png(g.pixels(), label='loaded + A2').save('/tmp/lf52_frames/L4_load_A2.png')
    summary(g, 'Loaded + A2 (vis)')

    # Try A1 multiple times
    g_restore(g, loaded)
    for _ in range(3):
        g.action(1)
    summary(g, 'Loaded + A1×3')
    render_png(g.pixels(), label='loaded + A1x3').save('/tmp/lf52_frames/L4_load_A1x3.png')

    # What about A1/A2 from INIT (no load)?
    g_restore(g, loaded)
    g_init = LF52(up_to_level=4, verbose=False)
    summary(g_init, 'L4 init')
    init_snap = g_snap(g_init)
    for a in [1, 2]:
        g_restore(g_init, init_snap)
        try:
            g_init.action(a)
            summary(g_init, f'Init + A{a}')
        except Exception as e:
            print(f'Init + A{a}: ERROR {e}')


if __name__ == '__main__':
    main()
