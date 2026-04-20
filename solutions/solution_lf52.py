"""LF52 complete solution — all 10 levels.

Composes per-level modules:
  L1-L6: hardcoded sequences in lf52_tool.LF52(up_to_level=7)
  L7: solutions/solution_lf52_l7.apply_solution
  L8: solutions/solution_lf52_l8.apply_solution
  L9: solutions/solution_lf52_l9.apply_solution
  L10: solutions/solution_lf52_l10.apply_solution

Total ~0.5s to verify against the real engine.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')


def solve(verbose=True):
    from lf52_tool import LF52
    from solutions.solution_lf52_l7 import apply_solution as apply_l7
    from solutions.solution_lf52_l8 import apply_solution as apply_l8
    from solutions.solution_lf52_l9 import apply_solution as apply_l9
    from solutions.solution_lf52_l10 import apply_solution as apply_l10

    g = LF52(up_to_level=7, verbose=False)
    if verbose:
        print(f'L1-L6 replay: levels_completed={g.level()}')

    for level, apply in [(7, apply_l7), (8, apply_l8), (9, apply_l9), (10, apply_l10)]:
        apply(g)
        if verbose:
            print(f'After L{level}: levels_completed={g.level()} state={g.obs.state.name}')
    return g


if __name__ == '__main__':
    import time
    t = time.time()
    g = solve()
    print(f'\nTotal runtime: {time.time()-t:.2f}s')
    if g.obs.state.name == 'WIN' and g.obs.levels_completed >= 10:
        print('*** LF52 FULLY SOLVED (25/25 complete) ***')
    else:
        print(f'!!! Unexpected final state: {g.obs.state.name} levels={g.obs.levels_completed}')
