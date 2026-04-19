"""Fast runner: play LF52 L1-L9 from scratch, land at L10 init.

No BFS at runtime — uses pre-computed solution sequences only.
Typical runtime: ~5 seconds.

Usage:
    uv run python lf52_play_to_l10.py

Returns a game object at L10 init ready for L10 work.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import time
from lf52_tool import LF52


def play_to_l10(verbose=True):
    """Apply L1-L9 solutions. Return game at L10 init."""
    t0 = time.time()

    # LF52(up_to_level=7) replays L1-L6 via lf52_tool's hardcoded sequences.
    g = LF52(up_to_level=7, verbose=False)
    if verbose:
        print(f'After L1-L6: levels={g.level()}, t={time.time()-t0:.1f}s')

    # L7-L9 via solution modules
    from solutions.solution_lf52_l7 import apply_solution as a7
    from solutions.solution_lf52_l8 import apply_solution as a8
    from solutions.solution_lf52_l9 import apply_solution as a9

    a7(g)
    if verbose:
        print(f'After L7:    levels={g.level()}, t={time.time()-t0:.1f}s')
    a8(g)
    if verbose:
        print(f'After L8:    levels={g.level()}, t={time.time()-t0:.1f}s')
    a9(g)
    if verbose:
        ik = g.env._game.ikhhdzfmarl
        print(f'After L9:    levels={g.level()}, whtqurkphir={ik.whtqurkphir} (L10), t={time.time()-t0:.1f}s')
    return g


if __name__ == '__main__':
    g = play_to_l10()
    print()
    print(f'Total time: paid once, L10 init ready.')
    ik = g.env._game.ikhhdzfmarl
    grid = ik.hncnfaqaddg
    foz = [(s.name, tuple(s.chahdtpdoz)) for s in grid.xpnsbxlatu if 'fozwvlovdui' in s.name]
    print(f'L10 init: foz={foz}')
