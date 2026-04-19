"""SC25 BFS solver — find optimal solutions for all 6 levels."""
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

# Spell costs (clicks + auto-cast action)
SPELL_COST = {"resize": 5, "teleport": 4, "fireball": 4}

DIR_MAP = {"U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}


def act(g, d, data=None):
    return g.perform_action(ActionInput(id=d, data=data or {}))


def pos(g):
    p = g.cflwkfoggh
    if not p:
        return None
    return (p.x, p.y, p.scale)


def cast(g, slots):
    for (r, c) in slots:
        x, y = SLOT_XY[(r, c)]
        act(g, CLICK, {"x": x, "y": y})


def replay(level_idx, actions):
    """Replay a sequence of actions from level start. Returns game state."""
    g = mod.Sc25()
    g.set_level(level_idx)
    if level_idx == 0:
        act(g, UP)  # consume demo animation
    for a in actions:
        if a == "resize":
            cast(g, RESIZE_SLOTS)
        elif a == "teleport":
            cast(g, TELEPORT_SLOTS)
        elif a == "fireball":
            cast(g, FIREBALL_SLOTS)
        else:
            act(g, DIR_MAP[a])
    return g


def action_cost(actions):
    return sum(SPELL_COST.get(a, 1) for a in actions)


def state_key(g):
    """Extract a hashable state key. Includes position, scale, and door state."""
    p = g.cflwkfoggh
    if not p:
        return None
    # Track whether doors still exist
    has_doors = len(g.doors) > 0
    has_doors2 = len(g.second_doors) > 0
    return (p.x, p.y, p.scale, has_doors, has_doors2)


def bfs(level_idx, max_override=None):
    """BFS solve a single level."""
    g0 = mod.Sc25()
    g0.set_level(level_idx)
    if level_idx == 0:
        act(g0, UP)

    limit = max_override or g0.sykpecmoq or 50
    spells = g0.wdsxxkugj
    start_key = state_key(g0)
    print(f"Level {level_idx+1}: start={pos(g0)}, limit={limit}, spells={spells}")

    # Available spell actions
    avail_spells = []
    if "fpokrvgln" in spells:
        avail_spells.append("resize")
    if "jzukcpajs" in spells:
        avail_spells.append("teleport")
    if "aprnrzeyj" in spells:
        avail_spells.append("fireball")

    queue = deque()
    queue.append(([], 0))  # (path, cost)
    visited = {start_key}
    iters = 0

    while queue:
        path, cost = queue.popleft()
        iters += 1
        if iters % 5000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}")

        # Try moves
        for dname in ["U", "D", "L", "R"]:
            new_cost = cost + 1
            if new_cost > limit:
                continue
            new_path = path + [dname]
            g = replay(level_idx, new_path)
            if g._current_level_index > level_idx:
                print(f"  FOUND! cost={new_cost} ({iters} iters): {new_path}")
                return new_path, new_cost
            key = state_key(g)
            if key and key not in visited:
                visited.add(key)
                queue.append((new_path, new_cost))

        # Try spells
        for spell in avail_spells:
            spell_c = SPELL_COST[spell]
            new_cost = cost + spell_c
            if new_cost > limit:
                continue
            new_path = path + [spell]
            g = replay(level_idx, new_path)
            if g._current_level_index > level_idx:
                print(f"  FOUND (spell)! cost={new_cost} ({iters} iters): {new_path}")
                return new_path, new_cost
            key = state_key(g)
            if key and key not in visited:
                visited.add(key)
                queue.append((new_path, new_cost))

    print(f"  No solution found ({iters} iters, {len(visited)} states)")
    return None, None


def path_to_api_actions(path):
    """Convert BFS path to actual API action strings."""
    actions = []
    for a in path:
        if a == "resize":
            for (r, c) in RESIZE_SLOTS:
                x, y = SLOT_XY[(r, c)]
                actions.append(f"ACTION6:{x},{y}")
        elif a == "teleport":
            for (r, c) in TELEPORT_SLOTS:
                x, y = SLOT_XY[(r, c)]
                actions.append(f"ACTION6:{x},{y}")
        elif a == "fireball":
            for (r, c) in FIREBALL_SLOTS:
                x, y = SLOT_XY[(r, c)]
                actions.append(f"ACTION6:{x},{y}")
        elif a == "U":
            actions.append("ACTION1")
        elif a == "D":
            actions.append("ACTION2")
        elif a == "L":
            actions.append("ACTION3")
        elif a == "R":
            actions.append("ACTION4")
    return actions


if __name__ == "__main__":
    all_solutions = {}
    total_cost = 0

    for level in range(6):
        path, cost = bfs(level)
        if path:
            all_solutions[level] = path
            total_cost += cost
            api_actions = path_to_api_actions(path)
            print(f"  API actions ({len(api_actions)}): {api_actions}")
        else:
            print(f"  FAILED on level {level+1}")
            break
        print()

    print("=" * 60)
    print(f"Total actions: {total_cost}")
    print(f"Baseline: {sum([39, 5, 32, 33, 66, 41])}")  # 216
    print()
    for level, path in all_solutions.items():
        print(f"Level {level+1}: {action_cost(path)} actions: {path}")
