"""Test: do clicks work AFTER doing some A-actions at L7?"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')

import copy, hashlib
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
        # Include color/visibility/selection
        sprites.append((nm, x, y, getattr(s, 'visible', None)))
    sprites.sort()
    return hashlib.md5(repr(sprites).encode()).hexdigest()[:10]


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


def main():
    g = LF52(up_to_level=1, verbose=False)
    setup_l7(g)
    init_snap = copy.deepcopy(g.env._game)
    init_foz = foz_count(g)

    # Try EACH single A-action, then probe all clicks
    for a_action in [None, 1, 2, 3, 4]:
        g.env._game = copy.deepcopy(init_snap)
        if a_action is not None:
            g.env.step(getattr(GameAction, f'ACTION{a_action}'))
        snap_after_a = copy.deepcopy(g.env._game)
        h_after_a = state_hash(g)
        foz_after_a = foz_count(g)
        pieces_after_a = piece_positions(g)
        label = f"init" if a_action is None else f"A{a_action}"
        print(f"\n=== After {label}: foz={foz_after_a}, pieces={pieces_after_a}, hash={h_after_a} ===")

        # Now try ALL piece positions as clicks (source click)
        for (pnm, px, py) in pieces_after_a:
            g.env._game = copy.deepcopy(snap_after_a)
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': px*6+3+ox, 'y': py*6+3+oy})
            h_after_click = state_hash(g)
            if h_after_click != h_after_a:
                print(f"  CLICK {pnm} ({px},{py}): sprite CHANGED ({h_after_click})")
            else:
                # Check frame
                import numpy as np
                import hashlib as hl
                # Need obs. Retry with step return
                pass


if __name__ == '__main__':
    main()
