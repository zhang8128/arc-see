"""G50T L2: test 2-ghost chaining.

Plan:
  1. LL -> live player on switch[1], record path
  2. ACTION5 -> ghost A saved ([L,L]), new player at (49,25). rlazdofsxb=1
  3. Walk to switch[0]=(13,37): DDDDLLLLUULL (12 moves)
     - Ghost A replays [L,L] on live moves 1,2 -> ends on switch[1] holding it
  4. ACTION5 -> ghost B saved, new player at (49,25). rlazdofsxb=2
     QUESTION 1: does ghost A still exist?
     QUESTION 2: what are the door states now?
  5. Walk following ghost B's path so ghost B ends at switch[0]:
     DDDDLLLLUULL (ghost B replays exactly its path, ends at switch[0])
  6. From there, BFS for goal (25,19) while both ghosts are (hopefully) frozen
     holding both switches.
"""
import importlib.util
from collections import deque
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


def ghost_info(g):
    """List of (ghost_position, remaining_moves) for each ghost."""
    eng = g.vgwycxsxjz
    gs = getattr(eng, 'rloltuowth', {})
    if isinstance(gs, dict):
        return [((gk.x, gk.y), len(v)) for gk, v in gs.items()]
    return []


def switches(g):
    return tuple(h.dijhfchobv for h in g.vgwycxsxjz.hamayflsib)


def doors(g):
    return tuple((d.x, d.y) for d in g.vgwycxsxjz.uwxkstolmf)


def counter(g):
    return getattr(g.vgwycxsxjz, 'rlazdofsxb', None)


def show(g, label):
    print(f"\n{label}")
    print(f"  player: {pos(g)}")
    print(f"  rlazdofsxb (ghost counter): {counter(g)}")
    print(f"  ghosts: {ghost_info(g)}")
    print(f"  switches (hamay states): {switches(g)}")
    print(f"  doors: {doors(g)}")


def main():
    g = fresh()
    show(g, "=== Start ===")

    # Step 1: walk to switch[1]
    apply(g, ['L', 'L'])
    show(g, "After LL (live player on switch[1])")

    # Step 2: ACTION5 - save ghost A
    do(g, 'ACTION5')
    show(g, "After ACTION5 #1 (ghost A recorded, new live player spawned)")

    # Step 3: walk the live player to switch[0]=(13,37)
    #   Path from (49,25): DDDDLLLLUULL = 12 moves
    path_to_sw0 = list('DDDDLLLLUULL')
    for i, a in enumerate(path_to_sw0):
        do(g, a)
    show(g, f"After walking to switch[0] ({len(path_to_sw0)} moves)")

    # Step 4: ACTION5 - save ghost B
    do(g, 'ACTION5')
    show(g, "After ACTION5 #2 (ghost B recorded)")

    # Step 5: walk the new live player - does ghost B replay correctly?
    #   When live player moves, ghost B replays path_to_sw0 step by step.
    #   We want ghost B to end up on switch[0].
    #   If we walk the SAME path, ghost B mirrors us step-for-step, but then
    #   ghost B ends on (13,37) and live player also ends on (13,37) — that's
    #   collision-free (ghosts don't block the live player) but wastes moves.
    #   Better: we walk ANY sequence of 12+ moves. After 12 live moves,
    #   ghost B has finished its path and is holding switch[0].
    # For the test: just walk the same path again and see both switches held.
    for a in path_to_sw0:
        do(g, a)
    show(g, "After re-walking path_to_sw0 (ghost B now on switch[0])")

    # Check: are both switches now held?
    sw = switches(g)
    print(f"\n  switches held? [switch0={sw[0]}, switch1={sw[1]}]")


if __name__ == "__main__":
    main()
