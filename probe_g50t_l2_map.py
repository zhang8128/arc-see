"""G50T L2: map the reachable area, test each switch independently.

Answers:
  1. What tiles can the player reach without any triggers?
  2. Can the player stand on hamay[0] (13,37)? hamay[1] (37,25)?
  3. When the player stands on each switch, which door(s) move?
  4. Is the goal (25,19) reachable via just walking through an opened door?
"""
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTIONS = {
    'U': 'ACTION1',  # up
    'D': 'ACTION2',  # down
    'L': 'ACTION3',  # left
    'R': 'ACTION4',  # right
}


def fresh_game(level=1):
    g = mod.G50t()
    g.set_level(level)
    return g


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def do(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, ACTIONS[name])))


def snapshot_doors(g):
    eng = g.vgwycxsxjz
    return tuple((d.x, d.y, d.rotation) for d in eng.uwxkstolmf)


def snapshot_switches(g):
    eng = g.vgwycxsxjz
    return tuple(h.dijhfchobv for h in eng.hamayflsib)


def bfs_reach(level=1, max_depth=200):
    """Simple BFS using engine replay (no ghosts, just walking)."""
    # We'll do this without trying to snapshot/restore engine state —
    # instead replay move sequences from a fresh game for each node.
    start_g = fresh_game(level)
    start = pos(start_g)
    seen = {start: []}
    q = deque([(start, [])])
    while q:
        p, path = q.popleft()
        if len(path) >= max_depth:
            continue
        for name in ACTIONS:
            g = fresh_game(level)
            for a in path:
                do(g, a)
            do(g, name)
            np_ = pos(g)
            if np_ != p and np_ not in seen:
                seen[np_] = path + [name]
                q.append((np_, path + [name]))
    return seen


def main():
    print("=== L2 reachable-without-mechanics scan ===")
    # First a shallow BFS to see connectivity
    reach = bfs_reach(level=1, max_depth=25)
    print(f"Reached {len(reach)} tiles in up to depth 25:")
    for p in sorted(reach, key=lambda t: (t[1], t[0])):
        print(f"  {p}  via {''.join(reach[p])}")

    goal = (25, 19)
    sw0 = (13, 37)
    sw1 = (37, 25)
    print()
    print(f"Goal (25,19) reachable by walking alone? {goal in reach}")
    print(f"Switch[0] (13,37) reachable? {sw0 in reach}")
    print(f"Switch[1] (37,25) reachable? {sw1 in reach}")

    # Test each switch: step onto it and see what the doors do
    print("\n=== Switch -> door mapping ===")
    for sw_name, sw_pos in [('hamay[0]=(13,37)', sw0), ('hamay[1]=(37,25)', sw1)]:
        if sw_pos not in reach:
            print(f"\n{sw_name}: not directly reachable, skipping")
            continue
        g = fresh_game(1)
        before_doors = snapshot_doors(g)
        before_sw = snapshot_switches(g)
        for a in reach[sw_pos]:
            do(g, a)
        after_doors = snapshot_doors(g)
        after_sw = snapshot_switches(g)
        print(f"\n{sw_name}:")
        print(f"  path: {''.join(reach[sw_pos])}")
        print(f"  player now at: {pos(g)}")
        print(f"  switch states: {before_sw} -> {after_sw}")
        for i, (b, a_) in enumerate(zip(before_doors, after_doors)):
            if b != a_:
                print(f"  door[{i}] MOVED: {b} -> {a_}")
            else:
                print(f"  door[{i}] unchanged: {b}")


if __name__ == "__main__":
    main()
