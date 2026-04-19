"""LF52 full solve L1-L6 via legitimate play.

L1: 8 moves (solution_lf52_full.py L1_CLICKS)
L2: 35 moves (solution_lf52_full.py L2_SOLVE)
L3: 46 moves (solution_lf52_full.py L3_SOLVE)
L4: 34 moves (solution_lf52_l4.py L4_SOLVE) — NEW 2026-04-16
L5: 67 moves (solution_lf52_l5.py SOLUTION) — verified legit 2026-04-16
L6: 55 moves (solution_lf52_l6.py SOLUTION_STR) — verified legit 2026-04-16

Total: 245 moves for L1-L6.

All verified via lf52_tool which drives the same arc_agi engine as MCP.
L7-L10 remain unsolved. L7 from legitimate play has 3 pieces + 6 sub-vehicles
(different from set_level L7 state previous sessions analyzed).
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

from lf52_tool import LF52
from arcengine import GameAction
from solutions.solution_lf52_l4 import L4_SOLVE
from solutions.solution_lf52_l5 import SOLUTION as L5_SOLUTION
from solutions.solution_lf52_l6 import parse_solution as parse_l6


def apply_coord_step(g, step):
    """Handle string-and-coord solution format."""
    if isinstance(step, str):
        g.env.step(getattr(GameAction, f'ACTION{int(step[1:])}'))
    elif step[0] == 'A':
        g.env.step(getattr(GameAction, f'ACTION{step[1]}'))
    elif step[0] == 'C' and len(step) == 2:
        # ('C', (x, y)) - direct viewport click
        g.env.step(GameAction.ACTION6, data={'x': step[1][0], 'y': step[1][1]})
    elif step[0] == 'C' and len(step) == 3:
        # ('C', (sx, sy), (dx, dy)) - piece-grid chain
        _, (sx, sy), (dx, dy) = step
        ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
        g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
        ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
        g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})


def run():
    # Start at L4 init (after L1+L2+L3 solves automatically via lf52_tool)
    g = LF52(up_to_level=4, verbose=False)
    print(f'Reached L4 legit: level={g.level()}')

    # L4
    for step in L4_SOLVE:
        apply_coord_step(g, step)
    print(f'After L4 solve: level={g.env._game._current_level_index}')

    # L5
    for step in L5_SOLUTION:
        apply_coord_step(g, step)
    print(f'After L5 solve: level={g.env._game._current_level_index}')

    # L6
    for step in parse_l6():
        apply_coord_step(g, step)
    print(f'After L6 solve: level={g.env._game._current_level_index}')

    return g


if __name__ == '__main__':
    run()
