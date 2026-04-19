"""Test: can piece (0, 1) chain DOWN to (0, 3) which is a track cell?"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')

import copy, hashlib
import numpy as np
from lf52_tool import LF52
from arcengine import GameAction
import solution_lf52_l5 as L5
import solution_lf52_l6 as L6


def setup_l7(g):
    g.env._game.set_level(4)
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
    for step in L5.SOLUTION:
        if isinstance(step, str):
            g.env.step(getattr(GameAction, f'ACTION{int(step[1:])}'))
        else:
            kind, src, direction = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            sx, sy = src; dx, dy = direction
            g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})
    for step in L6.parse_solution():
        if step[0] == 'A':
            g.env.step(getattr(GameAction, f'ACTION{step[1]}'))
        else:
            _, (sx, sy), (dx, dy) = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})


def state_hash(g):
    sprites = []
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        s = item[1]
        nm = getattr(s, 'name', '')
        if not nm:
            continue
        x, y = getattr(s, 'x', -999), getattr(s, 'y', -999)
        sprites.append((nm, x, y))
    sprites.sort()
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    return hashlib.md5(repr((sprites, ox, oy)).encode()).hexdigest()[:10]


def foz_count(g):
    return sum(1 for item in g.env._game.ikhhdzfmarl._sorted_cache
               if getattr(item[1], 'name', '').startswith('fozwvlovdui'))


def piece_positions(g):
    pos = []
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        s = item[1]
        nm = getattr(s, 'name', '')
        if nm.startswith('fozwvlovdui'):
            x, y = getattr(s, 'x', -1), getattr(s, 'y', -1)
            pos.append((nm, x // 6, y // 6))
    return sorted(pos)


def try_chain(g, src_tile, dst_tile, label=""):
    """Try a 2-click chain from src to dst, both in TILE coords."""
    ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    sx, sy = src_tile
    dx_, dy_ = dst_tile
    snap = copy.deepcopy(g.env._game)

    h_before = state_hash(g)
    foz_before = foz_count(g)
    pieces_before = piece_positions(g)

    # Click source
    obs1 = g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
    h_mid = state_hash(g)

    # Click dest
    ox2, oy2 = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    obs2 = g.env.step(GameAction.ACTION6, data={'x': dx_*6+3+ox2, 'y': dy_*6+3+oy2})
    h_after = state_hash(g)
    foz_after = foz_count(g)
    pieces_after = piece_positions(g)

    print(f"\n=== {label}: chain {src_tile} → {dst_tile} ===")
    print(f"  hash before={h_before} mid={h_mid} after={h_after}")
    print(f"  foz {foz_before} → {foz_after}")
    print(f"  pieces before: {pieces_before}")
    print(f"  pieces after:  {pieces_after}")

    # Restore state
    g.env._game = copy.deepcopy(snap)


def main():
    g = LF52(up_to_level=1, verbose=False)
    setup_l7(g)
    print(f"L7 init: pieces={piece_positions(g)}")
    print(f"origin: {tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)}")

    # Test chains from each piece, each direction
    piece_coords = [(0, 1), (6, 1), (22, 6)]
    for (sx, sy) in piece_coords:
        for (dx, dy) in [(2, 0), (-2, 0), (0, 2), (0, -2)]:
            dst = (sx + dx, sy + dy)
            try_chain(g, (sx, sy), dst, f"piece({sx},{sy}) dir{(dx,dy)}")


if __name__ == '__main__':
    main()
