"""Check actual sizes of L7 sprites to identify big 'world map' sprites."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')

from lf52_tool import LF52
from arcengine import GameAction
import solution_lf52_l5 as L5
import solution_lf52_l6 as L6


def setup_l7(g):
    g.env._game.set_level(4)
    g.env._game.on_set_level(g.env._game.current_level)
    obs = g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})
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


def main():
    g = LF52(up_to_level=1, verbose=False)
    setup_l7(g)

    # Inspect all named sprites with their sizes
    cache = g.env._game.ikhhdzfmarl._sorted_cache
    for item in cache:
        s = item[1]
        nm = getattr(s, 'name', '')
        if not nm:
            continue
        x, y = getattr(s, 'x', -999), getattr(s, 'y', -999)
        # Try multiple size-related attrs
        w_attr = None
        h_attr = None
        for attr in ['width', 'w', 'rqbcokmadki']:  # common obfuscated names
            v = getattr(s, attr, None)
            if v is not None:
                w_attr = (attr, v)
                break
        for attr in ['height', 'h']:
            v = getattr(s, attr, None)
            if v is not None:
                h_attr = (attr, v)
                break
        # Check grid (which is the actual pixel data)
        grid = getattr(s, 'grid', None)
        grid_shape = None
        if grid is not None:
            try:
                import numpy as np
                arr = np.asarray(grid)
                grid_shape = arr.shape
            except Exception:
                pass
        print(f"{nm!r} at world_pix({x}, {y}) tile({x//6},{y//6}) grid_shape={grid_shape} w={w_attr} h={h_attr}")


if __name__ == '__main__':
    main()
