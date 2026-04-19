"""Try clicking 7-cells at various points in sequence. Also click vehicle interiors."""
import copy, sys
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
                    if dx == 0 and dy == 0: continue
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
            g.click(*step[1]); g.click(*step[2])
        else:
            g.action(step[1])


def probe_click_target(g, state_label, targets):
    base = g_snap(g)
    for cx, cy, tag in targets:
        g_restore(g, base)
        pix_before = g.pixels()
        g.click(cx, cy)
        pix_after = g.pixels()
        lvl = g.level()
        diff = int((pix_before != pix_after).sum())
        red = int((pix_after == 2).sum())
        if diff > 2 or lvl > 3:
            print(f'  [{state_label}] click({cx:2d},{cy:2d}) [{tag:15s}]: diff={diff} red={red} lvl={lvl}')


def main():
    # Define the sequence to reach various states
    seq_full = [
        ('C', (13, 25), (25, 25)),
        ('C', (25, 25), (37, 25)),
        ('A', 3),
        ('C', (37, 25), (49, 25)),   # v1 load
        ('A', 4), ('A', 4), ('A', 4), ('A', 4),
        ('C', (19, 25), (31, 25)),
        ('C', (31, 25), (31, 37)),
        ('C', (31, 37), (31, 49)),
        ('C', (49, 25), (49, 37)),
        ('C', (49, 37), (49, 49)),
        ('C', (49, 49), (37, 49)),
        ('C', (37, 49), (25, 49)),   # v2 load
    ]

    # States to test at
    states_to_test = [
        (4, 'after v1 load'),
        (8, 'after A4x4'),
        (9, 'after chain-merge'),
        (11, 'pieces at row 49'),
        (13, 'both at row 49'),
        (14, 'chain left'),
        (15, 'after v2 load'),
    ]

    for stop_idx, label in states_to_test:
        g = LF52(up_to_level=4, verbose=False)
        for step in seq_full[:stop_idx]:
            if step[0] == 'C':
                g.click(*step[1]); g.click(*step[2])
            else:
                g.action(step[1])
        pix = g.pixels()
        e_c = centers(all_pos(pix, 14))
        sev_c = centers(all_pos(pix, 7))
        b_c = centers(all_pos(pix, 11))
        c_big = [c for c in centers(all_pos(pix, 12)) if c[2] >= 4]
        print(f'\n=== State after step {stop_idx} ({label}) ===')
        print(f'  e={e_c} 7={sev_c} b={b_c} c={c_big}')

        # Build click targets: all 7-cells, all e-piece centers, all vehicle centers
        targets = []
        for c in sev_c:
            targets.append((c[0], c[1], f'7cell'))
        for c in b_c:
            targets.append((c[0], c[1], f'vehicle'))
        # Also click each e-piece
        for c in e_c:
            targets.append((c[0], c[1], f'e-piece'))

        probe_click_target(g, label, targets)

    # Also: after full sequence, explore A-action combos
    print('\n=== After full sequence (15 steps), explore A-combos ===')
    g = LF52(up_to_level=4, verbose=False)
    apply_seq(g, seq_full)
    base = g_snap(g)
    # Try various A-sequences
    for seq_name, a_seq in [
        ('A3', [3]), ('A3x2', [3, 3]), ('A3x3', [3, 3, 3]),
        ('A3+A1', [3, 1]), ('A3+A2', [3, 2]),
        ('A3x3+A1', [3, 3, 3, 1]),
        ('A3x3+A2', [3, 3, 3, 2]),
        ('A3x3+A4', [3, 3, 3, 4]),
    ]:
        g_restore(g, base)
        for a in a_seq:
            g.action(a)
        pix = g.pixels()
        e_c = centers(all_pos(pix, 14))
        lvl = g.level()
        print(f'  {seq_name}: lvl={lvl} e={e_c}')
        # Also try clicks at each e
        for cx, cy, sz in e_c:
            snap2 = g_snap(g)
            g.click(cx, cy)
            pix_sel = g.pixels()
            red = centers(all_pos(pix_sel, 2), max_dist=2)
            if red:
                print(f'    click e@({cx},{cy}): red={red}')
            g_restore(g, snap2)


if __name__ == '__main__':
    main()
