"""Investigate state AFTER step 15 of the L4 partial sequence.
Step 15 consumed 2 e-pieces (24→16) + bumped 7 count (15→17).
Now what clicks are available? Is there a path to reduce further without spawn regress?
"""
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52, render_png
from solutions.solution_lf52_l4_partial import L4_PARTIAL


def all_positions(pix, color):
    ys, xs = np.where(pix == color)
    return set(zip(xs.tolist(), ys.tolist()))


def group_positions(positions):
    if not positions:
        return []
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


def cluster_centers(positions):
    out = []
    for c in group_positions(positions):
        xs = [p[0] for p in c]
        ys = [p[1] for p in c]
        out.append((sum(xs) // len(xs), sum(ys) // len(ys), len(c)))
    return sorted(out)


def click_probe(g, x, y, label):
    """Click at (x,y), report hints and selectable state, then restore."""
    snap = copy.deepcopy(g.env._game)
    g.click(x, y)
    pix = g.pixels()
    red = all_positions(pix, 2)
    green = all_positions(pix, 3)
    yellow = all_positions(pix, 4)
    red_clusters = cluster_centers(red)
    green_clusters = cluster_centers(green)
    yellow_clusters = cluster_centers(yellow)
    print(f'  click({x:2d},{y:2d}) [{label:20s}]: G{len(green_clusters)} Y{len(yellow_clusters)} R{len(red_clusters)}')
    if red_clusters:
        for rc in red_clusters:
            print(f'     red-hint: ({rc[0]},{rc[1]}) size={rc[2]}')
    g.env._game = snap
    g.obs = None
    g._cached_frame = None


def main():
    g = LF52(up_to_level=4)

    # Apply full partial sequence
    for step in L4_PARTIAL:
        if step[0] == 'C':
            g.click(*step[1])
            g.click(*step[2])
        else:
            g.action(step[1])

    pix = g.pixels()
    print(f'\n=== After L4_PARTIAL (25 actions): lvl={g.level()}, state={g.state_name()} ===')
    counts = {v: int((pix == v).sum()) for v in range(16) if int((pix == v).sum()) > 0}
    print(f'colors: {counts}')

    e_clusters = cluster_centers(all_positions(pix, 14))
    sev_clusters = cluster_centers(all_positions(pix, 7))
    f_clusters = cluster_centers(all_positions(pix, 15))
    c_clusters = cluster_centers(all_positions(pix, 12))
    print(f'\ne-clusters ({len(e_clusters)}):', e_clusters)
    print(f'7-clusters ({len(sev_clusters)}):', sev_clusters)
    print(f'f-clusters ({len(f_clusters)}):', f_clusters)
    print(f'c-clusters ({len(c_clusters)}):', c_clusters)

    render_png(pix, label='After step 25').save('/tmp/lf52_frames/L4_post25.png')
    print('\nSaved /tmp/lf52_frames/L4_post25.png')

    # === Test all clickable e-piece positions ===
    print('\n--- Probe all e-cluster clicks ---')
    for cx, cy, sz in e_clusters:
        click_probe(g, cx, cy, f'e@({cx},{cy}) sz{sz}')

    # === Also try clicking 7-cells (goals) directly ===
    print('\n--- Probe 7-cell clicks (goals) ---')
    for gx, gy, sz in sev_clusters:
        click_probe(g, gx, gy, f'7@({gx},{gy}) sz{sz}')

    # === Try each A-action (may reveal viewport changes) ===
    print('\n--- Test A-actions from this state (without commit) ---')
    for a in [1, 2, 3, 4]:
        snap = copy.deepcopy(g.env._game)
        before_pix = g.pixels()
        try:
            g.action(a)
            after_pix = g.pixels()
            diff = int((before_pix != after_pix).sum())
            e_clusters_after = cluster_centers(all_positions(after_pix, 14))
            print(f'  A{a}: {diff} cells changed, e-clusters={len(e_clusters_after)}, e-count={int((after_pix==14).sum())}')
        except Exception as e:
            print(f'  A{a}: ERROR {e}')
        g.env._game = snap
        g.obs = None
        g._cached_frame = None


if __name__ == '__main__':
    main()
