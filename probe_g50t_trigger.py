"""G50T: does the (37,7) trigger persist after stepping off, or revert?"""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def dump(g, tag):
    eng = g.vgwycxsxjz
    p = eng.dzxunlkwxt
    ham = eng.hamayflsib[0]
    uwx = eng.uwxkstolmf[0]
    print(f"  [{tag}] player=({p.x},{p.y}) "
          f"ham.pos=({ham.x},{ham.y}) ham.d={ham.dijhfchobv} "
          f"uwx.pos=({uwx.x},{uwx.y}) uwx.d={uwx.dijhfchobv}")


def act(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, name)))


def main():
    g = mod.G50t()
    g.set_level(0)
    dump(g, "start")
    for i in range(4):
        act(g, 'ACTION4')
    dump(g, "after 4R (should be at 37,7)")

    # Step off in some direction. ACTION3 = LEFT
    act(g, 'ACTION3')
    dump(g, "after 1L")

    # Step further away
    act(g, 'ACTION3')
    dump(g, "after 2L")

    # Step back right
    act(g, 'ACTION4')
    dump(g, "after 1R")
    act(g, 'ACTION4')
    dump(g, "after 2R (back at 37,7)")

    # Now try going down from (37,7)
    act(g, 'ACTION2')
    dump(g, "try 1D from (37,7)")

    # From the retained state, try each direction
    print("\n=== Fresh: walk to (37,7), try every direction ===")
    g2 = mod.G50t()
    g2.set_level(0)
    for _ in range(4):
        act(g2, 'ACTION4')
    dump(g2, "at (37,7)")
    for a in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4']:
        # Copy would be better; use snapshots since we want to know what stays
        import copy
        g3 = copy.deepcopy(g2)
        act(g3, a)
        dump(g3, f"(37,7) + {a}")


if __name__ == "__main__":
    main()
