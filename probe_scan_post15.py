"""Scan post-15 + various A-actions for multiple hint signatures."""
import copy, sys
from pathlib import Path
from collections import defaultdict, deque
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from lf52_tool import LF52


def sm(g):
    d = defaultdict(list)
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        d[getattr(sp, 'name', '')].append((sp.x, sp.y))
    return dict(d)


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
    xs = [x for x, y in c]; ys = [y for x, y in c]
    return (sum(xs)//len(xs), sum(ys)//len(ys))


def main():
    base_seq = [
        ('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25)),
        ('A',4),('A',4),('A',4),('A',4),
        ('C',(19,25),(31,25)),('C',(31,25),(31,37)),('C',(31,37),(31,49)),
        ('C',(49,25),(49,37)),('C',(49,37),(49,49)),
        ('C',(49,49),(37,49)),('C',(37,49),(25,49)),
    ]
    for n3 in range(0, 5):
        for n4 in range(0, 5):
            for n2 in range(0, 3):
                g = LF52(up_to_level=4, verbose=False)
                for step in base_seq:
                    if step[0] == 'C':
                        g.click(*step[1]); g.click(*step[2])
                    else:
                        g.action(step[1])
                try:
                    for _ in range(n3): g.action(3)
                    for _ in range(n4): g.action(4)
                    for _ in range(n2): g.action(2)
                except Exception:
                    continue
                sm_cur = sm(g)
                base = (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))
                hints = set()
                for cy in range(0, 64, 3):
                    for cx in range(0, 64, 3):
                        g.env._game = copy.deepcopy(base[0])
                        g.obs = copy.deepcopy(base[1])
                        g._cached_frame = None
                        try:
                            g.click(cx, cy)
                        except Exception:
                            continue
                        pa = g.pixels()
                        red = find_red_clusters(pa)
                        if red:
                            rsig = tuple(sorted([(cc(r), len(r)) for r in red]))
                            hints.add(rsig)
                if hints:
                    h2_status = sorted(sm_cur['hupkpseyuim2'])
                    foz_status = sorted(sm_cur['fozwvlovdui'])
                    print(f'post15+A3x{n3}+A4x{n4}+A2x{n2}: foz={foz_status} h2={h2_status} hints={len(hints)}', flush=True)
                    for h in hints:
                        print(f'  {h}', flush=True)


if __name__ == '__main__':
    main()
