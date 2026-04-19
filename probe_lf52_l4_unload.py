"""From each intermediate state in L4_PARTIAL, probe the loaded vehicle click.
Goal: find unload landings that absorb multiple pieces for net piece reduction.
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


def g_snap(g):
    return (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))


def g_restore(g, snap):
    g.env._game = copy.deepcopy(snap[0])
    g.obs = copy.deepcopy(snap[1])
    g._cached_frame = None


def apply(g, steps):
    for step in steps:
        if step[0] == 'C':
            g.click(*step[1])
            g.click(*step[2])
        else:
            g.action(step[1])


def probe_clicks(g, label, targets):
    """For each target click coord, snapshot-click-report."""
    base = g_snap(g)
    pix_before = g.pixels()
    print(f'\n=== {label} ===')
    e_before = centers(all_pos(pix_before, 14))
    print(f'  before: e-clusters={len(e_before)}: {e_before}')
    for (cx, cy, tag) in targets:
        g_restore(g, base)
        g.click(cx, cy)
        pix_after = g.pixels()
        diff = int((pix_before != pix_after).sum())
        red = centers(all_pos(pix_after, 2))
        if red:
            print(f'  click({cx:2d},{cy:2d}) [{tag:20s}]: {diff} changed, red={red}')
        elif diff > 2:
            print(f'  click({cx:2d},{cy:2d}) [{tag:20s}]: {diff} changed (no red hints)')


def main():
    g = LF52(up_to_level=4, verbose=False)
    # Execute up to step 8 (after A4×4 = state with 3 pieces: tile2, tile3, vehicle)
    apply(g, L4_PARTIAL[:8])
    targets = [
        (49, 25, 'vehicle'),
        (50, 25, 'vehicle-r'),
        (48, 25, 'vehicle-l'),
        (49, 26, 'vehicle-b'),
        (48, 27, 'vehicle-bl'),
        (19, 25, 'tile2'),
        (25, 25, 'tile3'),
        (18, 25, 'tile2-l'),
        (27, 25, 'tile3-r'),
        (20, 25, 'tile2-r'),
        (24, 25, 'tile3-l'),
    ]
    probe_clicks(g, 'After 8 actions (3 pieces: tile2, tile3, vehicle-loaded)', targets)

    # Also probe from step 4 (just-loaded, before A4×4)
    g2 = LF52(up_to_level=4, verbose=False)
    apply(g2, L4_PARTIAL[:4])
    targets4 = [
        (49, 25, 'vehicle'),
        (19, 25, 'tile2-spawned'),
        (7, 61, 'sub-panel'),
        (18, 25, 'tile2-alt'),
        (20, 25, 'tile2-alt2'),
    ]
    probe_clicks(g2, 'After 4 actions (vehicle just loaded)', targets4)


if __name__ == '__main__':
    main()
