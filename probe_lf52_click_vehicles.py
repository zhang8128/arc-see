"""Click on VEHICLE interiors (b/c cells) at various states.
Maybe clicking an empty vehicle loads it from adjacent pieces."""
import copy, sys
from pathlib import Path
from collections import defaultdict, deque
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from lf52_tool import LF52


def g_snap(g):
    return (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))


def g_restore(g, snap):
    g.env._game = copy.deepcopy(snap[0])
    g.obs = copy.deepcopy(snap[1])
    g._cached_frame = None


def piece_count(g):
    return sum(1 for item in g.env._game.ikhhdzfmarl._sorted_cache
               if getattr(item[1], 'name', '') == 'fozwvlovdui')


def find_red_clusters(pix):
    ys, xs = np.where(pix == 2)
    unassigned = set(zip(xs.tolist(), ys.tolist()))
    clusters = []
    while unassigned:
        seed = next(iter(unassigned))
        c = {seed}
        unassigned.discard(seed)
        q = deque([seed])
        while q:
            a, b = q.popleft()
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    if dx == 0 and dy == 0: continue
                    nb = (a+dx, b+dy)
                    if nb in unassigned:
                        unassigned.discard(nb)
                        c.add(nb)
                        q.append(nb)
        clusters.append(c)
    return clusters


def cc(c):
    xs=[x for x,y in c]; ys=[y for x,y in c]
    return (sum(xs)//len(xs), sum(ys)//len(ys))


def apply_seq(g, seq):
    for step in seq:
        if step[0] == 'C':
            g.click(*step[1]); g.click(*step[2])
        else:
            g.action(step[1])


def probe_all_vehicle_cells(g, label):
    """Click on b (color 11) and c (color 12) cells to find vehicle interactions."""
    pix = g.pixels()
    b_cells = np.where(pix == 11)
    c_cells = np.where(pix == 12)
    all_cells = list(zip(b_cells[1].tolist(), b_cells[0].tolist())) + list(zip(c_cells[1].tolist(), c_cells[0].tolist()))
    # Dedupe
    all_cells = list(set(all_cells))
    print(f'--- {label}: {len(all_cells)} vehicle cells ---', flush=True)
    base = g_snap(g)
    hits = []
    for cx, cy in all_cells:
        g_restore(g, base)
        try:
            g.click(cx, cy)
        except Exception:
            continue
        pix_after = g.pixels()
        red = find_red_clusters(pix_after)
        if red:
            hits.append((cx, cy, [(cc(r), len(r)) for r in red]))
            print(f'  click({cx},{cy}): red={[(cc(r), len(r)) for r in red]}', flush=True)
    print(f'  total: {len(hits)} vehicle clicks with hints', flush=True)


def main():
    states = [
        ('init', []),
        ('A3x4+A2x2', [('A',3)]*4 + [('A',2)]*2),
        ('just-loaded', [('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25))]),
        ('load+A3x4', [('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25))] + [('A',3)]*4),
        ('load+A3x4+A2x2', [('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25))] + [('A',3)]*4 + [('A',2)]*2),
        ('load+A4x4', [('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25))] + [('A',4)]*4),
    ]
    for label, seq in states:
        g = LF52(up_to_level=4, verbose=False)
        try:
            apply_seq(g, seq)
        except Exception as e:
            print(f'{label}: ERR {e}', flush=True)
            continue
        probe_all_vehicle_cells(g, label)


if __name__ == '__main__':
    main()
