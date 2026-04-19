"""LF52 L4 exploration probe.

Goal: find the win condition. Mechanics are mapped but piece-reduction is blocked.
Test various post-unload strategies, geometric placements, multi-load cycles.
"""
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
from lf52_tool import LF52, render_png


def full_ascii(pix, ymin=0, ymax=64, xmin=0, xmax=64):
    """Full color-number ascii grid over a region."""
    lines = []
    header = '    ' + ''.join(f'{x%10}' for x in range(xmin, xmax))
    lines.append(header)
    hundreds = '    ' + ''.join(f'{x//10}' for x in range(xmin, xmax))
    lines.append(hundreds)
    for y in range(ymin, ymax):
        row = ''
        for x in range(xmin, xmax):
            v = int(pix[y, x])
            if v == 0:
                row += '.'
            elif v == 14:
                row += 'e'
            elif v == 15:
                row += 'f'
            elif v == 7:
                row += '7'
            elif v == 11:
                row += 'b'
            elif v == 12:
                row += 'c'
            elif v == 9:
                row += '|'
            elif v == 2:
                row += 'R'   # red hint
            elif v == 3:
                row += 'G'   # green select
            elif v == 4:
                row += 'Y'   # yellow border
            elif v == 5:
                row += '#'
            else:
                row += str(v)
        lines.append(f'{y:3d} {row}')
    return '\n'.join(lines)


def dump(g, label):
    pix = g.pixels()
    print(f'\n=== {label} ===')
    print(f'lvl={g.level()}, state={g.state_name()}')
    counts = {}
    for v in range(16):
        c = int((pix == v).sum())
        if c > 0:
            counts[v] = c
    print(f'colors: {counts}')
    return pix


def click_and_show_hints(g, x, y, title=''):
    """Click at (x,y) and show what hints appear."""
    snap = copy.deepcopy(g.env._game)
    g.click(x, y)
    pix = g.pixels()
    red = list(zip(*np.where(pix == 2)))  # (y, x) tuples
    green = list(zip(*np.where(pix == 3)))
    yellow = list(zip(*np.where(pix == 4)))
    print(f'{title} click({x},{y}): green={len(green)} yellow={len(yellow)} red={len(red)}', end='')
    if red:
        rys = sorted(set(y for y, x in red))
        rxs = sorted(set(x for y, x in red))
        print(f' red-at y={rys[:5]}{"..." if len(rys)>5 else ""} x={rxs[:5]}{"..." if len(rxs)>5 else ""}')
        # Cluster red cells: group by (y//4, x//4)
        clusters = {}
        for y, x in red:
            key = (y // 6 * 6, x // 6 * 6)
            clusters.setdefault(key, []).append((x, y))
        print(f'  red clusters ({len(clusters)}):')
        for key, cells in sorted(clusters.items()):
            xs = [x for x, y in cells]
            ys = [y for x, y in cells]
            print(f'    center ~({sum(xs)//len(xs)},{sum(ys)//len(ys)}): {len(cells)} cells, bbox x={min(xs)}-{max(xs)} y={min(ys)}-{max(ys)}')
    else:
        print()
    # Restore
    g.env._game = snap
    g.obs = None
    g._cached_frame = None


def main():
    g = LF52(up_to_level=4)
    dump(g, 'L4 init')

    # Render L4 init with full detail
    pix = g.pixels()
    render_png(pix, label='L4 init').save('/tmp/lf52_frames/L4_00_init.png')
    print(full_ascii(pix, ymin=15, ymax=36, xmin=0, xmax=64))

    # Show 7-cells location
    ys7, xs7 = np.where(pix == 7)
    print(f'\n7-cells: {list(zip(xs7.tolist(), ys7.tolist()))}')

    # === Test 1: what does clicking each e-piece from init reveal? ===
    print('\n--- TEST 1: click each e-piece from init ---')
    # Main row B tile 1 (cols 12-15, rows 24-27): center at (13,25)
    click_and_show_hints(g, 13, 25, 'main-tile-1 (B)')
    click_and_show_hints(g, 14, 25, 'main-tile-1 alt')
    # Main row B tile 6 (cols 42-45, rows 24-27)
    click_and_show_hints(g, 43, 25, 'main-tile-6 (B)')
    click_and_show_hints(g, 44, 25, 'main-tile-6 alt')
    # Sub panel tile
    click_and_show_hints(g, 37, 61, 'sub-panel')


if __name__ == '__main__':
    main()
