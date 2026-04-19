"""Test full sequence: descend both pieces to row 49, chain into vehicle 2."""
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


def sstate(g):
    pix = g.pixels()
    e = centers(all_pos(pix, 14))
    b = centers(all_pos(pix, 11))
    c = [c for c in centers(all_pos(pix, 12)) if c[2] >= 4]
    return {'e': e, 'b': b, 'c': c, 'lvl': g.level()}


def hints(g, cx, cy):
    snap = g_snap(g)
    g.click(cx, cy)
    pix = g.pixels()
    red = centers(all_pos(pix, 2), max_dist=2)
    g_restore(g, snap)
    return red


def main():
    # Full sequence attempt
    g = LF52(up_to_level=4, verbose=False)
    seq = [
        ('C', (13, 25), (25, 25)),   # 1
        ('C', (25, 25), (37, 25)),   # 2
        ('A', 3),                     # 3
        ('C', (37, 25), (49, 25)),   # 4 LOAD v1
        ('A', 4), ('A', 4), ('A', 4), ('A', 4),  # 5-8 expand
        ('C', (19, 25), (31, 25)),   # 9 chain-merge via pivot
        ('C', (31, 25), (31, 37)),   # 10 descend
        ('C', (31, 37), (31, 49)),   # 11 descend
        ('C', (49, 25), (49, 37)),   # 12 descend (UNLOAD v1)
        ('C', (49, 37), (49, 49)),   # 13 descend
        ('C', (49, 49), (37, 49)),   # 14 chain left over f(43, 49)
    ]
    for i, step in enumerate(seq, 1):
        if step[0] == 'C':
            g.click(*step[1]); g.click(*step[2])
        else:
            g.action(step[1])
        s = sstate(g)
        print(f'{i:2d}. {step}: lvl={s["lvl"]} e={s["e"]}')

    # Now test hints at (37, 49)
    print('\n--- At state after (49,49)→(37,49), test (37, 49) hints ---')
    h = hints(g, 37, 49)
    print(f'hints at (37, 49): {h}')

    # Try to chain further left
    if h:
        # Try executing hint nearest to (25, 49) = vehicle 2
        best = None
        best_d = 1e9
        for rx, ry, sz in h:
            d = abs(rx - 25) + abs(ry - 49)
            if d < best_d:
                best_d = d
                best = (rx, ry)
        print(f'best hint: {best}')
        if best:
            g.click(37, 49)
            g.click(*best)
            s = sstate(g)
            print(f'After click best: lvl={s["lvl"]} e={s["e"]} b={s["b"]} c={s["c"]}')
            render_png(g.pixels(), label='v2 load attempt').save('/tmp/lf52_frames/L4_v2_load.png')

            # Test if anything else is clickable now
            print('\n--- After v2 load attempt, enumerate moves ---')
            pix = g.pixels()
            e_centers = centers(all_pos(pix, 14))
            for cx, cy, sz in e_centers:
                hh = hints(g, cx, cy)
                if hh:
                    print(f'  e@({cx},{cy}): {hh}')
            # A-actions
            for a in [1, 2, 3, 4]:
                snap = g_snap(g)
                try:
                    g.action(a)
                    diff = int((pix != g.pixels()).sum())
                    lvl = g.level()
                    print(f'  A{a}: diff={diff} lvl={lvl}')
                except Exception as e:
                    print(f'  A{a}: ERROR {e}')
                g_restore(g, snap)


if __name__ == '__main__':
    main()
