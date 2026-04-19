"""Single env, apply 25-action partial + A3, then probe each clickable position.
Use engine deepcopy to branch exploration without re-fetching from API.
"""
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52, render_png
from solutions.solution_lf52_l4_partial import L4_PARTIAL


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


def apply_partial(g):
    for step in L4_PARTIAL:
        if step[0] == 'C':
            g.click(*step[1])
            g.click(*step[2])
        else:
            g.action(step[1])


def g_snap(g):
    return (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))


def g_restore(g, snap):
    g.env._game = copy.deepcopy(snap[0])
    g.obs = copy.deepcopy(snap[1])
    g._cached_frame = None


def main():
    g = LF52(up_to_level=4, verbose=False)
    apply_partial(g)
    g.action(3)  # A3 scroll
    pix = g.pixels()
    print(f'After 25 + A3: lvl={g.level()} e={int((pix==14).sum())} 7={int((pix==7).sum())}')
    e_clusters = centers(all_pos(pix, 14))
    sev_clusters = centers(all_pos(pix, 7))
    f_clusters = centers(all_pos(pix, 15))
    print(f'  e-clusters: {e_clusters}')
    print(f'  7-clusters: {sev_clusters}')
    print(f'  f-clusters: {f_clusters}')
    render_png(pix, label='post25 + A3').save('/tmp/lf52_frames/L4_post25A3.png')

    base_snap = g_snap(g)

    print('\n--- Click each e-piece center ---')
    for cx, cy, sz in e_clusters:
        g_restore(g, base_snap)
        g.click(cx, cy)
        pix_after = g.pixels()
        red = centers(all_pos(pix_after, 2))
        diff = int((pix != pix_after).sum())
        print(f'  click e@({cx},{cy}) sz={sz}: diff={diff} red-hints={red}')

    print('\n--- Click around e@(4, 55) ---')
    for (cx, cy) in [(3, 55), (4, 55), (5, 55), (6, 55), (4, 54), (4, 56),
                     (5, 54), (5, 56), (4, 53), (4, 57), (5, 53), (5, 57),
                     (3, 54), (3, 56), (6, 54), (6, 56)]:
        g_restore(g, base_snap)
        g.click(cx, cy)
        pix_after = g.pixels()
        red = centers(all_pos(pix_after, 2))
        diff = int((pix != pix_after).sum())
        if red or diff > 10:
            print(f'  click({cx},{cy}): diff={diff} red={red}')

    print('\n--- Click around e@(4, 31) ---')
    for (cx, cy) in [(3, 31), (4, 31), (5, 31), (6, 31), (4, 30), (4, 32),
                     (5, 30), (5, 32)]:
        g_restore(g, base_snap)
        g.click(cx, cy)
        pix_after = g.pixels()
        red = centers(all_pos(pix_after, 2))
        diff = int((pix != pix_after).sum())
        if red or diff > 10:
            print(f'  click({cx},{cy}): diff={diff} red={red}')

    print('\n--- Click on loaded top vehicle e@(40, 19) ---')
    for (cx, cy) in [(38, 18), (39, 18), (40, 18), (41, 18),
                     (38, 19), (39, 19), (40, 19), (41, 19), (42, 19),
                     (38, 20), (41, 20), (40, 20), (39, 20),
                     (38, 21), (39, 21), (40, 21), (41, 21)]:
        g_restore(g, base_snap)
        g.click(cx, cy)
        pix_after = g.pixels()
        red = centers(all_pos(pix_after, 2))
        diff = int((pix != pix_after).sum())
        if red or diff > 10:
            print(f'  click({cx},{cy}): diff={diff} red={red}')


if __name__ == '__main__':
    main()
