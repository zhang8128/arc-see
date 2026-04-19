"""Explore state after L4_PARTIAL (25 actions). Test A-actions with FRESH env each time."""
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


def summarize(g, label):
    pix = g.pixels()
    e = centers(all_pos(pix, 14))
    s7 = centers(all_pos(pix, 7))
    print(f'{label:40s} lvl={g.level()} e={int((pix==14).sum())} 7={int((pix==7).sum())} '
          f'e-clusters={len(e)}: {e}')
    return pix


def apply_partial(g):
    """Apply L4_PARTIAL steps to a fresh env."""
    for step in L4_PARTIAL:
        if step[0] == 'C':
            g.click(*step[1])
            g.click(*step[2])
        else:
            g.action(step[1])


def try_a_action(a):
    """Fresh env, apply partial, then A-action, report result."""
    g = LF52(up_to_level=4, verbose=False)
    apply_partial(g)
    pix_before = g.pixels()
    try:
        g.action(a)
        pix_after = g.pixels()
        diff = int((pix_before != pix_after).sum())
        e_now = centers(all_pos(pix_after, 14))
        sev_now = centers(all_pos(pix_after, 7))
        print(f'  A{a}: {diff:4d} cells changed → e-clusters={len(e_now)}: {e_now}')
        print(f'         7-clusters={len(sev_now)}: {sev_now}')
        render_png(pix_after, label=f'A{a} after 25').save(f'/tmp/lf52_frames/L4_post25_A{a}.png')
    except Exception as e:
        print(f'  A{a}: ERROR {e}')


def try_click_after(click_pos, label):
    """Fresh env, apply partial, then click, report."""
    g = LF52(up_to_level=4, verbose=False)
    apply_partial(g)
    pix_before = g.pixels()
    try:
        g.click(*click_pos)
        pix_after = g.pixels()
        diff = int((pix_before != pix_after).sum())
        red = centers(all_pos(pix_after, 2))
        print(f'  click{click_pos} [{label}]: {diff} changed, red={red}, lvl={g.level()}')
    except Exception as e:
        print(f'  click{click_pos} [{label}]: ERROR {e}')


def main():
    # Baseline
    g = LF52(up_to_level=4, verbose=False)
    apply_partial(g)
    pix = summarize(g, '=== After 25 actions ===')
    render_png(pix, label='after 25 actions').save('/tmp/lf52_frames/L4_post25_v2.png')

    print('\n--- Try each A-action from this state (fresh env each time) ---')
    for a in [1, 2, 3, 4, 7]:
        try_a_action(a)

    print('\n--- Try clicks on visible elements ---')
    # loaded top vehicle e-cluster at (40, 19) — size 12
    try_click_after((40, 19), 'loaded-top-vehicle')
    try_click_after((38, 18), 'loaded-top-vehicle-alt')
    # partial pieces at (0, 31) and (0, 55)
    try_click_after((0, 31), 'partial-left-1')
    try_click_after((0, 55), 'partial-left-2')
    # bot vehicle (c-cluster at (22, 43) sz16) — loaded?
    try_click_after((22, 43), 'bot-vehicle-c')
    try_click_after((23, 43), 'bot-vehicle-c2')
    # Big c-cluster is 16 cells — that's a 4x4 vehicle interior. Let's sample inside.


if __name__ == '__main__':
    main()
