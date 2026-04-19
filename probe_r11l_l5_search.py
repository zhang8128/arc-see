"""R11L L5 search: find foot sequences that absorb both obstacles for each body."""
import copy
import numpy as np
import arc_agi
from arcengine import GameAction
from collections import deque

arcade = arc_agi.Arcade()
env = arcade.make("r11l-aa269680", render_mode=None)

L1 = [(36, 13), (26, 61), (42, 30)]


def replay_to_l5():
    env.reset()
    env.reset()
    for px, py in L1:
        obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
    from solve_r11l_v2 import solve_level
    for level in range(2, 5):
        snap = copy.deepcopy(env._game)
        clicks = solve_level(snap, level, level)
        if clicks:
            env._game = copy.deepcopy(snap)
            for cx, cy in clicks:
                obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
                if obs.levels_completed >= level:
                    break
    print(f"At L5: lc={obs.levels_completed}")
    return obs.levels_completed >= 4


def get_collision_set(body_sprite, obstacle_sprite):
    """Get all body positions where body collides with obstacle."""
    bw, bh = body_sprite.width, body_sprite.height
    ow, oh = obstacle_sprite.width, obstacle_sprite.height
    ox, oy = obstacle_sprite.x, obstacle_sprite.y
    orig_x, orig_y = body_sprite.x, body_sprite.y

    positions = set()
    for dx in range(-bw - ow, bw + ow + 1):
        for dy in range(-bh - oh, bh + oh + 1):
            bx, by = ox + dx, oy + dy
            body_sprite.set_position(bx, by)
            if body_sprite.collides_with(obstacle_sprite):
                positions.add((bx, by))

    body_sprite.set_position(orig_x, orig_y)
    return positions


def find_reachable_feet(snap, foot_indices, obstacles_list, wall_sprites):
    """For each foot, find where it can go (no collision with walls)."""
    reach = {}
    for fi in foot_indices:
        foot = snap.ftmaz[fi]
        fw, fh = foot.width, foot.height
        orig_x, orig_y = foot.x, foot.y
        valid = set()
        for x in range(0, 64 - fw + 1):
            for y in range(0, 64 - fh + 1):
                foot.set_position(x, y)
                blocked = False
                for w in wall_sprites:
                    if foot.collides_with(w):
                        blocked = True
                        break
                if not blocked:
                    valid.add((x, y))
        foot.set_position(orig_x, orig_y)
        reach[fi] = valid
        print(f"  foot[{fi}]: {len(valid)} reachable positions")
    return reach


def body_centroid(foot_positions, body_width=5, body_height=5):
    """Compute body position from foot positions (each is (x,y) of foot sprite)."""
    n = len(foot_positions)
    cx = sum(fp[0] + 2 for fp in foot_positions) // n  # integer division like game
    cy = sum(fp[1] + 2 for fp in foot_positions) // n
    return (cx - body_width // 2, cy - body_height // 2)


def search_absorption_sequence(snap, body_name, foot_indices, obstacle_sprites,
                                hand_sprite, reach_map, max_clicks):
    """BFS for foot movement sequences that absorb all obstacles and reach hand.

    State: (foot_positions_tuple, absorbed_set_frozen, selected_foot_or_none)
    Each click either selects a foot or moves the selected foot.
    """
    g = snap
    kignw = g.brdck[body_name]["kignw"]

    # Precompute collision sets for each obstacle
    obs_collision = {}
    for obs in obstacle_sprites:
        obs_collision[obs.name] = get_collision_set(kignw, obs)
        print(f"  Collision set for {obs.name}: {len(obs_collision[obs.name])} positions")

    # Collision set for hand
    hand_collision = get_collision_set(kignw, hand_sprite)
    print(f"  Collision set for hand: {len(hand_collision)} positions")

    # Build obstacle name→sprite map
    obs_map = {obs.name: obs for obs in obstacle_sprites}

    # Initial foot positions
    init_feet = tuple((g.ftmaz[fi].x, g.ftmaz[fi].y) for fi in foot_indices)
    init_absorbed = frozenset()

    # State: (feet_tuple, absorbed, last_selected_foot_idx_or_none)
    # After a foot is selected (costs 1 click), the next click moves it
    # Selecting: click on foot center; Moving: click on target position

    # Actually, in the game, clicking a foot selects it (if not already selected).
    # But foot[0] is already selected at start (self.tfhng = 0, pprcmbqpwi called).
    # For simplicity, model as: each "move" costs 2 clicks (select + move).
    # But if the foot is already selected, it's just 1 click.

    # Let me model it simpler: each "foot move" costs 2 clicks (select + dest).
    # The game starts with the first foot selected, so first move = 1 click.
    # But let's just count clicks properly.

    # Actually, re-reading the game: the initial state has self.tfhng = 0 and
    # pprcmbqpwi called on ftmaz[0]. So foot[0] is already selected.

    # For BFS, state = (feet_pos, absorbed_obstacles)
    # Action = (foot_index, target_pos) → costs 2 clicks if changing foot, 1 if same
    # But this is complex. Let me simplify: count total clicks.

    # Hmm, let me just do a coarser search first.
    # Discretize foot positions to step=2 to reduce state space.

    STEP = 2

    # Quantize foot positions
    def quantize(pos):
        return (pos[0] // STEP * STEP, pos[1] // STEP * STEP)

    def quantize_feet(feet):
        return tuple(quantize(f) for f in feet)

    # BFS with cost = number of clicks
    # State = (quantized_feet, absorbed)
    # For each state, try moving each foot to nearby positions

    init_state = (quantize_feet(init_feet), init_absorbed)

    # For selected foot tracking, initially foot_indices[0] is selected
    # We model: moving the already-selected foot = 1 click,
    # switching + moving = 2 clicks

    # State includes which foot was last moved (to know if switch needed)
    # (feet, absorbed, last_moved_foot_local_idx)
    init_state = (quantize_feet(init_feet), init_absorbed, 0)  # foot_indices[0] selected

    queue = deque()
    queue.append((init_state, 0, []))  # state, clicks_used, click_history
    visited = {init_state: 0}

    best = None

    print(f"\n  Starting BFS (max_clicks={max_clicks}, step={STEP})...")

    checked = 0
    while queue:
        state, clicks, history = queue.popleft()
        feet, absorbed, last_foot = state

        checked += 1
        if checked % 100000 == 0:
            print(f"  Checked {checked}, queue={len(queue)}, best={'None' if not best else best[0]}")

        # Check if all obstacles absorbed
        if len(absorbed) == len(obstacle_sprites):
            # Check if body at hand position
            bpos = body_centroid(list(feet))
            if bpos in hand_collision:
                if best is None or clicks < best[0]:
                    best = (clicks, history, feet)
                    print(f"  >>> SOLUTION FOUND: {clicks} clicks! <<<")
                    print(f"      History: {history}")
                    print(f"      Feet: {feet}")
                    # Don't stop — keep looking for better
                    continue

        if clicks >= max_clicks:
            continue
        if best and clicks >= best[0]:
            continue

        # Try moving each foot
        for fi_local, fi_global in enumerate(foot_indices):
            foot_cost = 1 if fi_local == last_foot else 2
            new_clicks = clicks + foot_cost

            if new_clicks > max_clicks:
                continue
            if best and new_clicks >= best[0]:
                continue

            # Get valid positions for this foot (from precomputed reachability)
            for tx in range(0, 64, STEP):
                for ty in range(0, 64, STEP):
                    target = (tx, ty)

                    if target == feet[fi_local]:
                        continue

                    # Check wall collision (approximate — skip for speed)
                    # We'll verify solutions exactly later

                    # Compute new feet
                    new_feet = list(feet)
                    new_feet[fi_local] = target
                    new_feet_t = tuple(new_feet)

                    # Compute new body position
                    bpos = body_centroid(new_feet)

                    # Check new absorptions
                    new_absorbed = set(absorbed)
                    for obs in obstacle_sprites:
                        if obs.name not in new_absorbed:
                            if bpos in obs_collision[obs.name]:
                                new_absorbed.add(obs.name)

                    new_absorbed_f = frozenset(new_absorbed)
                    new_state = (quantize_feet(new_feet_t), new_absorbed_f, fi_local)

                    if new_state in visited and visited[new_state] <= new_clicks:
                        continue
                    visited[new_state] = new_clicks

                    new_hist = history + [(fi_local, target)]
                    queue.append((new_state, new_clicks, new_hist))

    print(f"  BFS done: checked {checked} states")
    return best


if __name__ == "__main__":
    if not replay_to_l5():
        print("Failed to reach L5")
        exit(1)

    l5_snap = copy.deepcopy(env._game)
    g = l5_snap

    print("\n=== Analyzing yukft (2 feet) ===")
    yukft_feet = [0, 1]  # foot indices
    yukft_kignw = g.brdck["yukft"]["kignw"]
    yukft_obs = [o for o in g.nxahg if o.name in ("xigcb-txxvzpgkne", "xigcb-txxvzpyzud")]
    yukft_hand = g.dfugm["pgknepyzud"]["xwdrv"]

    print(f"  Body: {yukft_kignw.name} at ({yukft_kignw.x},{yukft_kignw.y})")
    print(f"  Hand: {yukft_hand.name} at ({yukft_hand.x},{yukft_hand.y}) colors={set(int(c) for c in np.unique(yukft_hand.pixels) if c > 0)}")
    for o in yukft_obs:
        print(f"  Obstacle: {o.name} at ({o.x},{o.y})")
    for fi in yukft_feet:
        f = g.ftmaz[fi]
        print(f"  foot[{fi}]: ({f.x},{f.y})")

    yukft_result = search_absorption_sequence(
        copy.deepcopy(l5_snap), "yukft", yukft_feet, yukft_obs, yukft_hand, {}, 15)

    if yukft_result:
        print(f"\n  YUKFT solution: {yukft_result[0]} clicks")
        print(f"  Moves: {yukft_result[1]}")
    else:
        print("\n  YUKFT: no solution found")

    print("\n=== Analyzing yukft-2 (3 feet) ===")
    y2_feet = [2, 3, 4]  # foot indices
    y2_kignw = g.brdck["yukft-2"]["kignw"]
    y2_obs = [o for o in g.nxahg if o.name in ("xigcb-txxvzttyia", "xigcb-txxvzzjgrp")]
    y2_hand = g.dfugm["ttyiazjgrp"]["xwdrv"]

    print(f"  Body: {y2_kignw.name} at ({y2_kignw.x},{y2_kignw.y})")
    print(f"  Hand: {y2_hand.name} at ({y2_hand.x},{y2_hand.y}) colors={set(int(c) for c in np.unique(y2_hand.pixels) if c > 0)}")
    for o in y2_obs:
        print(f"  Obstacle: {o.name} at ({o.x},{o.y})")
    for fi in y2_feet:
        f = g.ftmaz[fi]
        print(f"  foot[{fi}]: ({f.x},{f.y})")

    y2_result = search_absorption_sequence(
        copy.deepcopy(l5_snap), "yukft-2", y2_feet, y2_obs, y2_hand, {}, 20)

    if y2_result:
        print(f"\n  YUKFT-2 solution: {y2_result[0]} clicks")
        print(f"  Moves: {y2_result[1]}")
    else:
        print("\n  YUKFT-2: no solution found")
