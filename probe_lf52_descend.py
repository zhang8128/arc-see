"""Test: can we bring a piece to vehicle 2 via descend + horizontal?"""
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


def find_hints(g, cx, cy):
    """Click (cx, cy), find red hints (center + size). Returns list of (rx, ry, size)."""
    base_snap = g_snap(g)
    g.click(cx, cy)
    pix = g.pixels()
    red = centers(all_pos(pix, 2), max_dist=2)
    g_restore(g, base_snap)
    return red


def try_move(g, cx, cy, rx, ry):
    """Click (cx, cy) then (rx, ry). Return before/after state."""
    s_before = sstate(g)
    g.click(cx, cy)
    g.click(rx, ry)
    s_after = sstate(g)
    return s_before, s_after


def enumerate_moves(g):
    """Enumerate all (src, dst) click pairs. Uses centers."""
    pix = g.pixels()
    e_centers = centers(all_pos(pix, 14))
    moves = []
    for cx, cy, sz in e_centers:
        hints = find_hints(g, cx, cy)
        for rx, ry, _ in hints:
            moves.append(((cx, cy), (rx, ry)))
    # Also A-actions
    for a in [1, 2, 3, 4]:
        moves.append(('A', a))
    return moves


def main():
    g = LF52(up_to_level=4, verbose=False)
    apply_seq(g, [
        ('C', (13, 25), (25, 25)),
        ('C', (25, 25), (37, 25)),
        ('A', 3),
        ('C', (37, 25), (49, 25)),
        ('A', 4), ('A', 4), ('A', 4), ('A', 4),
    ])
    # Unload main vehicle to (49, 37)
    g.click(49, 25)
    g.click(49, 37)

    # Now descend (49, 37) → (49, 49)
    print('=== After unload to (49, 37), try descend ===')
    hints = find_hints(g, 49, 37)
    print(f'hints at (49, 37): {hints}')

    # Execute jump to (49, 49)
    g.click(49, 37)
    g.click(49, 49)
    print(f'state after jump to (49, 49): {sstate(g)}')
    render_png(g.pixels(), label='descend').save('/tmp/lf52_frames/L4_descend.png')

    # What hints does (49, 49) produce?
    hints = find_hints(g, 49, 49)
    print(f'hints at (49, 49): {hints}')

    # Try (19, 25) → (31, 25) chain first, then descend (31, 25) and (49, 25)
    print('\n=== Alt: step-9 chain first, then descend both pieces ===')
    g2 = LF52(up_to_level=4, verbose=False)
    apply_seq(g2, [
        ('C', (13, 25), (25, 25)),
        ('C', (25, 25), (37, 25)),
        ('A', 3),
        ('C', (37, 25), (49, 25)),
        ('A', 4), ('A', 4), ('A', 4), ('A', 4),
        ('C', (19, 25), (31, 25)),  # chain to (31, 25)
    ])
    print(f'after chain: {sstate(g2)}')
    # Try (31, 25) → (31, 37)
    hints = find_hints(g2, 31, 25)
    print(f'hints at (31, 25): {hints}')
    hints = find_hints(g2, 49, 25)
    print(f'hints at (49, 25): {hints}')

    # Execute descent
    snap_2piece = g_snap(g2)
    g2.click(31, 25); g2.click(31, 37)
    g2.click(49, 25); g2.click(49, 37)
    print(f'after both descend: {sstate(g2)}')

    # Now continue down
    hints = find_hints(g2, 31, 37)
    print(f'hints at (31, 37): {hints}')
    hints = find_hints(g2, 49, 37)
    print(f'hints at (49, 37): {hints}')

    # Full descent
    g2.click(31, 37); g2.click(31, 49)
    g2.click(49, 37); g2.click(49, 49)
    print(f'after to row 49: {sstate(g2)}')
    render_png(g2.pixels(), label='row49').save('/tmp/lf52_frames/L4_row49_2piece.png')

    # From (31, 49) and (49, 49), explore
    hints1 = find_hints(g2, 31, 49)
    hints2 = find_hints(g2, 49, 49)
    print(f'hints at (31, 49): {hints1}')
    print(f'hints at (49, 49): {hints2}')

    # Try chain (49, 49) -> (31, 49) or vice versa? Or further
    # Check if vehicle 2 can be loaded
    print('\n--- Try loading vehicle 2 ---')
    snap_row49 = g_snap(g2)
    # Vehicle 2 is at (25, 49). Pieces at (31, 49), (49, 49).
    # Chain (49, 49) over (31, 49) pivot would land at (13, 49) — over/past vehicle 2
    g_restore(g2, snap_row49)
    hints = find_hints(g2, 49, 49)
    print(f'full hints at (49, 49): {hints}')

    # Also try driving vehicle 2 into position first (before descending)
    print('\n--- Try: chain first, drive vehicle 2 right via A4, then descend ---')
    g3 = LF52(up_to_level=4, verbose=False)
    apply_seq(g3, [
        ('C', (13, 25), (25, 25)),
        ('C', (25, 25), (37, 25)),
        ('A', 3),
        ('C', (37, 25), (49, 25)),
        ('A', 4), ('A', 4), ('A', 4), ('A', 4),
        ('C', (19, 25), (31, 25)),
    ])
    # Try each combo of A3/A4 before descent
    snap_2p = g_snap(g3)
    for seq_name, a_seq in [('+0', []), ('A3', [3]), ('A3x2', [3, 3]), ('A3x3', [3, 3, 3]),
                             ('A4', [4]), ('A4x2', [4, 4])]:
        g_restore(g3, snap_2p)
        for a in a_seq:
            g3.action(a)
        pix = g3.pixels()
        e = centers(all_pos(pix, 14))
        b = centers(all_pos(pix, 11))
        print(f'  {seq_name}: e={e} b={b}')


if __name__ == '__main__':
    main()
