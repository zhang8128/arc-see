"""Focus on sub-panel piece clickability. Try many pre-sequences ending with different vehicle configs."""
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
    # After the opener (9 actions), state: 4 pieces. Let's see if we can load h2@(54, 66) via some path.
    # Opener: [A3, merge1, merge2, load, A4x4, chain-merge] - 9 actions
    # After opener: h2 at [(54, 66), (66, 18), (72, 42)]
    # h2@(54, 66) is at row 66. Adjacent to piece at (30, 78)? No, distance 24+24 too far.
    # But maybe we can drive h2@(54, 66) via A3 to col 30 (need 4 A3s more)

    OPENER = [('A',3),('C',(13,25),(25,25)),('C',(25,25),(37,25)),('C',(37,25),(49,25)),
              ('A',4),('A',4),('A',4),('A',4),('C',(19,25),(31,25))]

    g = LF52(up_to_level=4, verbose=False)
    for step in OPENER:
        if step[0] == 'C': g.click(*step[1]); g.click(*step[2])
        else: g.action(step[1])
    opener_snap = (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))
    print(f'Opener: foz={sorted(sm(g)["fozwvlovdui"])} h2={sorted(sm(g)["hupkpseyuim2"])}', flush=True)

    # Try each A3×n after opener
    for n3 in range(0, 8):
        g.env._game = copy.deepcopy(opener_snap[0])
        g.obs = copy.deepcopy(opener_snap[1])
        g._cached_frame = None
        try:
            for _ in range(n3): g.action(3)
        except Exception:
            continue
        sm_cur = sm(g)
        h2_pos = sorted(sm_cur['hupkpseyuim2'])
        # Enumerate clicks
        pix = g.pixels()
        base = (copy.deepcopy(g.env._game), copy.deepcopy(g.obs))
        hints = set()
        for cy in range(0, 64, 2):
            for cx in range(0, 64, 2):
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
        print(f'opener+A3x{n3}: h2={h2_pos} hints-unique={len(hints)}', flush=True)
        for h in hints:
            print(f'  {h}', flush=True)


if __name__ == '__main__':
    main()
