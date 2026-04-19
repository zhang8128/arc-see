"""Find the 'big' background sprite on L7 that renders panels."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
sys.path.insert(0, '/Users/kairos/Projects/arc-see/solutions')

import numpy as np
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

    # Look at ALL entries in cache — include unnamed ones
    cache = g.env._game.ikhhdzfmarl._sorted_cache
    print(f"Total cache items: {len(cache)}")
    # Unique z-values and counts
    from collections import Counter
    zs = Counter()
    for item in cache:
        zs[item[0]] += 1
    print(f"Z-value distribution: {dict(zs)}")

    # List all unnamed sprites with their sizes and grids
    print("\n=== All unnamed sprites (size + position) ===")
    for item in cache:
        s = item[1]
        nm = getattr(s, 'name', '')
        if nm:
            continue
        x, y = getattr(s, 'x', -1), getattr(s, 'y', -1)
        size = getattr(s, 'lrggiefpfpe', None)
        z = item[0]
        grid_tuple = getattr(s, 'gmhhfvghrrq', None)
        grid_info = None
        if isinstance(grid_tuple, tuple) and grid_tuple:
            g = grid_tuple[0]
            if isinstance(g, np.ndarray):
                unique_vals = sorted(np.unique(g).tolist())
                grid_info = f"shape={g.shape}, colors={unique_vals}"
        print(f"  z={z}, pix({x},{y}), size={size}, grid={grid_info}")

    # Also look at named sprites for grid attributes
    print("\n=== Named sprites with 2D+ grid attrs ===")
    for item in cache:
        s = item[1]
        nm = getattr(s, 'name', '')
        if not nm:
            continue
        # Look for 2D numpy arrays
        grid_attrs = []
        for a in dir(s):
            if a.startswith('_'):
                continue
            try:
                v = getattr(s, a)
                if isinstance(v, np.ndarray) and v.ndim >= 2:
                    grid_attrs.append((a, v.shape))
            except Exception:
                pass
        if grid_attrs:
            x = getattr(s, 'x', -1)
            y = getattr(s, 'y', -1)
            print(f"  {nm!r} @ tile({x//6},{y//6}): grid_attrs={grid_attrs}")


if __name__ == '__main__':
    main()
