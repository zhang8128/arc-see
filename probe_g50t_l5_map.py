"""G50T L5: initial reach + switch→door mapping + door/teleporter analysis."""
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
    g.perform_action(ActionInput(id=getattr(GameAction, ACTIONS[name])))


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def doors(g):
    return tuple((d.x, d.y, d.rotation, bool(d.dpdubazedr), bool(d.dijhfchobv))
                 for d in g.vgwycxsxjz.uwxkstolmf)


def sw_state(g):
    return tuple(getattr(h, 'dijhfchobv', None) for h in g.vgwycxsxjz.hamayflsib)


def bfs_reach(max_depth=35):
    g0 = fresh()
    start = pos(g0)
    print(f"L5 start: {start}, goal: (6, 42) → win at (7, 43)")
    print(f"Initial doors: {doors(g0)}")
    seen = {start: []}
    q = deque([(start, [])])
    while q:
        p, path = q.popleft()
        if len(path) >= max_depth:
            continue
        for name in 'UDLR':
            g = fresh()
            for a in path:
                do(g, a)
            do(g, name)
            np_ = pos(g)
            if np_ != p and np_ not in seen:
                seen[np_] = path + [name]
                q.append((np_, path + [name]))
    return seen


# Known entity locations for annotation
ANNOT = {
    (55, 25): 'sw[0]',
    (19, 37): 'sw[1]',
    (19, 25): 'sw[2]',
    (1, 7): 'sw[3]',
    (43, 37): 'ulhh[4]',
    (43, 49): 'ulhh[5]',
    (7, 43): 'WIN',
}


def main():
    reach = bfs_reach()
    print(f"\nReached {len(reach)} tiles:")
    for p in sorted(reach, key=lambda t: (t[1], t[0])):
        a = f"  <-- {ANNOT[p]}" if p in ANNOT else ""
        print(f"  {p}  via {''.join(reach[p])}{a}")

    for t in (ANNOT):
        if t not in reach:
            print(f"NOT reached: {t} ({ANNOT[t]})")

    # Test each reachable switch
    print("\n=== Switch → door mapping ===")
    for idx in range(4):
        targets = {0: (55,25), 1: (19,37), 2: (19,25), 3: (1,7)}
        sw_pos = targets[idx]
        if sw_pos not in reach:
            print(f"\nsw[{idx}] at {sw_pos}: not reachable")
            continue
        g = fresh()
        before_d = doors(g)
        for a in reach[sw_pos]:
            do(g, a)
        after_d = doors(g)
        print(f"\nsw[{idx}] at {sw_pos} (path {''.join(reach[sw_pos])}):")
        for i, (b, a_) in enumerate(zip(before_d, after_d)):
            if b != a_:
                print(f"  door[{i}] CHANGED: {b[:3]} -> {a_[:3]}  latched={a_[4]}")
            else:
                print(f"  door[{i}] unchanged at ({b[0]},{b[1]})")


if __name__ == "__main__":
    main()
