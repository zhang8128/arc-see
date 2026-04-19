"""G50T L2: test optimized phase C - walk toward goal during ghost B's replay.

Hypothesis:
  During phase C (after ACTION5 #2), we need 12+ live moves for ghost B to
  finish replaying. Instead of re-walking the same 12-move path (which ends
  at (13,37)), walk directly toward (7,19) which is the closest pre-goal tile
  reachable with just ghost A held. Then on move 12, door[0] opens and we
  walk RRR to the goal.

Prefix:
  Phase A: L L ACTION5          (3 actions)
  Phase B: DDDDLLLLUULL ACTION5  (13 actions)
  Phase C: UUULLLLLLLDD          (12 actions, live player → (7,19))
  Phase D: RRR                   (3 actions, (7,19) → (25,19))
Total: 31 actions.

Also checks some even shorter variations.
"""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTION_NAMES = {
    'U': 'ACTION1', 'D': 'ACTION2', 'L': 'ACTION3', 'R': 'ACTION4',
}


def fresh():
    g = mod.G50t()
    g.set_level(1)
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


def is_win(g):
    return g._state.name == "WIN" or g._current_level_index > 1


def run(seq, label):
    g = fresh()
    apply(g, seq)
    won = is_win(g)
    print(f"\n{label}: {len(seq)} actions")
    print(f"  final player: {pos(g)}")
    print(f"  state: {g._state.name}, level_idx: {g._current_level_index}")
    print(f"  WIN: {'YES' if won else 'no'}")
    return won


def main():
    # Optimized candidate
    seq1 = (
        list('LL') + ['ACTION5']
        + list('DDDDLLLLUULL') + ['ACTION5']
        + list('UUULLLLLLLDD')  # phase C: to (7,19)
        + list('RRR')           # phase D: to (25,19)
    )
    run(seq1, "Optimized (31 actions)")

    # Even shorter: can we skip the UU at the start of phase C?
    # UU → (49,13), LLLLLLL → (7,13), D → (7,19), so UULLLLLLLD = 10 moves,
    # ends at (7,19). But ghost B needs 12 moves to finish. We can add 2
    # no-op moves (blocked by wall) or just accept that we need 12 moves.
    # BFS shows (7,13) is reachable, so UULLLLLLL goes there in 9 moves.
    # From (7,13) we need to go to (7,19) but then we still need to have
    # 12 total live moves before ghost B finishes.
    #
    # Alternative: walk RLRL back-and-forth to burn moves.
    # But each "move" is either a real step or a blocked step. Blocked steps
    # still count as a game action and still advance ghost replay? Let me test.

    # Blocked move test: walk into a wall and count as a move?
    seq_blocked = (
        list('LL') + ['ACTION5']
        + list('DDDDLLLLUULL') + ['ACTION5']
        + list('UU')    # 2 moves up, player (49,13)
        + list('UU')    # try to go up more - (49,7) via UU
        + list('U')     # U into wall - blocked but counts as action?
    )
    g = fresh()
    apply(g, seq_blocked)
    print(f"\nBlocked-move test:")
    print(f"  player after {len(seq_blocked)} actions: {pos(g)}")
    print(f"  ghost list: {[(k.x, k.y) for k in g.vgwycxsxjz.rloltuowth]}")

    # Count optimal
    print(f"\n=== Baseline 175 comparison ===")
    print(f"  Original prefix+BFS: 55 actions (31.4%)")
    print(f"  Optimized: {len(seq1)} actions ({100*len(seq1)/175:.1f}%)")


if __name__ == "__main__":
    main()
