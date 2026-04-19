"""R11L L5 solver: staged foot-placement search for paint absorption."""
import copy
import numpy as np
import arc_agi
from arcengine import GameAction

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


def get_collision_set(body_sprite, target_sprite):
    """Get all body positions where body collides with target."""
    orig = (body_sprite.x, body_sprite.y)
    positions = set()
    tw, th = target_sprite.width, target_sprite.height
    tx, ty = target_sprite.x, target_sprite.y
    bw, bh = body_sprite.width, body_sprite.height
    for bx in range(tx - bw, tx + tw + 1):
        for by in range(ty - bh, ty + th + 1):
            body_sprite.set_position(bx, by)
            if body_sprite.collides_with(target_sprite):
                positions.add((bx, by))
    body_sprite.set_position(*orig)
    return positions


def body_pos_from_feet(foot_positions, n_feet, bw=5, bh=5):
    """Compute body position from foot positions (game's integer arithmetic)."""
    sx = sum(fp[0] + 2 for fp in foot_positions)  # sum of foot centers x
    sy = sum(fp[1] + 2 for fp in foot_positions)
    cx = sx // n_feet
    cy = sy // n_feet
    return (cx - bw // 2, cy - bh // 2)


def find_foot_move_for_target(snap, body_name, foot_indices, target_set,
                               current_feet, step=1):
    """Find a single foot move that puts body in target_set.

    Returns list of (foot_local_idx, new_foot_pos, resulting_body_pos).
    """
    n = len(foot_indices)
    results = []
    walls = snap.yhfnp

    for fi_local in range(n):
        fi_global = foot_indices[fi_local]
        foot = snap.ftmaz[fi_global]
        fw, fh = foot.width, foot.height
        orig = (foot.x, foot.y)

        for fx in range(0, 64 - fw + 1, step):
            for fy in range(0, 64 - fh + 1, step):
                if (fx, fy) == current_feet[fi_local]:
                    continue
                # Check wall collision
                foot.set_position(fx, fy)
                blocked = any(foot.collides_with(w) for w in walls)
                if blocked:
                    foot.set_position(*orig)
                    continue
                foot.set_position(*orig)

                # Compute body position
                new_feet = list(current_feet)
                new_feet[fi_local] = (fx, fy)
                bpos = body_pos_from_feet(new_feet, n)
                if bpos in target_set:
                    results.append((fi_local, (fx, fy), bpos))

    return results


def find_two_foot_moves_for_target(snap, body_name, foot_indices, target_set,
                                    current_feet, step=2):
    """Find two foot moves that put body in target_set.

    Returns list of ((fi1, pos1), (fi2, pos2), resulting_body_pos).
    """
    n = len(foot_indices)
    results = []
    walls = snap.yhfnp

    # Precompute valid positions per foot
    valid_pos = {}
    for fi_local in range(n):
        fi_global = foot_indices[fi_local]
        foot = snap.ftmaz[fi_global]
        fw, fh = foot.width, foot.height
        orig = (foot.x, foot.y)
        valid = []
        for fx in range(0, 64 - fw + 1, step):
            for fy in range(0, 64 - fh + 1, step):
                foot.set_position(fx, fy)
                if not any(foot.collides_with(w) for w in walls):
                    valid.append((fx, fy))
        foot.set_position(*orig)
        valid_pos[fi_local] = valid

    # Try all pairs of moves
    for fi1 in range(n):
        for pos1 in valid_pos[fi1]:
            feet_after_1 = list(current_feet)
            feet_after_1[fi1] = pos1
            for fi2 in range(n):
                for pos2 in valid_pos[fi2]:
                    if fi2 == fi1 and pos2 == pos1:
                        continue
                    feet_after_2 = list(feet_after_1)
                    feet_after_2[fi2] = pos2
                    bpos = body_pos_from_feet(feet_after_2, n)
                    if bpos in target_set:
                        results.append(((fi1, pos1), (fi2, pos2), bpos))
                        if len(results) >= 100:
                            return results
    return results


def clicks_for_moves(moves, last_foot_local):
    """Count clicks for a sequence of (foot_local, pos) moves."""
    total = 0
    for fi, pos in moves:
        if fi != last_foot_local:
            total += 2  # select + move
        else:
            total += 1  # just move (already selected)
        last_foot_local = fi
    return total, last_foot_local


def verify_absorption(snap, body_name, foot_indices, move_sequence):
    """Verify a move sequence using the actual game engine."""
    g = copy.deepcopy(snap)
    env._game = g

    # Execute each move
    for fi_local, target_pos in move_sequence:
        fi_global = foot_indices[fi_local]
        foot = g.ftmaz[fi_global]
        # Select foot (click on it)
        obs = env.step(GameAction.ACTION6, data={"x": foot.x + 2, "y": foot.y + 2})
        # Move foot
        obs = env.step(GameAction.ACTION6, data={"x": target_pos[0] + 2, "y": target_pos[1] + 2})

    # Check absorption
    absorbed = list(g.fwqwj.get(f"bdkaz-{body_name}", []))
    # Check body position
    kignw = g.brdck[body_name]["kignw"]
    bpos = (kignw.x, kignw.y) if kignw else None
    # Check body colors
    if kignw:
        colors = {int(c) for c in np.unique(kignw.pixels) if c > 0}
    else:
        colors = set()

    return absorbed, bpos, colors, obs


def solve_body_staged(snap, body_name, foot_indices, obstacles, hand, max_clicks=20):
    """Solve one body: absorb all obstacles then reach hand.

    Uses staged search: for each obstacle, find moves to absorb it,
    then find moves to reach the hand.
    """
    g = snap
    n = len(foot_indices)
    kignw = g.brdck[body_name]["kignw"]

    # Get collision sets
    obs_coll = {}
    for obs in obstacles:
        obs_coll[obs.name] = get_collision_set(kignw, obs)
        print(f"    {obs.name}: {len(obs_coll[obs.name])} collision positions")

    hand_coll = get_collision_set(kignw, hand)
    print(f"    hand: {len(hand_coll)} collision positions")

    current_feet = [(g.ftmaz[fi].x, g.ftmaz[fi].y) for fi in foot_indices]
    print(f"    Initial feet: {current_feet}")
    print(f"    Initial body: {body_pos_from_feet(current_feet, n)}")

    # Try all permutations of obstacle absorption order
    from itertools import permutations
    best_solution = None

    for obs_order in permutations(obstacles):
        targets = [(obs.name, obs_coll[obs.name]) for obs in obs_order]
        targets.append(("hand", hand_coll))

        # For each target, try 1-move and 2-move solutions
        def search_stages(stage_idx, feet, last_foot, clicks_so_far, moves_so_far):
            nonlocal best_solution

            if best_solution and clicks_so_far >= best_solution[0]:
                return

            if stage_idx >= len(targets):
                # All targets hit — solution found
                if best_solution is None or clicks_so_far < best_solution[0]:
                    best_solution = (clicks_so_far, moves_so_far[:], last_foot)
                    print(f"    >>> Solution: {clicks_so_far} clicks, order={[o.name for o in obs_order]} <<<")
                return

            target_name, target_set = targets[stage_idx]

            # Try 1-move solutions
            one_moves = find_foot_move_for_target(
                snap, body_name, foot_indices, target_set, feet, step=1)
            for fi, pos, bpos in one_moves:
                new_feet = list(feet)
                new_feet[fi] = pos
                cost = 2 if fi != last_foot else 1
                new_clicks = clicks_so_far + cost
                if best_solution and new_clicks >= best_solution[0]:
                    continue
                moves_so_far.append((fi, pos))
                search_stages(stage_idx + 1, new_feet, fi, new_clicks, moves_so_far)
                moves_so_far.pop()

            # Try 2-move solutions
            two_moves = find_two_foot_moves_for_target(
                snap, body_name, foot_indices, target_set, feet, step=2)
            for (fi1, pos1), (fi2, pos2), bpos in two_moves:
                new_feet = list(feet)
                new_feet[fi1] = pos1
                new_feet[fi2] = pos2
                cost1 = 2 if fi1 != last_foot else 1
                cost2 = 2 if fi2 != fi1 else 1
                new_clicks = clicks_so_far + cost1 + cost2
                if best_solution and new_clicks >= best_solution[0]:
                    continue
                moves_so_far.append((fi1, pos1))
                moves_so_far.append((fi2, pos2))
                search_stages(stage_idx + 1, new_feet, fi2, new_clicks, moves_so_far)
                moves_so_far.pop()
                moves_so_far.pop()

        # Start search: foot_indices[0] is selected initially (game's default for ftmaz sorting)
        # Actually, we need to know which foot is initially selected
        # ftmaz is sorted by distance from origin. For yukft-2: foot[2] at (39,45) is closest.
        # Initial selected = local index 0 (which is foot_indices[0])
        search_stages(0, current_feet, 0, 0, [])

    return best_solution


if __name__ == "__main__":
    if not replay_to_l5():
        print("Failed to reach L5")
        exit(1)

    l5_snap = copy.deepcopy(env._game)
    g = l5_snap

    # === yukft (2 feet) ===
    print("\n=== Solving yukft ===")
    yukft_fi = [0, 1]
    yukft_obs = [o for o in g.nxahg if o.name in ("xigcb-txxvzpgkne", "xigcb-txxvzpyzud")]
    # Hand is on body "pgknepyzud" (which has no kignw — it's a target body)
    yukft_hand = g.dfugm["pgknepyzud"]["xwdrv"]
    print(f"  Obstacles: {[(o.name, o.x, o.y) for o in yukft_obs]}")
    print(f"  Hand: ({yukft_hand.x},{yukft_hand.y}) colors={set(int(c) for c in np.unique(yukft_hand.pixels) if c > 0)}")

    yukft_sol = solve_body_staged(l5_snap, "yukft", yukft_fi, yukft_obs, yukft_hand, 15)
    if yukft_sol:
        clicks, moves, last_foot = yukft_sol
        print(f"\n  YUKFT: {clicks} clicks, {len(moves)} moves")
        for fi, pos in moves:
            print(f"    foot[{fi}] -> ({pos[0]},{pos[1]})")

        # Verify
        absorbed, bpos, colors, obs = verify_absorption(
            l5_snap, "yukft", yukft_fi, moves)
        print(f"  Verify: absorbed={absorbed}, body={bpos}, colors={colors}")
    else:
        print("  YUKFT: NO SOLUTION")

    # === yukft-2 (3 feet) ===
    print("\n=== Solving yukft-2 ===")
    y2_fi = [2, 3, 4]
    y2_obs = [o for o in g.nxahg if o.name in ("xigcb-txxvzttyia", "xigcb-txxvzzjgrp")]
    y2_hand = g.dfugm["ttyiazjgrp"]["xwdrv"]
    print(f"  Obstacles: {[(o.name, o.x, o.y) for o in y2_obs]}")
    print(f"  Hand: ({y2_hand.x},{y2_hand.y}) colors={set(int(c) for c in np.unique(y2_hand.pixels) if c > 0)}")

    y2_sol = solve_body_staged(l5_snap, "yukft-2", y2_fi, y2_obs, y2_hand, 20)
    if y2_sol:
        clicks, moves, last_foot = y2_sol
        print(f"\n  YUKFT-2: {clicks} clicks, {len(moves)} moves")
        for fi, pos in moves:
            print(f"    foot[{fi}] -> ({pos[0]},{pos[1]})")

        # Verify
        absorbed, bpos, colors, obs = verify_absorption(
            l5_snap, "yukft-2", y2_fi, moves)
        print(f"  Verify: absorbed={absorbed}, body={bpos}, colors={colors}")
    else:
        print("  YUKFT-2: NO SOLUTION")

    if yukft_sol and y2_sol:
        total = yukft_sol[0] + y2_sol[0]
        print(f"\n=== TOTAL: {total} clicks (budget: 37) ===")
