"""Test A-actions directly on L4 init. Does memory's claim hold up?"""
import copy
import sys
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


def test_action(g, base_snap, a, label):
    g_restore(g, base_snap)
    pix_before = g.pixels()
    g.action(a)
    pix_after = g.pixels()
    diff = int((pix_before != pix_after).sum())
    e_after = centers(all_pos(pix_after, 14))
    b_after = centers(all_pos(pix_after, 11))
    c_after = centers(all_pos(pix_after, 12))
    print(f'  A{a} [{label}]: diff={diff} e-clusters={e_after} b-clusters={b_after} c-clusters={c_after}')
    render_png(pix_after, label=f'init + A{a}').save(f'/tmp/lf52_frames/L4_init_A{a}.png')


def main():
    g = LF52(up_to_level=4, verbose=False)
    pix = g.pixels()
    print(f'L4 init: e={int((pix==14).sum())} f={int((pix==15).sum())}')
    e_c = centers(all_pos(pix, 14))
    b_c = centers(all_pos(pix, 11))
    c_c = centers(all_pos(pix, 12))
    print(f'e-clusters: {e_c}')
    print(f'b-clusters (vehicle borders): {b_c}')
    print(f'c-clusters (vehicle interiors): {c_c}')

    base = g_snap(g)
    print('\n--- Test each A-action from L4 init ---')
    for a in [1, 2, 3, 4]:
        test_action(g, base, a, f'init')

    print('\n--- Click tile 6 (right piece) to check if it can move ---')
    g_restore(g, base)
    pix_before = g.pixels()
    g.click(43, 25)
    pix_after = g.pixels()
    diff = int((pix_before != pix_after).sum())
    red = centers(all_pos(pix_after, 2))
    print(f'  click(43, 25) [right piece]: diff={diff} red={red}')

    g_restore(g, base)
    pix_before = g.pixels()
    g.click(37, 61)
    pix_after = g.pixels()
    diff = int((pix_before != pix_after).sum())
    red = centers(all_pos(pix_after, 2))
    print(f'  click(37, 61) [sub piece]: diff={diff} red={red}')

    print('\n--- After A3 from init, test again ---')
    g_restore(g, base)
    g.action(3)
    after_a3 = g_snap(g)
    pix = g.pixels()
    print(f'  after A3: e-clusters={centers(all_pos(pix, 14))}')
    print(f'           b-clusters={centers(all_pos(pix, 11))}')
    print(f'           c-clusters={centers(all_pos(pix, 12))}')

    # Click each e-piece after A3
    for cx, cy, sz in centers(all_pos(pix, 14)):
        g_restore(g, after_a3)
        g.click(cx, cy)
        pix_after = g.pixels()
        red = centers(all_pos(pix_after, 2))
        diff = int((pix != pix_after).sum())
        print(f'  click e@({cx},{cy}): diff={diff} red={red}')

    print('\n--- After A4 from init, test again ---')
    g_restore(g, base)
    g.action(4)
    after_a4 = g_snap(g)
    pix = g.pixels()
    print(f'  after A4: e-clusters={centers(all_pos(pix, 14))}')
    print(f'           b-clusters={centers(all_pos(pix, 11))}')
    print(f'           c-clusters={centers(all_pos(pix, 12))}')
    # Click each e-piece after A4
    for cx, cy, sz in centers(all_pos(pix, 14)):
        g_restore(g, after_a4)
        g.click(cx, cy)
        pix_after = g.pixels()
        red = centers(all_pos(pix_after, 2))
        diff = int((pix != pix_after).sum())
        print(f'  click e@({cx},{cy}): diff={diff} red={red}')


if __name__ == '__main__':
    main()
