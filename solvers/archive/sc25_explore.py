"""SC25 explorer — use local game engine to understand mechanics and find solutions."""
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('sc25', 'environment_files/sc25/f9b21a2f/sc25.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
CLICK = GameAction.ACTION6

# Camera scale=1, offset=0 — display coords = grid coords
SLOT_XY = {
    (0,0): (25, 50), (0,1): (30, 50), (0,2): (35, 50),
    (1,0): (25, 55), (1,1): (30, 55), (1,2): (35, 55),
    (2,0): (25, 60), (2,1): (30, 60), (2,2): (35, 60),
}

# Spell patterns: which slots to toggle
TELEPORT_SLOTS  = [(0,0), (0,1), (1,1)]       # jzukcpajs
RESIZE_SLOTS    = [(0,1), (1,0), (1,2), (2,1)] # fpokrvgln
FIREBALL_SLOTS  = [(0,1), (1,1), (2,1)]        # aprnrzeyj


def make_game(level=0):
    g = mod.Sc25()
    g.set_level(level)
    return g


def act(g, action_id, data=None):
    """Perform an action (handles all animation frames internally)."""
    ai = ActionInput(id=action_id, data=data or {})
    return g.perform_action(ai)


def player_pos(g):
    p = g.cflwkfoggh
    if p:
        return (p.x, p.y, p.scale)
    return None


def click_slot(g, row, col):
    x, y = SLOT_XY[(row, col)]
    return act(g, CLICK, {"x": x, "y": y})


def cast_spell(g, slots):
    for (r, c) in slots:
        click_slot(g, r, c)


def explore_level(level_idx):
    """Explore a single level's mechanics."""
    g = make_game(level_idx)
    p = player_pos(g)
    print(f"\n=== Level {level_idx + 1} ===")
    print(f"Player: pos=({p[0]},{p[1]}), scale={p[2]}")
    print(f"Action limit: {g.sykpecmoq}")
    print(f"Spells: {g.wdsxxkugj}")

    # Test all 4 directions
    for d, name in [(UP, "UP"), (DOWN, "DOWN"), (LEFT, "LEFT"), (RIGHT, "RIGHT")]:
        g2 = make_game(level_idx)
        act(g2, d)
        p2 = player_pos(g2)
        print(f"  {name}: ({p[0]},{p[1]}) -> ({p2[0]},{p2[1]}), level={g2._current_level_index}")


def bfs_solve(level_idx, max_depth=None, include_spells=None):
    """BFS to find optimal move sequence for a level.

    Pure-Python BFS: replay from game engine each time (slow but correct).
    """
    g0 = make_game(level_idx)
    limit = g0.sykpecmoq or 50
    if max_depth:
        limit = min(limit, max_depth)
    start = player_pos(g0)
    avail_spells = g0.wdsxxkugj if not include_spells else include_spells

    print(f"\nBFS Level {level_idx + 1}: start={start}, limit={limit}, spells={avail_spells}")

    # State: (x, y, scale, doors_destroyed_flag, spell_cast_flags...)
    # For simplicity, track (x, y, scale, level_idx, action_count)
    # and expand with spell options

    # Actions: moves + optional spell casts
    MOVES = [(UP, "U"), (DOWN, "D"), (LEFT, "L"), (RIGHT, "R")]

    # Build available spell actions
    SPELL_ACTIONS = []
    if "fpokrvgln" in avail_spells:
        SPELL_ACTIONS.append(("resize", RESIZE_SLOTS))
    if "jzukcpajs" in avail_spells:
        SPELL_ACTIONS.append(("teleport", TELEPORT_SLOTS))
    if "aprnrzeyj" in avail_spells:
        SPELL_ACTIONS.append(("fireball", FIREBALL_SLOTS))

    queue = deque()
    queue.append([])  # empty action list
    visited = {(start[0], start[1], start[2])}

    best = None
    iterations = 0

    while queue:
        path = queue.popleft()
        iterations += 1

        if iterations % 5000 == 0:
            print(f"  iter={iterations}, queue={len(queue)}, depth={len(path)}, visited={len(visited)}")

        cost = 0
        for a in path:
            if a.startswith("S:"):
                spell_name = a[2:]
                if spell_name == "resize":
                    cost += 4
                elif spell_name == "teleport":
                    cost += 3
                elif spell_name == "fireball":
                    cost += 3
            else:
                cost += 1

        if cost >= limit:
            continue

        # Replay to get current state
        g = make_game(level_idx)
        for a in path:
            if a.startswith("S:"):
                spell_name = a[2:]
                if spell_name == "resize":
                    cast_spell(g, RESIZE_SLOTS)
                elif spell_name == "teleport":
                    cast_spell(g, TELEPORT_SLOTS)
                elif spell_name == "fireball":
                    cast_spell(g, FIREBALL_SLOTS)
            else:
                d = {"U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}[a]
                act(g, d)

        # Try each move
        for d, dname in MOVES:
            g2 = make_game(level_idx)
            for a in path:
                if a.startswith("S:"):
                    spell_name = a[2:]
                    if spell_name == "resize":
                        cast_spell(g2, RESIZE_SLOTS)
                    elif spell_name == "teleport":
                        cast_spell(g2, TELEPORT_SLOTS)
                    elif spell_name == "fireball":
                        cast_spell(g2, FIREBALL_SLOTS)
                else:
                    dd = {"U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}[a]
                    act(g2, dd)

            act(g2, d)
            p = player_pos(g2)

            if p is None or g2._current_level_index > level_idx:
                new_cost = cost + 1
                print(f"  FOUND! {new_cost} actions: {path + [dname]}")
                if best is None or new_cost < best[0]:
                    best = (new_cost, path + [dname])
                continue

            key = (p[0], p[1], p[2])
            if key not in visited:
                visited.add(key)
                queue.append(path + [dname])

        # Try spell casts
        for spell_name, slots in SPELL_ACTIONS:
            spell_cost = len(slots)
            if cost + spell_cost >= limit:
                continue

            g2 = make_game(level_idx)
            for a in path:
                if a.startswith("S:"):
                    sn = a[2:]
                    if sn == "resize":
                        cast_spell(g2, RESIZE_SLOTS)
                    elif sn == "teleport":
                        cast_spell(g2, TELEPORT_SLOTS)
                    elif sn == "fireball":
                        cast_spell(g2, FIREBALL_SLOTS)
                else:
                    dd = {"U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}[a]
                    act(g2, dd)

            cast_spell(g2, slots)
            p = player_pos(g2)

            if p is None or g2._current_level_index > level_idx:
                new_cost = cost + spell_cost
                sol = path + [f"S:{spell_name}"]
                print(f"  FOUND (spell)! {new_cost} actions: {sol}")
                if best is None or new_cost < best[0]:
                    best = (new_cost, sol)
                continue

            key = (p[0], p[1], p[2])
            if key not in visited:
                visited.add(key)
                queue.append(path + [f"S:{spell_name}"])

    print(f"BFS complete: {iterations} iterations, {len(visited)} states visited")
    if best:
        print(f"Best solution: {best[0]} actions: {best[1]}")
    else:
        print("No solution found!")
    return best


if __name__ == "__main__":
    # Explore all levels first
    for i in range(6):
        explore_level(i)

    # Then solve level by level
    print("\n" + "="*60)
    print("SOLVING LEVELS")
    print("="*60)

    result = bfs_solve(0, max_depth=20)
