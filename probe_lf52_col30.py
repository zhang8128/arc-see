"""Test: can we load h2@(48, 66) by positioning it at (30, 66) via A3×3,
then chain piece at (30, 54) or (30, 78) into it?"""
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
    # Execute opener, then try different A3 counts to align h2@(48,66) under/above col-30 pieces
    g = LF52(up_to_level=4, verbose=False)
    for step in [('C',(13,25),(25,25)),('C',(25,25),(37,25)),('A',3),('C',(37,25),(49,25)),
                 ('A',4),('A',4),('A',4),('A',4),('C',(19,25),(31,25))]:
        if step[0]=='C': g.click(*step[1]); g.click(*step[2])
        else: g.action(step[1])

    sm = sprite_map(g)
    print(f'After 9-action opener: foz={sorted(sm["fozwvlovdui"])}')
    print(f'                       h2={sorted(sm["hupkpseyuim2"])}')
    base = g_snap(g)

    # h2 currently at... let me see. After A3 + A4x4 = net +3 for h2 maybe?
    # Init h2=(48,18),(48,66),(72,42). After 1 A3: h2=(42,18),(42,66),(66,42). After 4 A4: each A4 +6 in x
    # Net: h2=(48,18)+(-6+24)=((66,18), etc

    # From opener state, drive h2 by additional A3/A4
    # Try aligning h2@(66,18) or similar with col-30 pieces — not possible, they're at col 30
    # Well actually hupkpseyuim2 was at init at (48, 66). To align with col 30, need A3×3.
    # With opener we did A3×1 + A4×4 = net +3 in x (one A3 back -6, four A4 forward +6×4=+24 → net +18)
    # So h2@(48,66) → (48+18, 66) = (66, 66). To reach col 30 we need A3 more.

    print('\n=== Test A3 from opener state ===')
    for n in range(1, 8):
        g_restore(g, base)
        for _ in range(n):
            g.action(3)
        sm2 = sprite_map(g)
        print(f'  A3x{n}: h2={sorted(sm2["hupkpseyuim2"])}')
        # Also check if pieces are clickable now
        clicks = enumerate_clicks(g)
        if clicks:
            print(f'    clicks: {clicks}')

    # Also from INIT directly, no opener — try A3x3 first to position h2@(48,66) at col 30
    print('\n=== From INIT, A3x3 first ===')
    g = LF52(up_to_level=4, verbose=False)
    for _ in range(3): g.action(3)
    sm = sprite_map(g)
    print(f'  A3x3 only: h2={sorted(sm["hupkpseyuim2"])}')
    clicks = enumerate_clicks(g)
    print(f'  clicks: {clicks}')

    # try A3x3 then click (30, 54) piece
    print('\n=== After A3x3, try clicking col-30 pieces in viewport ===')
    # Need to check what's in viewport
    pix = g.pixels()
    ys, xs = np.where(pix == 14)
    e_positions = sorted(set(zip(xs.tolist(), ys.tolist())))
    print(f'  e positions in viewport: {e_positions[:20]}')

    # Render
    render_png(pix, label='A3x3').save('/tmp/lf52_frames/L4_A3x3.png')


if __name__ == '__main__':
    main()
