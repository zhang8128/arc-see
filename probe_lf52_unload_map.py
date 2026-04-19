"""After load + N A-actions, enumerate all e-piece clicks and their red hints.
Find states where unload absorbs multiple pieces or lands on 7-goals."""
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52


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


def load_vehicle(g):
    """Standard load: tile 1 → tile 3 → tile 5, then A3 to move vehicle, then chain into vehicle."""
    apply_seq(g, [
        ('C', (13, 25), (25, 25)),
        ('C', (25, 25), (37, 25)),
        ('A', 3),
        ('C', (37, 25), (49, 25)),
    ])


def explore_state(g, label):
    pix = g.pixels()
    base = g_snap(g)
    e_c = centers(all_pos(pix, 14))
    sev_c = centers(all_pos(pix, 7))
    f_c = centers(all_pos(pix, 15))
    print(f'\n=== {label} ===')
    print(f'  lvl={g.level()} e-count={int((pix==14).sum())} 7-count={int((pix==7).sum())}')
    print(f'  e-clusters ({len(e_c)}): {e_c}')
    print(f'  7-clusters ({len(sev_c)}): {sev_c}')

    # For each e-piece, click and report red hints
    piece_hints = {}
    for cx, cy, sz in e_c:
        g_restore(g, base)
        try:
            g.click(cx, cy)
        except Exception:
            continue
        pix_sel = g.pixels()
        red = centers(all_pos(pix_sel, 2), max_dist=2)
        if red:
            print(f'  click e@({cx},{cy}): red={red}')
            piece_hints[(cx, cy)] = red
    return piece_hints


def main():
    # Fresh env
    g = LF52(up_to_level=4, verbose=False)
    load_vehicle(g)
    print('Loaded vehicle (post-step 4, before any A-action)')
    explore_state(g, 'After load (0 A-actions)')

    # Each subsequent A-action
    post_load_snap = g_snap(g)
    for n_a4 in range(1, 6):
        g_restore(g, post_load_snap)
        for _ in range(n_a4):
            g.action(4)
        explore_state(g, f'After load + A4×{n_a4}')

    for n_a3 in range(1, 6):
        g_restore(g, post_load_snap)
        for _ in range(n_a3):
            g.action(3)
        explore_state(g, f'After load + A3×{n_a3}')

    # Also test A3 then A4 mix
    for (n3, n4) in [(1, 1), (1, 2), (2, 1), (2, 2), (1, 3), (3, 1), (2, 3), (3, 2)]:
        g_restore(g, post_load_snap)
        for _ in range(n3): g.action(3)
        for _ in range(n4): g.action(4)
        explore_state(g, f'After load + A3×{n3} + A4×{n4}')


if __name__ == '__main__':
    main()
