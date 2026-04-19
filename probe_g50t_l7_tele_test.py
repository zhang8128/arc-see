"""G50T L7: test teleport activation conditions for pair A (ulhh[4,5]) and
pair B (ulhh[6,7])."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTION_NAMES = {'U': 'ACTION1', 'D': 'ACTION2', 'L': 'ACTION3', 'R': 'ACTION4'}


def fresh():
    g = mod.G50t()
    g.set_level(6)
    return g


def do(g, name):
    full = name if name.startswith('ACTION') else ACTION_NAMES[name]
    g.perform_action(ActionInput(id=getattr(GameAction, full)))


def apply(g, seq):
    for a in seq:
        do(g, a)


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def main():
    # Test 1: walk to ulhh[5]=(13,25) from start directly, no sw press.
    # Expected: end at (13, 25), no teleport.
    g = fresh()
    apply(g, list('LL'))
    print(f"Test 1 (LL): {pos(g)}")  # should be (13, 25)

    # Test 2: press sw[2] first (via DDL), then walk back to (13, 25)
    # Path: D D L (sw[2]) then... (19,37) → we need to reach (13, 25)
    # From (19, 37): U (19, 31), U (19, 25), L (13, 25) — but check blockers
    g = fresh()
    apply(g, list('DDL') + list('UULL'))  # sw[2] then go back
    print(f"Test 2 (DDLUU + LL to ulhh[5]): {pos(g)}")

    # Test 3: walk via DDLRUULL (from the reach)
    g = fresh()
    apply(g, list('DDLRUULL'))
    print(f"Test 3 (DDLRUULL): {pos(g)}")

    # Test 4: from start to ulhh[6] = DDRRUUUURRDDDD (14 moves)
    g = fresh()
    apply(g, list('DDRRUUUURRDDDD'))
    print(f"Test 4 (to ulhh[6]): {pos(g)}")

    # Test 5: press sw[2] first then walk to ulhh[6]
    # Path: DDL (sw[2]), then go to (49, 37). From (19, 37):
    # R → (25, 37), R → (31, 37), R → (37, 37), R → (43, 37), R → (49, 37)? maybe
    g = fresh()
    apply(g, list('DDL') + list('RRRRRR'))
    print(f"Test 5 (sw[2]+RRRRRR): {pos(g)}")

    # Test 6: reach sw[3] via teleport (DDLRUULLUU) and observe
    g = fresh()
    apply(g, list('DDLRUULLUU'))
    print(f"Test 6 (DDLRUULLUU): {pos(g)}")
    # what are the switch states?
    print(f"  switches: {tuple(h.dijhfchobv for h in g.vgwycxsxjz.hamayflsib if hasattr(h, 'dijhfchobv'))}")
    print(f"  doors: {[(d.x, d.y, bool(d.dijhfchobv)) for d in g.vgwycxsxjz.uwxkstolmf]}")


if __name__ == "__main__":
    main()
