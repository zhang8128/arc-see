"""Find how to load the h2 vehicle at (42, 66).
This vehicle is aligned with pieces at (30, 54), (30, 78) — maybe THE way to reach them.
"""
import copy, sys
from pathlib import Path
from collections import defaultdict, deque
sys.path.insert(0, str(Path(__file__).parent))
import numpy as np
from lf52_tool import LF52, render_png


def sprite_map(g):
    d = defaultdict(list)
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        d[getattr(sp, 'name', '')].append((sp.x, sp.y))
    return d


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


def cluster_center(c):
    xs = [x for x, y in c]
    ys = [y for x, y in c]
    return (sum(xs)//len(xs), sum(ys)//len(ys))


def piece_count(g):
    return sum(1 for item in g.env._game.ikhhdzfmarl._sorted_cache
               if getattr(item[1], 'name', '') == 'fozwvlovdui')


def enumerate_clicks(g):
    pix = g.pixels()
    ys, xs = np.where(pix == 14)
    unassigned = set(zip(xs.tolist(), ys.tolist()))
    clusters = []
    while unassigned:
        seed = next(iter(unassigned))
        c = {seed}
        unassigned.discard(seed)
        q = deque([seed])
        while q:
            a, b = q.popleft()
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nb = (a+dx, b+dy)
                if nb in unassigned:
                    unassigned.discard(nb)
                    c.add(nb)
                    q.append(nb)
        clusters.append(c)
    base = g_snap(g)
    out = []
    for c in clusters:
        cx, cy = cluster_center(c)
        g_restore(g, base)
        g.click(cx, cy)
        red_clusters = find_red_clusters(g.pixels())
        for rc in red_clusters:
            rx, ry = cluster_center(rc)
            out.append((cx, cy, rx, ry))
    g_restore(g, base)
    return out


def main():
    # From INIT (before any moves)
    g = LF52(up_to_level=4, verbose=False)
    init_snap = g_snap(g)
    sm = sprite_map(g)
    print(f'INIT: foz={sorted(sm["fozwvlovdui"])}')
    print(f'     h2={sorted(sm["hupkpseyuim2"])}')
    print(f'     h1={sorted(sm["hupkpseyuim"])}')

    # Try A3, then various A1/A2 + A3/A4 to drive the h2@(42,66) vehicle
    # Key insight: at init, h2 is at (42, 66). Piece at (30, 78) is BELOW
    # Piece at (30, 54) is ABOVE
    print('\n=== Test A-actions from INIT to move h2@(42,66) ===')
    for name, aseq in [
        ('', []),
        ('A1', [1]),
        ('A2', [2]),
        ('A3', [3]),
        ('A4', [4]),
        ('A3A1', [3, 1]),
        ('A3A2', [3, 2]),
        ('A4A1', [4, 1]),
        ('A4A2', [4, 2]),
        ('A1A3', [1, 3]),
        ('A2A3', [2, 3]),
    ]:
        g_restore(g, init_snap)
        try:
            for a in aseq:
                g.action(a)
            sm2 = sprite_map(g)
            h2_diff = set(sm2['hupkpseyuim2']) - set(sm['hupkpseyuim2'])
            h1_diff = set(sm2['hupkpseyuim']) - set(sm['hupkpseyuim'])
            print(f'{name:10s}: h2-changed={h2_diff or "(no change)"} h1-changed={h1_diff or "(no change)"}')
        except Exception as e:
            print(f'{name}: ERROR {e}')

    # Try clicking pieces at init to see what hints appear
    print('\n=== From INIT, click each piece ===')
    g_restore(g, init_snap)
    clicks = enumerate_clicks(g)
    print(f'Click hints from init: {clicks}')

    # Render init to visualize world
    g_restore(g, init_snap)
    render_png(g.pixels(), label='L4 init').save('/tmp/lf52_frames/L4_init_study.png')

    # Try clicking sub-panel piece at (37, 61)
    print('\n=== Click various spots to check what is clickable ===')
    for cx, cy, label in [(37, 61, 'sub-piece'),
                          (13, 25, 'piece1'),
                          (43, 25, 'piece6'),
                          (14, 25, 'p1-alt'),
                          (36, 60, 'sub-tl'),
                          (39, 63, 'sub-br')]:
        g_restore(g, init_snap)
        g.click(cx, cy)
        pix = g.pixels()
        nr = int((pix == 2).sum())
        ng = int((pix == 3).sum())
        if nr or ng:
            red_clusters = find_red_clusters(pix)
            print(f'  click({cx},{cy}) [{label}]: green={ng} red={nr} red-clusters={[cluster_center(rc) for rc in red_clusters]}')
        else:
            print(f'  click({cx},{cy}) [{label}]: no hints')


if __name__ == '__main__':
    main()
