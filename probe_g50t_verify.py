"""G50T: verify single-point collision vs 7x7 box collision by testing specific moves."""
import copy
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def act(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, name)))


def test_reach(g, actions):
    for a in actions:
        act(g, a)
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def main():
    g = mod.G50t()
    g.set_level(0)

    # Test (19, 13) directly: from start (13, 7), go A2 A4
    print("=== Try to reach (19, 13) via A2 then A4 ===")
    g2 = copy.deepcopy(g)
    act(g2, 'ACTION2')
    print(f"  after A2: {(g2.vgwycxsxjz.dzxunlkwxt.x, g2.vgwycxsxjz.dzxunlkwxt.y)}")
    act(g2, 'ACTION4')
    print(f"  after A4: {(g2.vgwycxsxjz.dzxunlkwxt.x, g2.vgwycxsxjz.dzxunlkwxt.y)}")

    # Test via A4 then A2
    g3 = copy.deepcopy(g)
    act(g3, 'ACTION4')
    print(f"\n  via A4: {(g3.vgwycxsxjz.dzxunlkwxt.x, g3.vgwycxsxjz.dzxunlkwxt.y)}")
    act(g3, 'ACTION2')
    print(f"  after A2: {(g3.vgwycxsxjz.dzxunlkwxt.x, g3.vgwycxsxjz.dzxunlkwxt.y)}")

    # Test walkability check directly
    eng = g.vgwycxsxjz
    afb = eng.afbbgvkpip
    maze_px = afb.xmdjbwrpmv.pixels
    p = eng.dzxunlkwxt

    # The method rhvduhvfwn temporarily moves the sprite and checks.
    # Let me use the esidlbhbhw method to check individual pixels.
    print("\n=== Direct esidlbhbhw tests at player center coords ===")
    for (x, y) in [(13, 7), (19, 13), (25, 13), (31, 13), (37, 13)]:
        # Player center would be (x+3, y+3)
        cx, cy = x + 3, y + 3
        val = afb.esidlbhbhw(cx, cy)
        print(f"  player@({x},{y}) -> center ({cx},{cy}) -> afb.esidlbhbhw = {val}")

    # Check (19, 13) more carefully
    print("\n=== Walkability check for (19, 13) ===")
    # Move player sprite temporarily via its internal method to test
    # Actually call rhvduhvfwn from outside
    dx, dy = 1, 0  # right (from (13, 13) to (19, 13))
    # Set player position to (13, 13) first by moving
    g_test = copy.deepcopy(g)
    act(g_test, 'ACTION2')  # now at (13, 13)
    # Then try A4 to (19, 13) ?
    r = g_test.vgwycxsxjz.rhvduhvfwn(g_test.vgwycxsxjz.dzxunlkwxt, 19, 13)
    print(f"  rhvduhvfwn(player, 19, 13) from (13, 13) = {r}")


if __name__ == "__main__":
    main()
