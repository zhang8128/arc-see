"""G50T L4: deep inspect ulhhdeoyok entities + BFS reach + switch mapping.

Entity type `ulhhdeoyok` is new — appears in hamayflsib list but alongside
lqtxaumfed switches. Dump all its attributes, test interactions.
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
    g.set_level(3)
    return g


def do(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, ACTIONS[name])))


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def doors(g):
    return tuple((d.x, d.y) for d in g.vgwycxsxjz.uwxkstolmf)


def hamay_state(g):
    """Return tuple of info about each hamay entity."""
    return tuple(
        (type(h).__name__, h.x, h.y,
         getattr(h, 'dijhfchobv', None),
         getattr(h, 'is_visible', None))
        for h in g.vgwycxsxjz.hamayflsib
    )


def dump_ulhhdeoyok(g):
    """Dump EVERY attribute of the ulhhdeoyok entities."""
    for i, h in enumerate(g.vgwycxsxjz.hamayflsib):
        if type(h).__name__ != 'ulhhdeoyok':
            continue
        print(f"\n  hamay[{i}] ulhhdeoyok at ({h.x}, {h.y}):")
        for a in sorted(dir(h)):
            if a.startswith('_'):
                continue
            try:
                v = getattr(h, a)
            except Exception:
                continue
            if callable(v):
                continue
            print(f"    {a} = {v!r}")


def main():
    g = fresh()
    print("=== L4 initial state ===")
    print(f"Player: {pos(g)}")
    print(f"Doors: {doors(g)}")
    print(f"Hamay state: {hamay_state(g)}")
    dump_ulhhdeoyok(g)

    # BFS reach
    print("\n=== BFS reach ===")
    start = pos(g)
    seen = {start: []}
    q = deque([(start, [])])
    while q:
        p, path = q.popleft()
        if len(path) >= 30:
            continue
        for name in 'UDLR':
            g2 = fresh()
            for a in path:
                do(g2, a)
            do(g2, name)
            np_ = pos(g2)
            if np_ != p and np_ not in seen:
                seen[np_] = path + [name]
                q.append((np_, path + [name]))
    print(f"Reached {len(seen)} tiles:")
    for p in sorted(seen, key=lambda t: (t[1], t[0])):
        marker = ""
        if p == (7, 49): marker = "  <-- WIN"
        elif p == (49, 25): marker = "  <-- switch[0]"
        elif p == (31, 25): marker = "  <-- switch[1]"
        elif p == (25, 37): marker = "  <-- ulhh[2]"
        elif p == (25, 49): marker = "  <-- ulhh[3]"
        print(f"  {p}  via {''.join(seen[p])}{marker}")

    # Test each switch
    print("\n=== Switch mapping ===")
    for idx, sw_pos in [(0, (49, 25)), (1, (31, 25))]:
        if sw_pos not in seen:
            print(f"\nswitch[{idx}] at {sw_pos}: not reachable")
            continue
        g2 = fresh()
        before_d = doors(g2)
        before_h = hamay_state(g2)
        for a in seen[sw_pos]:
            do(g2, a)
        after_d = doors(g2)
        after_h = hamay_state(g2)
        print(f"\nswitch[{idx}] at {sw_pos}:")
        print(f"  path: {''.join(seen[sw_pos])}")
        for i, (b, a_) in enumerate(zip(before_d, after_d)):
            if b != a_:
                print(f"  door[{i}] MOVED: {b} -> {a_}")
        for i, (b, a_) in enumerate(zip(before_h, after_h)):
            if b != a_:
                print(f"  hamay[{i}] CHANGED: {b} -> {a_}")

    # Test walking onto ulhhdeoyok[2] (25, 37) — what happens?
    print("\n=== Walking on ulhhdeoyok ===")
    ulhh_pos = (25, 37)
    if ulhh_pos in seen:
        g2 = fresh()
        for a in seen[ulhh_pos]:
            do(g2, a)
        print(f"On ulhh[2] at {ulhh_pos}:")
        print(f"  player: {pos(g2)}")
        print(f"  hamay: {hamay_state(g2)}")
        print(f"  doors: {doors(g2)}")
    else:
        print(f"ulhh[2] at {ulhh_pos}: not reachable directly")


if __name__ == "__main__":
    main()
