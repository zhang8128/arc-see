"""G50T L3: explore reach after latching door[2] via switch[2].

Prefix: UURRRRDD (walk from (7,19) to (31,19) = switch[2], door[2] latches).
Then BFS all reachable positions.

Also test each additional switch from here (switch[1] reachable? switch[0]?).
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
LATCH_PREFIX = list('UURRRRDD')  # (7,19)→(31,19), latches door[2]


def fresh():
    g = mod.G50t()
    g.set_level(2)
    return g


def do(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, ACTIONS[name])))


def apply(g, seq):
    for a in seq:
        do(g, a)


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def doors(g):
    return tuple((d.x, d.y) for d in g.vgwycxsxjz.uwxkstolmf)


def bfs_post_latch(max_depth=30):
    g0 = fresh()
    apply(g0, LATCH_PREFIX)
    start = pos(g0)
    print(f"Post-latch start: {start}, doors: {doors(g0)}")

    # Walk off switch[2] first so switch[2] doesn't confuse door state
    # Actually we want to know what tiles are reachable. Each probe replays from scratch.
    seen = {start: list(LATCH_PREFIX)}
    q = deque([(start, list(LATCH_PREFIX))])
    while q:
        p, path = q.popleft()
        if len(path) - len(LATCH_PREFIX) >= max_depth:
            continue
        for name in 'UDLR':
            g = fresh()
            apply(g, path + [name])
            np_ = pos(g)
            if np_ != p and np_ not in seen:
                seen[np_] = path + [name]
                q.append((np_, path + [name]))
    return seen


def main():
    reach = bfs_post_latch()
    print(f"\nReached {len(reach)} tiles after latching door[2]:")
    for p in sorted(reach, key=lambda t: (t[1], t[0])):
        short = ''.join(reach[p][len(LATCH_PREFIX):])
        marker = ""
        if p == (19, 19):
            marker = "  <-- WIN tile"
        elif p == (19, 49):
            marker = "  <-- switch[0]"
        elif p == (37, 31):
            marker = "  <-- switch[1]"
        elif p == (31, 19):
            marker = "  <-- switch[2] (already latched)"
        print(f"  {p}  post-latch path: '{short}'{marker}")

    # Is the goal (19, 19) directly reachable now?
    goal = (19, 19)
    print(f"\nGoal (19,19) reachable after latch? {goal in reach}")
    if goal in reach:
        full = reach[goal]
        print(f"  full path: {''.join(full)} ({len(full)} actions)")


if __name__ == "__main__":
    main()
