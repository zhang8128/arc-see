"""G50T L7: map each reachable switch to its door effect, plus test latched
door[1] toggle behavior. Also test what the player does when stepping on each
reachable teleporter."""
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


def doors(g):
    return tuple((d.x, d.y, bool(d.dijhfchobv)) for d in g.vgwycxsxjz.uwxkstolmf)


def hamay_sw(g):
    return tuple(h.dijhfchobv for h in g.vgwycxsxjz.hamayflsib if hasattr(h, 'dijhfchobv'))


# Paths
SW2 = list('DDL')         # to (19, 37)
SW3 = list('DDLRUULLUU')  # to (13, 1)
# Teleporter paths from reach
ULHH4 = list('DDLRUULL')  # to (13, 13)
ULHH5 = list('LL')        # to (13, 25)
ULHH6 = list('DDRRUUUURRDDDD')  # to (49, 37)


def test(label, path):
    g = fresh()
    before_d = doors(g)
    apply(g, path)
    print(f"\n{label}: player={pos(g)}")
    print(f"  doors before: {before_d}")
    print(f"  doors after:  {doors(g)}")
    print(f"  switches: {hamay_sw(g)}")


def main():
    test("on sw[2] (19,37)", SW2)
    test("on sw[3] (13,1)", SW3)
    test("off sw[2] (try L from 19,37)", SW2 + ['L'])
    test("off sw[3] (try D from 13,1)", SW3 + ['D'])
    test("walk onto ulhh[4]", ULHH4)
    test("walk onto ulhh[5]", ULHH5)
    test("walk onto ulhh[6]", ULHH6)
    # Test: what if we touch sw[2] then walk to ulhh[5]?
    test("sw[2] touch, then LL to ulhh[5]", SW2 + ['U'] + ['L', 'L'])


if __name__ == "__main__":
    main()
