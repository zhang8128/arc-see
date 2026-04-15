"""Interactive L5 play with correct coord handling.

Click = world_pixel + panel_offset. Panel offset changes on L5 with loaded-vehicle moves.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

from lf52_tool import LF52, render_png
from arcengine import GameAction
import numpy as np
import copy


def setup_l5():
    g = LF52(up_to_level=1, verbose=False)
    g.env._game.set_level(4)
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    return g

def panel_offset(g):
    return tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)

def click_grid(g, gx, gy):
    """Click grid cell (gx, gy) accounting for panel offset."""
    ox, oy = panel_offset(g)
    # Click center of cell (3 pixels into a 6x6 tile)
    x = gx * 6 + 3 + ox
    y = gy * 6 + 3 + oy
    return g.env.step(GameAction.ACTION6, data={'x': x, 'y': y})

def do_chain(g, src_grid, direction):
    """Execute chain: click source, then click destination (2 cells in direction)."""
    sx, sy = src_grid
    dx, dy = direction
    dest = (sx + 2*dx, sy + 2*dy)
    click_grid(g, sx, sy)
    click_grid(g, dest[0], dest[1])

def do_a(g, a):
    return g.env.step(getattr(GameAction, f'ACTION{a}'))

def foz_count(g):
    return sum(1 for item in g.env._game.ikhhdzfmarl._sorted_cache if getattr(item[1], 'name', '') == 'fozwvlovdui')

def piece_positions(g):
    return sorted([(item[1].grid_x, item[1].grid_y) for item in g.env._game.ikhhdzfmarl._sorted_cache if getattr(item[1], 'name', '') == 'fozwvlovdui'])

def vehicle_positions(g):
    return sorted([(item[1].grid_x, item[1].grid_y) for item in g.env._game.ikhhdzfmarl._sorted_cache if getattr(item[1], 'name', '') == 'hupkpseyuim2'])

def pivot_positions(g):
    return sorted([(item[1].grid_x, item[1].grid_y) for item in g.env._game.ikhhdzfmarl._sorted_cache if getattr(item[1], 'name', '') == 'dgxfozncuiz'])

def sprites_at(g, x, y):
    return [s.name for s in g.env._game.ikhhdzfmarl.hncnfaqaddg.ijpoqzvnjt(x, y)]

def chain_valid(g, piece_grid, direction):
    px, py = piece_grid
    dx, dy = direction
    pivot = (px + dx, py + dy)
    dest = (px + 2*dx, py + 2*dy)
    if not (0 <= pivot[0] < 22 and 0 <= pivot[1] < 10):
        return False
    if not (0 <= dest[0] < 22 and 0 <= dest[1] < 10):
        return False
    p_sprites = sprites_at(g, *pivot)
    d_sprites = sprites_at(g, *dest)
    pivot_ok = any('fozwvlovdui' in s or 'dgxfozncuiz' in s for s in p_sprites)
    dest_ok = (len(d_sprites) == 1 and 'hupkpseyuim' in d_sprites[0]) or (len(d_sprites) == 2 and 'hupkpseyuim2' in d_sprites)
    return pivot_ok and dest_ok

def list_chains(g):
    result = []
    for px, py in piece_positions(g):
        for dx, dy, name in [(0, -1, 'UP'), (0, 1, 'DOWN'), (-1, 0, 'L'), (1, 0, 'R')]:
            if chain_valid(g, (px, py), (dx, dy)):
                dest = (px + 2*dx, py + 2*dy)
                pivot = (px + dx, py + dy)
                pivot_sprites = sprites_at(g, *pivot)
                consume = '*' if any('fozwvlovdui' in s for s in pivot_sprites) else ' '
                result.append(f'  ({px},{py}) {name}→({dest[0]},{dest[1]}) via {pivot}{consume}')
    return result

def print_state(g, label=''):
    foz = foz_count(g)
    print(f'\n=== {label} (foz={foz}) ===')
    print(f'  pieces: {piece_positions(g)}')
    print(f'  vehicles: {vehicle_positions(g)}')
    print(f'  pivots: {pivot_positions(g)}')
    print(f'  panel_offset: {panel_offset(g)}')
    chains = list_chains(g)
    if chains:
        print(f'  chains available:')
        for c in chains[:20]:
            print(c)

def main():
    g = setup_l5()
    print_state(g, 'INIT')

    # Step 1: Chain (1, 3) RIGHT to (3, 3) via f-pivot (2, 3)
    do_chain(g, (1, 3), (1, 0))
    print_state(g, 'After step 1: (1,3) → (3,3)')

    # Step 2: Explore more chain options now that piece is at (3, 3)
    # Also see where vehicles can go
    print('\n--- Next moves possible ---')
    snap = copy.deepcopy(g.env._game)
    for a in [1, 2, 3, 4]:
        g.env._game = copy.deepcopy(snap)
        try:
            do_a(g, a)
            vp = vehicle_positions(g)
            pp = piece_positions(g)
            print(f'  A{a}: vehicles={vp}, pieces={pp}')
        except Exception as e:
            print(f'  A{a}: err {e}')
    g.env._game = copy.deepcopy(snap)


if __name__ == '__main__':
    main()
