"""G50T L5: investigate when door[1] latch gets reverted.

Hypothesis: stepping onto sw[2] a second time toggles the latch (latch on
first press, latch off on second press).

Alt: pressing sw[1] un-latches door[1] somehow (cross-switch interaction).
"""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTIONS = {'U': 'ACTION1', 'D': 'ACTION2', 'L': 'ACTION3', 'R': 'ACTION4'}


def fresh():
    g = mod.G50t()
    g.set_level(4)
    return g


def do(g, name):
    full = name if name.startswith('ACTION') else ACTIONS[name]
    g.perform_action(ActionInput(id=getattr(GameAction, full)))


def apply(g, seq):
    for a in seq:
        do(g, a)


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def d_state(g):
    return tuple((d.x, d.y, bool(d.dijhfchobv)) for d in g.vgwycxsxjz.uwxkstolmf)


def main():
    # Test 1: press sw[2], step off, walk to sw[2] again.
    print("=== Test 1: press sw[2] twice ===")
    g = fresh()
    apply(g, ['D', 'R', 'R', 'R', 'D'])  # (1,13)→(19,25) sw[2]
    print(f"  after 1st press:   doors={d_state(g)}")
    apply(g, ['U'])  # step off
    print(f"  stepped off (U):   doors={d_state(g)}")
    apply(g, ['D'])  # step back on
    print(f"  back on sw[2]:     doors={d_state(g)}")
    apply(g, ['U'])  # step off again
    print(f"  stepped off again: doors={d_state(g)}")

    # Test 2: reach sw[1] via a path that DOES step on sw[2]
    print("\n=== Test 2: press sw[2] then continue to sw[1] ===")
    g = fresh()
    apply(g, ['D', 'R', 'R', 'R', 'D'])  # (1,13)→(19,25)
    print(f"  on sw[2]:           doors={d_state(g)}")
    apply(g, ['D'])  # → (19, 31)
    print(f"  after D to (19,31): doors={d_state(g)}")
    apply(g, ['D'])  # → (19, 37) = sw[1]
    print(f"  on sw[1]:           doors={d_state(g)}")
    apply(g, ['U'])  # step off sw[1]
    print(f"  off sw[1]:          doors={d_state(g)}")

    # Test 3: walk past sw[2] WITHOUT stopping
    print("\n=== Test 3: avoid touching sw[2] ===")
    g = fresh()
    # Try to reach sw[1] (19,37) without passing through sw[2] (19,25)
    # Paths avoiding (19,25): maybe via (13,19)→(13,25)? (13,25) may not exist.
    # Try: (1,13) D D D (1,31) R R R (19,31) D (19,37)
    apply(g, ['D', 'D', 'D', 'R', 'R', 'R', 'D'])
    print(f"  via left column:    player={pos(g)} doors={d_state(g)}")

    # Test 4: press sw[3] only and check if it stays
    print("\n=== Test 4: press sw[3] only, then walk to (19,37) ===")
    g = fresh()
    apply(g, ['U'])  # sw[3]
    print(f"  on sw[3]:           doors={d_state(g)}")
    apply(g, ['D'])  # off
    print(f"  off sw[3]:          doors={d_state(g)}")


if __name__ == "__main__":
    main()
