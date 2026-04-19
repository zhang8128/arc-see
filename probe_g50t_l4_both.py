"""G50T L4: observe state when BOTH switches held.

Use ghost A to hold switch[0] while live player stands on switch[1].
Inspect: door state, hamay state, ulhhdeoyok sets, any engine bools that flip.
"""
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
    g.set_level(3)
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


def full_snapshot(g, label):
    print(f"\n=== {label} ===")
    print(f"player: {pos(g)}")
    print(f"doors: {[(d.x, d.y, d.dijhfchobv) for d in g.vgwycxsxjz.uwxkstolmf]}")
    print("hamay:")
    for i, h in enumerate(g.vgwycxsxjz.hamayflsib):
        extra = ""
        if hasattr(h, 'rqxibulywa'):
            extra += f" rqx={h.rqxibulywa}"
        if hasattr(h, 'vbqvjbxkfm'):
            extra += f" vbq={h.vbqvjbxkfm}"
        if hasattr(h, 'dijhfchobv'):
            extra += f" pressed={h.dijhfchobv}"
        print(f"  [{i}] {type(h).__name__} at ({h.x},{h.y}){extra}")
    # Engine bools and scalars
    eng = g.vgwycxsxjz
    bools = {n: getattr(eng, n) for n in dir(eng)
             if not n.startswith('_') and isinstance(getattr(eng, n, None), bool)}
    ints = {n: getattr(eng, n) for n in dir(eng)
            if not n.startswith('_') and isinstance(getattr(eng, n, None), int)
            and not isinstance(getattr(eng, n, None), bool)}
    print(f"engine bools: {bools}")
    print(f"engine ints: {ints}")
    print(f"ghost count: {len(eng.rloltuowth)}")


def main():
    # Baseline
    g = fresh()
    full_snapshot(g, "START")

    # Press switch[0] alone (walk to (49, 25))
    g = fresh()
    apply(g, list('DDRRUURRDDD'))
    full_snapshot(g, "on switch[0] alone")

    # Press switch[1] alone
    g = fresh()
    apply(g, list('DDRD'))
    full_snapshot(g, "on switch[1] alone")

    # Ghost A holds switch[0], live player walks to switch[1]
    # Path to switch[0] = DDRRUURRDDD (11 moves).
    # After ACTION5, ghost A saved with path; live player at (25, 7).
    # Live player walks to switch[1]: DDRD (4 moves).
    # During these 4 moves, ghost A replays first 4 moves of its path:
    #   move 0: D → (25,13)
    #   move 1: D → (25,19)
    #   move 2: R → (31,19)
    #   move 3: R → (37,19)
    # Ghost A is NOT on switch[0] by the time we arrive at switch[1] — only 4
    # of its 11 moves replayed.
    # So live player needs to idle until ghost A completes 11 moves, then
    # walk to switch[1].
    # Simplest: live player re-walks the 11-move path → ghost A frozen on
    # switch[0], live player at (49,25) = on switch[0] too (not what we want).
    # Better: walk to (49, 25) then do moves that keep us there? Or walk to
    # switch[1] via a longer path that ends on switch[1] exactly at move 11.
    #
    # Actually: we want ghost A frozen on switch[0] AND live player on switch[1].
    # Ghost A freezes at live move 11. Live player must be on switch[1] at or
    # after move 11.
    # Shortest live path from (25,7) to (31,25) is DDRD (4 moves) ending at (31,25).
    # Then we need 7 more moves that return to switch[1]. Could wiggle.
    #
    # But let's first just verify what "both held" looks like. Easiest: walk
    # the 11-move path (ends on switch[0]), then walk to switch[1], but wait —
    # leaving switch[0] unpresses it. Hmm.
    #
    # Skip ghost for now. Test: press switch[0] for long enough during
    # live player's walk to observe any persistent state change.
    print("\n=== Walk sw[0] then sw[1] via direct path (no ghost) ===")
    g = fresh()
    apply(g, list('DDRRUURRDDD'))  # to (49, 25) = switch[0]
    full_snapshot(g, "arrived switch[0]")
    apply(g, list('LL') + ['U', 'L', 'L', 'D'])  # try to walk to (31, 25)
    full_snapshot(g, "after sequence from sw[0]")


if __name__ == "__main__":
    main()
