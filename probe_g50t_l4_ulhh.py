"""G50T L4: step on ulhh[2] with ghost holding switch[1] and observe."""
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


def snap(g, label):
    print(f"\n--- {label} ---")
    print(f"player: {pos(g)}")
    print(f"doors: {[(d.x, d.y) for d in g.vgwycxsxjz.uwxkstolmf]}")
    for i, h in enumerate(g.vgwycxsxjz.hamayflsib):
        extra = f" rqx={len(h.rqxibulywa)} vbq={len(h.vbqvjbxkfm)}"
        if hasattr(h, 'dijhfchobv'):
            extra += f" pressed={h.dijhfchobv}"
        print(f"  hamay[{i}] {type(h).__name__} at ({h.x},{h.y}) visible={h.is_visible}{extra}")
    print(f"ghosts: {[(k.x, k.y) for k in g.vgwycxsxjz.rloltuowth]}")
    print(f"engine bools: {[n for n in ('dofntsemri','jqpwhiraaj','jvtgoshrhq','pohkooyzds','safkknjslo','zvuxrhnlcb') if getattr(g.vgwycxsxjz, n)]}")
    print(f"state: {g._state.name} level_idx: {g._current_level_index}")


PREFIX = list('DDRD') + ['ACTION5']  # ghost A will hold switch[1] eventually


def main():
    g = fresh()
    apply(g, PREFIX)
    snap(g, "after ACTION5 (ghost A on path)")

    # Ghost A's path is DDRD (4 moves). Live player must make 4 moves for
    # ghost A to complete and freeze on (31,25). Let's walk toward ulhh[2].
    # After ACTION5, live player at (25, 7). Path to ulhh[2] via left column:
    # L L L (7,7) D D D D (7,31) D D (7,43)? Or LLLDDD...
    #
    # But wait - door[0] only opens on live move 5+ (after ghost A completes
    # 4 moves). Until then, door[0] is closed.
    # Live player moves 1-3: ghost A walking (not on switch yet), door closed.
    # Live player move 4: ghost A arrives at (31, 25) switch[1], door OPENS.
    # Live player move 5+: door stays open (ghost A frozen on sw1).
    #
    # So during moves 1-4, live player stuck in 18-tile region.
    # Let's first make those 4 moves, then explore.
    apply(g, list('LLLD'))  # random 4 moves in the initial region
    snap(g, "after 4 live moves (ghost A should be frozen)")

    # Now walk toward ulhh[2] = (25, 37). From (7, 13), path:
    # D D D D (7,37), R R R (25,37)
    apply(g, list('DDDD'))
    snap(g, "at (7, 37) area")
    apply(g, list('RRR'))
    snap(g, "should be at (25, 37) = ulhh[2]")

    # Try stepping off
    apply(g, list('U'))
    snap(g, "step off ulhh[2]")

    # Walk back on
    apply(g, list('D'))
    snap(g, "back on ulhh[2]")


if __name__ == "__main__":
    main()
