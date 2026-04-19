"""G50T L3: reach BFS + switch/door mapping.

Goal: (18,18) → win at (19,19). Player starts (7,19). Just 2 tiles east.
3 switches, 3 doors, one door has dpdubazedr=True (special).
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
LEVEL = 2  # L3


def fresh():
    g = mod.G50t()
    g.set_level(LEVEL)
    return g


def do(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, ACTIONS[name])))


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def doors(g):
    return tuple((d.x, d.y, d.rotation, bool(d.dpdubazedr)) for d in g.vgwycxsxjz.uwxkstolmf)


def switches(g):
    return tuple(h.dijhfchobv for h in g.vgwycxsxjz.hamayflsib)


def bfs_reach(max_depth=25):
    start_g = fresh()
    start = pos(start_g)
    print(f"L3 start: {start}, goal: {(18,18)}, doors: {doors(start_g)}")
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


def main():
    reach = bfs_reach()
    print(f"\nReached {len(reach)} tiles:")
    for p in sorted(reach, key=lambda t: (t[1], t[0])):
        marker = ""
        if p == (19, 19):
            marker = "  <-- WIN tile"
        elif p == (19, 49):
            marker = "  <-- switch[0]"
        elif p == (37, 31):
            marker = "  <-- switch[1]"
        elif p == (31, 19):
            marker = "  <-- switch[2]"
        print(f"  {p}  via {''.join(reach[p])}{marker}")

    goal_reachable = (19, 19) in reach
    print(f"\nGoal (19,19) reachable without mechanics? {goal_reachable}")
    if goal_reachable:
        print(f"  Path: {''.join(reach[(19,19)])} ({len(reach[(19,19)])} moves)")

    # Test each reachable switch
    print("\n=== Switch → door mapping ===")
    for sw_idx, sw_pos in [(0, (19, 49)), (1, (37, 31)), (2, (31, 19))]:
        if sw_pos not in reach:
            print(f"\nswitch[{sw_idx}] at {sw_pos}: not directly reachable")
            continue
        g = fresh()
        before = doors(g)
        for a in reach[sw_pos]:
            do(g, a)
        after = doors(g)
        print(f"\nswitch[{sw_idx}] at {sw_pos}:")
        print(f"  switches now: {switches(g)}")
        for i, (b, a_) in enumerate(zip(before, after)):
            if b != a_:
                print(f"  door[{i}] MOVED: {b} -> {a_}")
            else:
                print(f"  door[{i}] unchanged: {b}")


if __name__ == "__main__":
    main()
