"""Exhaustively click every (x, y) position in the viewport at various states.
Find ANY position that produces green selection or red hint, not just e-pieces."""
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


def apply_seq(g, seq):
    for step in seq:
        if step[0] == 'C':
            g.click(*step[1]); g.click(*step[2])
        else:
            g.action(step[1])


def exhaustive_clicks(g, label, sample_step=2):
    """Click every sample_step-th cell in viewport, report hits with non-empty hints."""
    pix_before = g.pixels()
    base = g_snap(g)
    hits = []
    for cy in range(0, 64, sample_step):
        for cx in range(0, 64, sample_step):
            g_restore(g, base)
            try:
                g.click(cx, cy)
            except Exception:
                continue
            pix_after = g.pixels()
            red = find_red_clusters(pix_after)
            if red:
                hits.append((cx, cy, [(cc(rc), len(rc)) for rc in red]))
    g_restore(g, base)
    print(f'=== {label}: {len(hits)} clickable positions ===', flush=True)
    # Group by red-cluster signature to dedupe
    by_sig = defaultdict(list)
    for cx, cy, red in hits:
        sig = tuple(red)
        by_sig[sig].append((cx, cy))
    for sig, positions in by_sig.items():
        cxs = [p[0] for p in positions]
        cys = [p[1] for p in positions]
        print(f'  red={sig}: {len(positions)} positions, bbox x={min(cxs)}-{max(cxs)} y={min(cys)}-{max(cys)}', flush=True)
    return hits


def main():
    states = [
        ('init', []),
        ('A3x4+A2x2', [('A',3)]*4 + [('A',2)]*2),
        ('opener', [('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25)),
                    ('A',4),('A',4),('A',4),('A',4),('C',(19,25),(31,25))]),
        ('opener+A3x4+A2x2', [('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25)),
                               ('A',4),('A',4),('A',4),('A',4),('C',(19,25),(31,25)),
                               ('A',3),('A',3),('A',3),('A',3),
                               ('A',2),('A',2)]),
        ('post15', [('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25)),
                    ('A',4),('A',4),('A',4),('A',4),
                    ('C',(19,25),(31,25)),('C',(31,25),(31,37)),('C',(31,37),(31,49)),
                    ('C',(49,25),(49,37)),('C',(49,37),(49,49)),
                    ('C',(49,49),(37,49)),('C',(37,49),(25,49))]),
        ('post15+A3x4+A2x2', [('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25)),
                               ('A',4),('A',4),('A',4),('A',4),
                               ('C',(19,25),(31,25)),('C',(31,25),(31,37)),('C',(31,37),(31,49)),
                               ('C',(49,25),(49,37)),('C',(49,37),(49,49)),
                               ('C',(49,49),(37,49)),('C',(37,49),(25,49)),
                               ('A',3),('A',3),('A',3),('A',3),
                               ('A',2),('A',2)]),
        ('A3x4+A2x2+A4x4', [('A',3)]*4 + [('A',2)]*2 + [('A',4)]*4),
    ]
    g = LF52(up_to_level=4, verbose=False)
    for label, seq in states:
        g = LF52(up_to_level=4, verbose=False)  # fresh env each time to avoid state issues
        try:
            apply_seq(g, seq)
        except Exception as e:
            print(f'{label}: seq failed: {e}', flush=True)
            continue
        exhaustive_clicks(g, label)


if __name__ == '__main__':
    main()
