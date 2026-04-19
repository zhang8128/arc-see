"""Trace L4 state after each action of the known partial sequence.
Goal: understand f-container / 7-cell / vehicle state progression to find win trigger.
"""
import copy
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52, render_png
from solutions.solution_lf52_l4_partial import L4_PARTIAL


def state_summary(g):
    pix = g.pixels()
    return {
        'lvl': g.level(),
        'state': g.state_name(),
        'e': int((pix == 14).sum()),
        '7': int((pix == 7).sum()),
        'f': int((pix == 15).sum()),
        'c': int((pix == 12).sum()),  # vehicle interior (open)
        'b': int((pix == 11).sum()),  # vehicle border
        # Count e-clusters
        'e_positions': set((x, y) for y, x in zip(*np.where(pix == 14))),
        '7_positions': set((x, y) for y, x in zip(*np.where(pix == 7))),
    }


def group_positions(positions):
    """Group adjacent cells into clusters."""
    if not positions:
        return []
    positions = list(positions)
    clusters = []
    unassigned = set(positions)
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


def fmt_clusters(positions):
    clusters = group_positions(positions)
    parts = []
    for c in clusters:
        xs = [p[0] for p in c]
        ys = [p[1] for p in c]
        parts.append(f'({min(xs)}-{max(xs)},{min(ys)}-{max(ys)}):{len(c)}')
    return ', '.join(parts) if parts else '(none)'


def step_and_show(g, step, idx):
    kind = step[0]
    if kind == 'C':
        _, p1, p2 = step
        g.click(*p1)
        g.click(*p2)
        label = f'C({p1[0]},{p1[1]})→({p2[0]},{p2[1]})'
    else:
        _, a = step
        g.action(a)
        label = f'A{a}'
    s = state_summary(g)
    e_clusters = fmt_clusters(s['e_positions'])
    sev_clusters = fmt_clusters(s['7_positions'])
    print(f'[{idx:02d}] {label:30s} lvl={s["lvl"]} e={s["e"]:2d} 7={s["7"]:2d} f={s["f"]:2d} c={s["c"]:2d} '
          f'| e-clusters: {e_clusters} | 7-clusters: {sev_clusters}')
    return s


def main():
    g = LF52(up_to_level=4)
    s0 = state_summary(g)
    print(f'L4 init: e={s0["e"]} 7={s0["7"]} f={s0["f"]} c={s0["c"]} b={s0["b"]}')
    print(f'  e-clusters: {fmt_clusters(s0["e_positions"])}')
    print(f'  7-clusters: {fmt_clusters(s0["7_positions"])}')
    print()

    # Save initial render
    render_png(g.pixels(), label='L4 init').save('/tmp/lf52_frames/L4_trace_00.png')

    for i, step in enumerate(L4_PARTIAL, 1):
        s = step_and_show(g, step, i)
        render_png(g.pixels(), label=f'L4 step {i}').save(f'/tmp/lf52_frames/L4_trace_{i:02d}.png')


if __name__ == '__main__':
    main()
