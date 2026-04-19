"""Fast TR87 solver: pure-Python BFS with game engine only for target finding.

The state transitions are trivial: cycle sprites up/down, select left/right.
BFS in pure Python is 1000x faster than replaying through the game engine.

The challenge: finding the target configuration. We use the game's bsqsshqpox()
method to check winning conditions.
"""
import importlib.util
import copy
import time
from collections import deque
from arcengine import GameAction

spec = importlib.util.spec_from_file_location('tr87', 'environment_files/tr87/cd924810/tr87.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

FULL = {GameAction.ACTION1: 'ACTION1', GameAction.ACTION2: 'ACTION2',
        GameAction.ACTION3: 'ACTION3', GameAction.ACTION4: 'ACTION4'}


def get_level_info(level_idx):
    """Extract starting configuration and cycle info."""
    g = mod.Tr87()
    g.full_reset()
    g.set_level(level_idx)

    alter_rules = g.current_level.get_data("alter_rules")
    double_translation = g.current_level.get_data("double_translation")
    tree_translation = g.current_level.get_data("tree_translation")

    # Get sprite cycle
    s = g.ztgmtnnufb[0]
    cycle = [s.name]
    current = s
    for _ in range(30):
        current = g.wpbnovjwkv(current, 1)
        if current.name == cycle[0]:
            break
        cycle.append(current.name)

    name_to_idx = {name: i for i, name in enumerate(cycle)}

    if alter_rules:
        # For alter_rules, the controllable items are in the rules
        all_sets = [s for rule in g.cifzvbcuwqe for s in rule]
        n_items = len(all_sets)
        start_indices = []
        for set_ in all_sets:
            set_indices = tuple(name_to_idx.get(s.name, 0) for s in set_)
            start_indices.append(set_indices)
    else:
        n_items = len(g.ztgmtnnufb)
        start_indices = [name_to_idx.get(s.name, 0) for s in g.ztgmtnnufb]

    return {
        "game": g,
        "n_items": n_items,
        "cycle_len": len(cycle),
        "cycle": cycle,
        "name_to_idx": name_to_idx,
        "start_indices": start_indices,
        "alter_rules": alter_rules,
        "double_translation": double_translation,
        "tree_translation": tree_translation,
    }


def find_target_brute(info):
    """Find target by brute-forcing all combinations and checking bsqsshqpox.

    Optimized: pre-compute sprite objects for each cycle position,
    swap in-place instead of deepcopy for each combo.
    """
    g = info["game"]
    n = info["n_items"]
    cycle_len = info["cycle_len"]
    cycle = info["cycle"]

    if info["alter_rules"]:
        return None  # too complex for brute force

    print(f"  Brute-forcing target ({cycle_len}^{n} = {cycle_len**n} combos)...")
    start_time = time.time()

    # Pre-compute all sprite objects for each position
    # For each bottom sprite slot, create all possible sprite objects
    all_sprites = []  # all_sprites[slot][cycle_idx] = sprite object
    for i in range(n):
        slot_sprites = [None] * cycle_len
        current = g.ztgmtnnufb[i]
        current_idx = info["name_to_idx"].get(current.name, 0)
        slot_sprites[current_idx] = current

        s = current
        for step in range(1, cycle_len):
            s = g.wpbnovjwkv(s, 1)
            idx = (current_idx + step) % cycle_len
            slot_sprites[idx] = s
        all_sprites.append(slot_sprites)

    # Save originals
    originals = list(g.ztgmtnnufb)

    from itertools import product
    checked = 0
    for combo in product(range(cycle_len), repeat=n):
        checked += 1
        # Swap sprites in-place
        for i, idx in enumerate(combo):
            g.ztgmtnnufb[i] = all_sprites[i][idx]
        if g.bsqsshqpox():
            elapsed = time.time() - start_time
            target_names = [cycle[idx] for idx in combo]
            print(f"  Found target at combo {combo} ({checked} checked, {elapsed:.1f}s)")
            print(f"  Target: {target_names}")
            # Restore originals
            for i in range(n):
                g.ztgmtnnufb[i] = originals[i]
            return list(combo)
        if checked % 100000 == 0:
            elapsed = time.time() - start_time
            print(f"  checked={checked} time={elapsed:.0f}s")

    # Restore originals
    for i in range(n):
        g.ztgmtnnufb[i] = originals[i]

    print(f"  No target found!")
    return None


def pure_bfs(start_indices, target_indices, n_items, cycle_len, max_depth=50):
    """Pure Python BFS — no game engine needed."""
    start = tuple(start_indices)
    target = tuple(target_indices)

    if start == target:
        return []

    # State: (sprite_indices_tuple, selected_index)
    s0 = (start, 0)
    visited = {s0}
    queue = deque([(s0, [])])

    while queue:
        (indices, sel), actions = queue.popleft()
        if len(actions) >= max_depth:
            continue

        for act in range(4):
            new_indices = indices
            new_sel = sel

            if act == 0:  # ACTION1 = up = -1
                lst = list(indices)
                lst[sel] = (lst[sel] - 1) % cycle_len
                new_indices = tuple(lst)
            elif act == 1:  # ACTION2 = down = +1
                lst = list(indices)
                lst[sel] = (lst[sel] + 1) % cycle_len
                new_indices = tuple(lst)
            elif act == 2:  # ACTION3 = select prev
                new_sel = (sel - 1) % n_items
            elif act == 3:  # ACTION4 = select next
                new_sel = (sel + 1) % n_items

            new_state = (new_indices, new_sel)

            if new_indices == target:
                act_map = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
                return actions + [act_map[act]]

            if new_state not in visited:
                visited.add(new_state)
                act_map = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
                queue.append((new_state, actions + [act_map[act]]))

    return None


def solve_level(level_idx):
    """Solve a single level."""
    info = get_level_info(level_idx)

    print(f"  n_items={info['n_items']}, cycle={info['cycle_len']}, "
          f"alter={info['alter_rules']}, double={info['double_translation']}, "
          f"tree={info['tree_translation']}")
    print(f"  Start: {info['start_indices']}")

    if info["alter_rules"]:
        # Use game-engine BFS for alter_rules levels
        print(f"  Using game-engine BFS for alter_rules level")
        return solve_engine_bfs(level_idx)

    # Find target
    target = find_target_brute(info)
    if target is None:
        print(f"  Could not find target!")
        return None

    # Pure Python BFS
    print(f"  Running pure-Python BFS...")
    start = time.time()
    actions = pure_bfs(info["start_indices"], target, info["n_items"], info["cycle_len"])
    elapsed = time.time() - start

    if actions:
        print(f"  BFS found {len(actions)} actions in {elapsed:.3f}s")
        # Verify
        g = mod.Tr87()
        g.full_reset()
        g.set_level(level_idx)
        for a in actions:
            g.action.id = a
            g.step()
            g.complete_action()
        if g.yfetxjexviz >= 0:
            return actions
        else:
            print(f"  Verification FAILED!")
            return None
    else:
        print(f"  No solution found!")
        return None


def solve_engine_bfs(level_idx, max_depth=40):
    """BFS using game engine (for alter_rules levels)."""
    g = mod.Tr87()
    g.full_reset()
    g.set_level(level_idx)
    snapshot = copy.deepcopy(g)

    def get_state(g):
        if hasattr(g, 'cifzvbcuwqe') and g.current_level.get_data("alter_rules"):
            all_sets = [s for rule in g.cifzvbcuwqe for s in rule]
            names = tuple(tuple(s.name for s in set_) for set_ in all_sets)
        else:
            names = tuple(s.name for s in g.ztgmtnnufb)
        return (names, g.qvtymdcqear_index)

    ACTS = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4]
    visited = {}
    queue = deque()
    start = time.time()

    for first_act in ACTS:
        g0 = copy.deepcopy(snapshot)
        g0.action.id = first_act
        g0.step()
        g0.complete_action()
        if g0.yfetxjexviz >= 0:
            return [first_act]
        s0 = get_state(g0)
        if s0 not in visited:
            visited[s0] = [first_act]
            queue.append((s0, [first_act]))

    checked = 0
    while queue:
        state, actions = queue.popleft()
        if len(actions) >= max_depth:
            continue
        for act in ACTS:
            new_actions = actions + [act]
            checked += 1

            g2 = copy.deepcopy(snapshot)
            for a in new_actions:
                g2.action.id = a
                g2.step()
                g2.complete_action()

            if g2.yfetxjexviz >= 0:
                elapsed = time.time() - start
                print(f"  BFS: {len(new_actions)} actions, {checked} checked, {elapsed:.1f}s")
                return new_actions

            ns = get_state(g2)
            if ns not in visited:
                visited[ns] = new_actions
                queue.append((ns, new_actions))

            if checked % 5000 == 0:
                elapsed = time.time() - start
                print(f"  BFS: checked={checked} states={len(visited)} time={elapsed:.0f}s")

    return None


def main():
    solutions = {}

    for level_idx in range(6):
        level_num = level_idx + 1
        print(f"\n{'='*50}")
        print(f"Level {level_num}")
        print(f"{'='*50}")

        sol = solve_level(level_idx)
        if sol:
            sol_str = ' '.join(FULL[a] for a in sol)
            print(f"  Solution: {len(sol)} actions ✓")
            print(f"  {sol_str}")
            solutions[level_num] = sol
        else:
            print(f"  FAILED!")

    # Verify chain
    if len(solutions) == 6:
        print(f"\n{'='*50}")
        print("API VERIFICATION")
        print(f"{'='*50}")

        import arc_agi
        arcade = arc_agi.Arcade()
        env = arcade.make('tr87-cd924810', render_mode=None)
        env.reset()

        total = 0
        for lv in range(1, 7):
            for a in solutions[lv]:
                result = env.step(a)
            total += len(solutions[lv])
            print(f"  Level {lv}: {len(solutions[lv]):3d} actions, completed={result.levels_completed}")

        print(f"\n  Total: {total} actions, State: {result.state}")

        if str(result.state) == "GameState.WIN":
            print("\n  ALL VERIFIED! ✓")
            print("\nSOLUTIONS = {")
            for lv in range(1, 7):
                sol_str = ' '.join(FULL[a] for a in solutions[lv])
                print(f'    {lv}: "{sol_str}",  # {len(solutions[lv])} actions')
            print("}")


if __name__ == "__main__":
    main()
