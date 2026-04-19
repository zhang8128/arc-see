"""SC25 Level 6 BFS solver with full state tracking."""
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('sc25', 'environment_files/sc25/f9b21a2f/sc25.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
CLICK = GameAction.ACTION6

SLOT_XY = {
    (0,0): (25, 50), (0,1): (30, 50), (0,2): (35, 50),
    (1,0): (25, 55), (1,1): (30, 55), (1,2): (35, 55),
    (2,0): (25, 60), (2,1): (30, 60), (2,2): (35, 60),
}
RESIZE_SLOTS = [(0,1), (1,0), (1,2), (2,1)]
TELEPORT_SLOTS = [(0,0), (0,1), (1,1)]
FIREBALL_SLOTS = [(0,1), (1,1), (2,1)]

SPELL_COST = {"resize": 5, "teleport": 4, "fireball": 4}


def act(g, d, data=None):
    return g.perform_action(ActionInput(id=d, data=data or {}))


def pos(g):
    p = g.cflwkfoggh
    return (p.x, p.y, p.scale) if p else None


def cast(g, slots):
    for (r, c) in slots:
        act(g, CLICK, {"x": SLOT_XY[(r, c)][0], "y": SLOT_XY[(r, c)][1]})


def state_key(g):
    """Full state key for level 6."""
    p = g.cflwkfoggh
    if not p:
        return None
    return (
        p.x, p.y, p.scale,
        g.player_direction,
        len(g.doors) > 0,
        len(g.second_doors) > 0,
        g.current_teleport_index,
        g.current_small_teleport_index,
        len(g.energy_packs),
    )


def replay(actions):
    """Replay a sequence on level 6."""
    g = mod.Sc25()
    g.set_level(5)  # level 6 is index 5
    dir_map = {"U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}
    for a in actions:
        if a == "resize":
            cast(g, RESIZE_SLOTS)
        elif a == "teleport":
            cast(g, TELEPORT_SLOTS)
        elif a == "fireball":
            cast(g, FIREBALL_SLOTS)
        else:
            act(g, dir_map[a])
    return g


def action_cost(actions):
    return sum(SPELL_COST.get(a, 1) for a in actions)


def bfs():
    g0 = mod.Sc25()
    g0.set_level(5)
    limit = g0.sykpecmoq  # 60
    start_key = state_key(g0)
    print(f"Level 6 BFS: start={pos(g0)}, limit={limit}")
    print(f"Start key: {start_key}")

    queue = deque()
    queue.append(([], 0))
    visited = {start_key}
    iters = 0

    while queue:
        path, cost = queue.popleft()
        iters += 1
        if iters % 5000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)} cost={cost}")

        # Try moves
        for dname in ["U", "D", "L", "R"]:
            new_cost = cost + 1
            if new_cost > limit:
                continue
            new_path = path + [dname]
            g = replay(new_path)
            if g._current_level_index > 5:
                print(f"  FOUND! cost={new_cost} ({iters} iters): {new_path}")
                return new_path, new_cost
            key = state_key(g)
            if key and key not in visited:
                visited.add(key)
                queue.append((new_path, new_cost))

        # Try spells
        for spell in ["resize", "teleport", "fireball"]:
            sc = SPELL_COST[spell]
            new_cost = cost + sc
            if new_cost > limit:
                continue
            new_path = path + [spell]
            g = replay(new_path)
            if g._current_level_index > 5:
                print(f"  FOUND (spell)! cost={new_cost} ({iters} iters): {new_path}")
                return new_path, new_cost
            key = state_key(g)
            if key and key not in visited:
                visited.add(key)
                queue.append((new_path, new_cost))

    print(f"No solution found ({iters} iters, {len(visited)} states)")
    return None, None


if __name__ == "__main__":
    path, cost = bfs()
    if path:
        print(f"\nSolution ({cost} actions): {path}")
