"""Try to load sub-panel vehicle (vehicle 2) after unloading main and descending to row 49."""
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
    c_big = [c for c in centers(all_pos(pix, 12)) if c[2] >= 4]
    sev = centers(all_pos(pix, 7))
    f_big = [c for c in centers(all_pos(pix, 15)) if c[2] >= 6]
    print(f'{label:50s} lvl={g.level()}')
    print(f'  e={e} b={b} c={c_big} 7={sev}')
    print(f'  f_big={f_big}')


def probe_clicks(g, snap, label, coords):
    for cx, cy in coords:
        g_restore(g, snap)
        pix_before = g.pixels()
        g.click(cx, cy)
        pix_after = g.pixels()
        red = centers(all_pos(pix_after, 2), max_dist=2)
        diff = int((pix_before != pix_after).sum())
        if red or diff > 3:
            print(f'  [{label}] click({cx:2d},{cy:2d}): diff={diff} red={red}')


def main():
    g = LF52(up_to_level=4, verbose=False)
    # Load vehicle, then A4×4
    apply_seq(g, [
        ('C', (13, 25), (25, 25)),
        ('C', (25, 25), (37, 25)),
        ('A', 3),
        ('C', (37, 25), (49, 25)),
        ('A', 4), ('A', 4), ('A', 4), ('A', 4),
    ])
    state = g_snap(g)
    summary(g, 'After load + A4×4')

    # Step 9 partial: click (19, 25) → (31, 25)  [chain absorbs (25, 25) pivot]
    # But try instead: click (49, 25) → (49, 37)  [unload main vehicle down]
    print('\n--- Try: unload main vehicle down ---')
    g_restore(g, state)
    g.click(49, 25)
    g.click(49, 37)
    summary(g, 'After unload to (49, 37)')
    state2 = g_snap(g)
    render_png(g.pixels(), label='unload v1 to row 37').save('/tmp/lf52_frames/L4_unload_v1_row37.png')

    # Now try: click (49, 37) — does it have hints down to (49, 49)?
    probe_clicks(g, state2, 'after-unload', [
        (49, 37), (49, 25), (19, 25), (43, 25), (25, 25),
    ])

    # Test: execute (49, 37) → (49, 49) if hint exists
    print('\n--- Execute (49, 37) → (49, 49) ---')
    g_restore(g, state2)
    g.click(49, 37)
    pix_sel = g.pixels()
    red_at_49_49 = int(pix_sel[49, 49]) == 2
    print(f'  Red at (49,49)? {red_at_49_49}')
    if red_at_49_49:
        g.click(49, 49)
        summary(g, 'After jump to row 49')
        state3 = g_snap(g)
        render_png(g.pixels(), label='piece at row 49').save('/tmp/lf52_frames/L4_piece_row49.png')
        # Now try to load vehicle 2
        print('\n--- Click piece at (49, 49) to see hints for vehicle 2 load ---')
        probe_clicks(g, state3, 'row49-piece', [
            (49, 49), (48, 49), (50, 49), (43, 49), (37, 49),
        ])

    # Also try doing the step-9 chain first then unloading differently
    print('\n--- Step-9 chain then explore ---')
    g_restore(g, state)
    g.click(19, 25)
    g.click(31, 25)
    summary(g, 'After step-9 chain')
    state4 = g_snap(g)
    render_png(g.pixels(), label='step9').save('/tmp/lf52_frames/L4_step9.png')
    # From 2-piece state at (31, 25) and (49, 25), try to descend
    probe_clicks(g, state4, '2piece', [
        (31, 25), (49, 25), (31, 37), (49, 37), (31, 49), (49, 49),
    ])


if __name__ == '__main__':
    main()
