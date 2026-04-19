"""G50T L6: test each reachable switch."""
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
    g.set_level(5)
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
    return tuple((d.x, d.y, bool(d.dijhfchobv)) for d in g.vgwycxsxjz.uwxkstolmf)


def main():
    # Known initial doors:
    # [0]=(43,7) trans, [1]=(31,7) trans, [2]=(19,25) latch, [3]=(1,25) latch, [4]=(31,49) latch

    # Test sw[0] at (43,25) — path LLU
    g = fresh()
    apply(g, ['L', 'L', 'U'])
    print(f"on sw[0] (43,25): player={pos(g)} doors={doors(g)}")
    apply(g, ['D'])
    print(f"  off sw[0]: player={pos(g)} doors={doors(g)}")

    # Test sw[1] at (31,25) — path LLULL
    g = fresh()
    apply(g, ['L', 'L', 'U', 'L', 'L'])
    print(f"\non sw[1] (31,25): player={pos(g)} doors={doors(g)}")
    apply(g, ['D'])
    print(f"  off sw[1]: player={pos(g)} doors={doors(g)}")

    # After sw[0] latches/unlatches something, what's the new reach?
    # Walk to sw[0], walk off, BFS again.
    print("\n=== BFS after touching sw[0] once ===")
    tiles, _ = bfs_after(['L', 'L', 'U', 'D'])
    print(f"Reached {len(tiles)} tiles")

    # After touching sw[1] once
    print("\n=== BFS after touching sw[1] once ===")
    tiles, _ = bfs_after(['L', 'L', 'U', 'L', 'L', 'D'])
    print(f"Reached {len(tiles)} tiles")

    # After touching BOTH sw[0] and sw[1]
    print("\n=== BFS after touching sw[0] then sw[1] ===")
    # Walk to sw[0] (LLU), step off (D), walk to sw[1] (LL), step off (D)
    # Wait — from (43,25), LL goes to (31, 25) which is sw[1]. Path: LLULLD? Let me check
    # (55,31) L(49,31) L(43,31) U(43,25)=sw[0] D(43,31) L(37,31)? Is (37,31) in reach?
    # From reach list: (37, 25), (43, 25), (43, 31), (49, 31), (55, 31)
    # So (37, 31) NOT in reach. Can't go L from (43, 31).
    # Alt: stay on (43, 25), go L to (37, 25), L to (31, 25)=sw[1]
    tiles, _ = bfs_after(['L', 'L', 'U', 'L', 'L', 'D'])
    print(f"Reached {len(tiles)} tiles")

    # Full BFS from fresh - try the reach-explore
    print("\n=== Multi-toggle BFS: press sw[0] then walk everywhere ===")
    g = fresh()
    apply(g, ['L', 'L', 'U'])  # on sw[0]
    print(f"With sw[0] pressed: doors={doors(g)}")
    # Is the reach different from this state?


def bfs_after(prefix, max_depth=15):
    g0 = fresh()
    apply(g0, prefix)
    tiles = {pos(g0): []}
    q = deque([(pos(g0), [])])
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
    return tiles, None


if __name__ == "__main__":
    main()
