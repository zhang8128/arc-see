"""G50T L3: find a path to switch[0] = (19, 49) and observe what it opens."""
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTION_NAMES = {'U': 'ACTION1', 'D': 'ACTION2', 'L': 'ACTION3', 'R': 'ACTION4'}


def fresh():
    g = mod.G50t()
    g.set_level(2)
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


def doors(g):
    return tuple((d.x, d.y) for d in g.vgwycxsxjz.uwxkstolmf)


def switches(g):
    return tuple(h.dijhfchobv for h in g.vgwycxsxjz.hamayflsib)


PREFIX = list('UURRRRDDDDR') + ['ACTION5']


def bfs_to_target(target):
    """BFS live-player moves after PREFIX, find path to target tile."""
    g0 = fresh()
    apply(g0, PREFIX)
    start = pos(g0)
    seen = {start: []}
    q = deque([(start, [])])
    while q:
        p, path = q.popleft()
        if p == target:
            return path
        if len(path) > 30:
            continue
        for name in 'UDLR':
            g = fresh()
            apply(g, PREFIX + path + [name])
            np_ = pos(g)
            if np_ == p or np_ in seen:
                continue
            seen[np_] = path + [name]
            q.append((np_, path + [name]))
    return None


def main():
    sw0 = (19, 49)
    path = bfs_to_target(sw0)
    if not path:
        print(f"switch[0] at {sw0} not reachable from post-prefix state")
        return
    print(f"Path to switch[0]: {''.join(path)} ({len(path)} moves)")

    # Walk there and see what door state becomes
    g = fresh()
    apply(g, PREFIX + path)
    print(f"\nOn switch[0]:")
    print(f"  player: {pos(g)}")
    print(f"  doors: {doors(g)}")
    print(f"  switches: {switches(g)}")
    print(f"  ghost positions: {[(k.x, k.y) for k in g.vgwycxsxjz.rloltuowth]}")

    # Now step off and observe
    g2 = fresh()
    apply(g2, PREFIX + path + ['U'])  # try going up
    print(f"\nAfter stepping off (U):")
    print(f"  player: {pos(g2)}")
    print(f"  doors: {doors(g2)}")
    print(f"  switches: {switches(g2)}")
    print(f"  door[0].dijhfchobv: {g2.vgwycxsxjz.uwxkstolmf[0].dijhfchobv}")
    print(f"  door[1].dijhfchobv: {g2.vgwycxsxjz.uwxkstolmf[1].dijhfchobv}")
    print(f"  door[2].dijhfchobv: {g2.vgwycxsxjz.uwxkstolmf[2].dijhfchobv}")

    # Also try L, R to see which directions work
    for d in 'UDLR':
        g3 = fresh()
        apply(g3, PREFIX + path + [d])
        new_p = pos(g3)
        if new_p != sw0:
            print(f"  can go {d} → {new_p}")


if __name__ == "__main__":
    main()
