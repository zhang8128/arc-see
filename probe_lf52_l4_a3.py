"""After L4_PARTIAL (25 actions) + A3, probe what's clickable."""
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


def try_click_on_state(setup_actions, click_pos, label):
    """Fresh env, apply partial + extra setup actions, then click."""
    g = LF52(up_to_level=4, verbose=False)
    apply_partial(g)
    for a in setup_actions:
        if isinstance(a, tuple):
            g.click(*a)
        else:
            g.action(a)
    pix_before = g.pixels()
    e_before = centers(all_pos(pix_before, 14))
    try:
        g.click(*click_pos)
        pix_after = g.pixels()
        diff = int((pix_before != pix_after).sum())
        red = centers(all_pos(pix_after, 2))
        green = centers(all_pos(pix_after, 3))
        e_after = centers(all_pos(pix_after, 14))
        change = 'E-DROP' if int((pix_after==14).sum()) < int((pix_before==14).sum()) else ''
        print(f'  [{label:30s}] click{click_pos}: diff={diff:4d} G={len(green)} R={len(red)} lvl={g.level()} {change}')
        if red:
            print(f'    red hints: {red}')
    except Exception as e:
        print(f'  [{label}] click{click_pos}: ERROR {e}')


def show_state_after(actions, label):
    g = LF52(up_to_level=4, verbose=False)
    apply_partial(g)
    for a in actions:
        if isinstance(a, tuple):
            g.click(*a)
        else:
            g.action(a)
    pix = g.pixels()
    e = centers(all_pos(pix, 14))
    s7 = centers(all_pos(pix, 7))
    f = centers(all_pos(pix, 15))
    c = centers(all_pos(pix, 12))
    print(f'\n=== {label} ===')
    print(f'lvl={g.level()} state={g.state_name()} e={int((pix==14).sum())} 7={int((pix==7).sum())}')
    print(f'e-clusters ({len(e)}): {e}')
    print(f'7-clusters ({len(s7)}): {s7}')
    print(f'f-clusters ({len(f)}): {f}')
    print(f'c-clusters ({len(c)}): {c}')
    fname = label.replace(' ', '_').replace('+', 'p')
    render_png(pix, label=label).save(f'/tmp/lf52_frames/L4_{fname}.png')


def main():
    # Baseline: after 25 actions
    show_state_after([], 'post25')

    # After one A3
    show_state_after([3], 'post25_A3')

    # After two A3s
    show_state_after([3, 3], 'post25_A3A3')

    # After three A3s
    show_state_after([3, 3, 3], 'post25_A3A3A3')

    print('\n--- Clicks after A3 ---')
    # After A3, pieces at (4, 31) and (4, 55) should be clickable
    for setup in [[3], [3, 3], [3, 3, 3]]:
        for cp in [(4, 31), (4, 55), (5, 31), (5, 55), (3, 31)]:
            label = f'A3x{len(setup)} then'
            try_click_on_state(setup, cp, label)
        # And try clicking the loaded vehicle
        for cp in [(40, 19), (38, 18), (39, 19), (41, 19)]:
            try_click_on_state(setup, cp, f'A3x{len(setup)} vehicle')


if __name__ == '__main__':
    main()
