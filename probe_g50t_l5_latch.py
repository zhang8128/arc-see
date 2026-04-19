"""G50T L5: verify latches persist, then BFS reach after latching both.

Step 1: walk to sw[3] (1,7), walk away — verify door[2] stays latched.
Step 2: also walk to sw[2] (19,25), walk away — verify door[1] stays latched.
Step 3: from that state, BFS for reach. Does sw[0] become reachable?
"""
import importlib.util
from collections import deque
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


def doors(g):
    return tuple((d.x, d.y, bool(d.dpdubazedr), bool(d.dijhfchobv))
                 for d in g.vgwycxsxjz.uwxkstolmf)


ANNOT = {
    (55, 25): 'sw[0]', (19, 37): 'sw[1]', (19, 25): 'sw[2]', (1, 7): 'sw[3]',
    (43, 37): 'ulhh[4]', (43, 49): 'ulhh[5]', (7, 43): 'WIN',
}


def bfs_from(prefix, max_depth=40):
    """BFS player tiles after prefix."""
    g0 = fresh()
    apply(g0, prefix)
    start = pos(g0)
    seen = {start: list(prefix)}
    tiles = {start: []}
    q = deque([(start, [])])
    while q:
        p, path = q.popleft()
        if len(path) >= max_depth:
            continue
        for name in 'UDLR':
            g = fresh()
            apply(g, prefix + path + [name])
            np_ = pos(g)
            if np_ != p and np_ not in tiles:
                tiles[np_] = path + [name]
                q.append((np_, path + [name]))
    return tiles


def main():
    # Step 1: just walk to sw[3], walk off, check door state
    g = fresh()
    print("=== Before any switches ===")
    print(f"doors: {doors(g)}")

    apply(g, ['U'])  # (1,13)→(1,7) = sw[3]
    print("\n=== on sw[3] ===")
    print(f"player: {pos(g)}")
    print(f"doors: {doors(g)}")

    apply(g, ['D'])  # step off, (1,7)→(1,13)
    print("\n=== stepped off sw[3] ===")
    print(f"player: {pos(g)}")
    print(f"doors: {doors(g)}")

    # sw[2] path from (1,13) after sw[3] is latched - try to reach (19,25)
    # Original path from (1,13) to (19,25) was DRRRD. Let's try.
    apply(g, ['D', 'R', 'R', 'R', 'D'])
    print("\n=== walked to sw[2] ===")
    print(f"player: {pos(g)}")
    print(f"doors: {doors(g)}")

    apply(g, ['U'])  # step off
    print("\n=== stepped off sw[2] ===")
    print(f"player: {pos(g)}")
    print(f"doors: {doors(g)}")

    # Now from (19, 19), BFS the new reach
    print("\n=== BFS from post-latch state ===")
    tiles = bfs_from(['U', 'D', 'R', 'R', 'R', 'D', 'U'])  # after the walk above
    print(f"Reached {len(tiles)} tiles:")
    for p in sorted(tiles, key=lambda t: (t[1], t[0])):
        a = f"  <-- {ANNOT[p]}" if p in ANNOT else ""
        print(f"  {p}{a}")

    missing = [t for t in ANNOT if t not in tiles]
    print(f"\nStill unreachable: {missing}")


if __name__ == "__main__":
    main()
