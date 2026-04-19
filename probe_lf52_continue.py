"""After 15 actions (3 pieces left), explore how to reduce further."""
import copy, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from lf52_tool import LF52, render_png
from collections import defaultdict


def sprite_map(g):
    renderer = g.env._game.ikhhdzfmarl
    by_name = defaultdict(list)
    for item in renderer._sorted_cache:
        _, sp, _ = item
        by_name[getattr(sp, 'name', '')].append((sp.x, sp.y))
    return by_name


def all_pos(pix, c):
    ys, xs = np.where(pix == c)
    return set(zip(xs.tolist(), ys.tolist()))


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


def enumerate_clicks(g, label):
    """Try clicking every pixel where a piece exists and report hints."""
    pix = g.pixels()
    base = g_snap(g)
    e_cells = all_pos(pix, 14)
    # Group into clusters
    from collections import deque
    unassigned = set(e_cells)
    clusters = []
    while unassigned:
        seed = next(iter(unassigned))
        cluster = {seed}
        unassigned.discard(seed)
        q = deque([seed])
        while q:
            cx, cy = q.popleft()
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (1, -1), (-1, 1)]:
                nb = (cx + dx, cy + dy)
                if nb in unassigned:
                    unassigned.discard(nb)
                    cluster.add(nb)
                    q.append(nb)
        clusters.append(cluster)
    print(f'--- {label} ---')
    print(f'  e-clusters: {[(min(x for x,y in c), min(y for x,y in c), len(c)) for c in clusters]}')
    # Click center of each cluster
    for cluster in clusters:
        xs = [x for x, y in cluster]
        ys = [y for x, y in cluster]
        cx, cy = sum(xs) // len(xs), sum(ys) // len(ys)
        g_restore(g, base)
        g.click(cx, cy)
        pix_sel = g.pixels()
        red_cells = np.where(pix_sel == 2)
        n_red = len(red_cells[0])
        # Find red cluster centers
        from collections import defaultdict as dd
        red_set = set(zip(red_cells[1].tolist(), red_cells[0].tolist()))
        red_unassigned = set(red_set)
        red_clusters = []
        while red_unassigned:
            seed = next(iter(red_unassigned))
            c = {seed}
            red_unassigned.discard(seed)
            q = deque([seed])
            while q:
                a, b = q.popleft()
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        nb = (a + dx, b + dy)
                        if nb in red_unassigned:
                            red_unassigned.discard(nb)
                            c.add(nb)
                            q.append(nb)
            if c:
                rxs = [x for x, y in c]
                rys = [y for x, y in c]
                red_clusters.append((sum(rxs)//len(rxs), sum(rys)//len(rys), len(c)))
        print(f'    click({cx},{cy}): red-cells={n_red} red-clusters={red_clusters}')
    g_restore(g, base)


def main():
    g = LF52(up_to_level=4, verbose=False)
    # Full 15-action sequence
    apply_seq(g, [
        ('C',(13,25),(25,25)),
        ('C',(25,25),(37,25)),
        ('A',3),
        ('C',(37,25),(49,25)),
        ('A',4),('A',4),('A',4),('A',4),
        ('C',(19,25),(31,25)),
        ('C',(31,25),(31,37)),
        ('C',(31,37),(31,49)),
        ('C',(49,25),(49,37)),
        ('C',(49,37),(49,49)),
        ('C',(49,49),(37,49)),
        ('C',(37,49),(25,49)),
    ])
    print('=== State after 15 actions ===')
    sm = sprite_map(g)
    print(f'pieces: {sorted(sm['fozwvlovdui'])}')
    print(f'vehicles hupkpseyuim: {sm['hupkpseyuim']}')
    print(f'vehicles hupkpseyuim2: {sm['hupkpseyuim2']}')

    render_png(g.pixels(), label='post15').save('/tmp/lf52_frames/L4_post15.png')

    # Try A3, A4 to scroll and see what's clickable
    base = g_snap(g)
    for seq_name, a_seq in [
        ('+0', []),
        ('A3', [3]),
        ('A3x2', [3, 3]),
        ('A3x3', [3, 3, 3]),
        ('A3x4', [3, 3, 3, 3]),
        ('A4', [4]),
        ('A4x2', [4, 4]),
    ]:
        g_restore(g, base)
        for a in a_seq:
            g.action(a)
        sm = sprite_map(g)
        print(f'\n{seq_name}: pieces world={sorted(sm['fozwvlovdui'])}')
        enumerate_clicks(g, seq_name)

if __name__ == '__main__':
    main()
