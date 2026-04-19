"""G50T L1 BFS — minimal state key approach.

Findings from probe_g50t.py:
- Player sprite at g.vgwycxsxjz.dzxunlkwxt, with int .x .y
- ACTION2=DOWN (+6y), ACTION4=RIGHT (+6x), each step = 6 pixels
- ACTION1, ACTION3, ACTION5 do nothing from L1 start (blocked or no-op)
- Pixels don't update on base layer; use deepcopy of engine state directly
"""
import copy
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTIONS = ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4', 'ACTION5']


def player(g):
    return g.vgwycxsxjz.dzxunlkwxt


def state_key(g):
    """Minimal state key: player (x, y)."""
    p = player(g)
    return (p.x, p.y)


def richer_key(g):
    """Richer key: add counters and any list lengths inside the engine."""
    eng = g.vgwycxsxjz
    p = player(g)
    return (
        p.x, p.y,
        # the big int counters we saw at engine root
        getattr(eng, 'yugzlzepkr', 0),
        getattr(eng, 'rlazdofsxb', 0),
        getattr(eng, 'vgpdqizwwm', 0),
    )


def is_won(g):
    return g._state.name == "WIN" or g._current_level_index > 0


def try_all_actions(level_idx=0, max_depth=100, key_fn=state_key):
    g = mod.G50t()
    g.set_level(level_idx)
    start_key = key_fn(g)
    print(f"L{level_idx+1} start key: {start_key}")

    seen = {start_key: 0}
    queue = deque([(g, [])])
    expanded = 0

    while queue:
        g, path = queue.popleft()
        expanded += 1
        if len(path) >= max_depth:
            continue
        for a in ACTIONS:
            g2 = copy.deepcopy(g)
            try:
                g2.perform_action(ActionInput(id=getattr(GameAction, a)))
            except Exception as e:
                continue
            k = key_fn(g2)
            if k in seen and seen[k] <= len(path) + 1:
                continue
            seen[k] = len(path) + 1

            if is_won(g2):
                print(f"  WIN at depth {len(path)+1}: {path + [a]}")
                return path + [a]
            queue.append((g2, path + [a]))

            if expanded % 1000 == 0:
                print(f"  expanded={expanded} frontier={len(queue)} seen={len(seen)} "
                      f"deepest={len(path)+1} pos={k[:2] if isinstance(k, tuple) else k}")
                if expanded > 20000:
                    print("  GIVING UP — state space too large")
                    return None
    print(f"  BFS exhausted. expanded={expanded} seen={len(seen)}")
    return None


def deeper_probe():
    """Push a few moves and look for things that change that our key doesn't capture."""
    g = mod.G50t()
    g.set_level(0)
    print("=== Walking around, tracking what changes ===")
    init_pos = (player(g).x, player(g).y)
    print(f"start pos: {init_pos}")

    # Walk right 4 times, down 4 times
    seq = ['ACTION4'] * 4 + ['ACTION2'] * 4
    for i, a in enumerate(seq):
        before = (player(g).x, player(g).y)
        g.perform_action(ActionInput(id=getattr(GameAction, a)))
        after = (player(g).x, player(g).y)
        moved = before != after
        eng = g.vgwycxsxjz
        print(f"  step {i+1} {a}: pos {before} -> {after} {'MOVED' if moved else 'BLOCKED'}")

    print("\nFinal state engine attrs (interesting ones):")
    eng = g.vgwycxsxjz
    for name in sorted(dir(eng)):
        if name.startswith('_'):
            continue
        try:
            v = getattr(eng, name)
        except Exception:
            continue
        if callable(v):
            continue
        if isinstance(v, (int, bool, float)):
            print(f"  {name}: {v}")


if __name__ == "__main__":
    deeper_probe()
    print()
    try_all_actions(level_idx=0, max_depth=60, key_fn=state_key)
