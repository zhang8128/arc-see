"""G50T L3: isolate door[2] behavior (the dpdubazedr=True door).

Questions:
  1. Does door[2] revert when player leaves switch[2]? (Or is it latched?)
  2. Is there a path to switch[1] that DOESN'T cross switch[2]?
  3. Does switch[1] alone move door[2], or was it cross-contamination?
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
    g.set_level(2)
    return g


def do(g, name):
    full = name if name.startswith('ACTION') else ACTIONS[name]
    g.perform_action(ActionInput(id=getattr(GameAction, full)))


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def doors(g):
    return tuple((d.x, d.y, bool(d.dijhfchobv), bool(d.dpdubazedr))
                 for d in g.vgwycxsxjz.uwxkstolmf)


def switches(g):
    return tuple(h.dijhfchobv for h in g.vgwycxsxjz.hamayflsib)


def show(g, label):
    print(f"\n{label}")
    print(f"  player: {pos(g)}")
    print(f"  switches: {switches(g)}")
    print(f"  doors: {doors(g)}")


def main():
    # Test 1: walk onto switch[2], then off, and see if door[2] reverts
    print("=== Test 1: is switch[2] latched? ===")
    g = fresh()
    show(g, "start")
    for a in 'UURRRRDD':  # (7,19)→(31,19) = switch[2]
        do(g, a)
    show(g, "on switch[2]")
    for a in 'U':  # step off switch[2] → (31,13)
        do(g, a)
    show(g, "off switch[2] (went U)")
    for a in 'UR':  # go (31,7) then (37,7) to get far
        do(g, a)
    show(g, "(37, 7)")

    # Test 2: is there a path to switch[1] that avoids (31,19)?
    # From top row (7,7)-(49,7), we reached (31,13) and (49,13).
    # Can we reach (37, 31) without crossing (31, 19)?
    # Only (31,13)→(31,19) is the connector we used. Let me try from (49,13).
    print("\n=== Test 2: path to switch[1] avoiding switch[2]? ===")
    g = fresh()
    for a in 'UURRRRRRRD':  # (7,19)→(7,7)→top→(49,7)→(49,13)
        do(g, a)
    show(g, "at (49, 13)")
    for a in 'D':
        do(g, a)
    show(g, "tried D from (49,13)")

    # Test 3: clean switch[1] test using a path that starts fresh
    # but wait - any path FROM START must go through top and down, and the only
    # downward connectors in reachable set are at x=7, 31, 49. So (31, 19) is
    # the unavoidable connector from the top-row to switch[1].
    # HOWEVER — if switch[2] is NOT latched (test 1 above tells us), then
    # temporarily touching it on the way doesn't matter.
    #
    # Let's test: step ONTO switch[2] and observe door[2] while player sits there.
    print("\n=== Test 3: door[2] behavior while on/off switch[2] ===")
    g = fresh()
    for a in 'UURRRRDD':  # → (31,19) = switch[2]
        do(g, a)
    show(g, "on switch[2]")
    print(f"  is hamay[2].dijhfchobv True? {g.vgwycxsxjz.hamayflsib[2].dijhfchobv}")
    print(f"  is door[2].dpdubazedr True? {g.vgwycxsxjz.uwxkstolmf[2].dpdubazedr}")


if __name__ == "__main__":
    main()
