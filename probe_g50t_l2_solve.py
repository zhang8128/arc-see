"""G50T L2: final BFS to the goal with both ghosts frozen holding both switches.

Starts from the verified chain setup:
  Phase A: L L ACTION5                      # ghost A = [L,L]
  Phase B: DDDDLLLLUULL ACTION5             # ghost B = 12 moves
  Phase C: re-walk DDDDLLLLUULL             # ghosts both finish their paths,
                                            # both are frozen holding switches
  Phase D: BFS from here until game state = WIN (or level advanced).
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


def is_win(g):
    return g._state.name == "WIN" or g._current_level_index > 1


PREFIX = (
    list('LL') + ['ACTION5']
    + list('DDDDLLLLUULL') + ['ACTION5']
    + list('DDDDLLLLUULL')
)


def main():
    # Verify prefix sets up the state we want
    g = fresh()
    apply(g, PREFIX)
    print(f"After prefix ({len(PREFIX)} actions):")
    print(f"  player: {pos(g)}")
    print(f"  state: {g._state.name}")
    print(f"  level_idx: {g._current_level_index}")

    # BFS from here
    print(f"\nBFS from (13,37) to goal (25,19)...")
    seen = {pos(g): []}
    q = deque([(pos(g), [])])
    best = None
    while q:
        p, path = q.popleft()
        if best is not None and len(path) >= len(best):
            continue
        if len(path) > 60:
            continue
        for name in 'UDLR':
            g2 = fresh()
            apply(g2, PREFIX + path + [name])
            new_p = pos(g2)
            if is_win(g2):
                full_solution = PREFIX + path + [name]
                print(f"\n*** WIN at move {len(path)+1} of phase D ***")
                print(f"Phase D path: {''.join(path + [name])}")
                print(f"Total L2 actions: {len(full_solution)}")
                if best is None or len(full_solution) < len(best):
                    best = full_solution
                break
            if new_p == p:
                continue  # blocked
            if new_p in seen and len(seen[new_p]) <= len(path) + 1:
                continue
            seen[new_p] = path + [name]
            q.append((new_p, path + [name]))

    if best:
        print("\n=== SOLUTION ===")
        print(f"Total: {len(best)} actions (baseline 175)")
        print(f"Ratio: {100*len(best)/175:.1f}%")
        print(f"Actions: {best}")
    else:
        print("\nNo win found in BFS bounds. Expanding search needed.")
        print(f"Reached {len(seen)} distinct tiles.")
        for p in sorted(seen.keys(), key=lambda t: (t[1], t[0])):
            print(f"  {p} via {''.join(seen[p])}")


if __name__ == "__main__":
    main()
