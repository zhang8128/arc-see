"""R11L L5 solver v2: multi-move stage support for yukft-2.

yukft: 4 clicks (solved).
yukft-2: needs 2+ moves per absorption stage since body = avg of 3 feet.
"""
import copy
import numpy as np
import arc_agi
from arcengine import GameAction
from itertools import permutations

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
    orig = (body_sprite.x, body_sprite.y)
    positions = set()
    tx, ty = target_sprite.x, target_sprite.y
    bw, bh = body_sprite.width, body_sprite.height
    tw, th = target_sprite.width, target_sprite.height
    for bx in range(tx - bw, tx + tw + 1):
        for by in range(ty - bh, ty + th + 1):
            body_sprite.set_position(bx, by)
            if body_sprite.collides_with(target_sprite):
                positions.add((bx, by))
    body_sprite.set_position(*orig)
    return positions


def body_pos(centers, n):
    sx = sum(c[0] for c in centers)
    sy = sum(c[1] for c in centers)
    return (sx // n - 2, sy // n - 2)


def get_valid_foot_positions(snap, foot_idx):
    foot = snap.ftmaz[foot_idx]
    fw, fh = foot.width, foot.height
    orig = (foot.x, foot.y)
    walls = snap.yhfnp
    valid = set()
    for fx in range(0, 64 - fw + 1):
        for fy in range(0, 64 - fh + 1):
            foot.set_position(fx, fy)
            if not any(foot.collides_with(w) for w in walls):
                valid.add((fx, fy))
    foot.set_position(*orig)
    return valid


def required_sums_for_target(target_set, n):
    sums = set()
    for bx, by in target_set:
        for dx in range(n):
            for dy in range(n):
                sums.add((n * (bx + 2) + dx, n * (by + 2) + dy))
    return sums


def solve_yukft2(l5_snap):
    """Solve yukft-2 with multi-move support.

    Strategy: try sequences of foot moves (up to 7 moves total for 3 targets).
    Use DFS with pruning.
    """
    g = l5_snap
    n = 3
    foot_globals = [2, 3, 4]
    kignw = g.brdck["yukft-2"]["kignw"]

    obs_ttyia = next(o for o in g.nxahg if "ttyia" in o.name)
    obs_zjgrp = next(o for o in g.nxahg if "zjgrp" in o.name)
    hand = g.dfugm["ttyiazjgrp"]["xwdrv"]

    coll_ttyia = get_collision_set(kignw, obs_ttyia)
    coll_zjgrp = get_collision_set(kignw, obs_zjgrp)
    coll_hand = get_collision_set(kignw, hand)

    sums_ttyia = required_sums_for_target(coll_ttyia, n)
    sums_zjgrp = required_sums_for_target(coll_zjgrp, n)
    sums_hand = required_sums_for_target(coll_hand, n)

    print(f"  ttyia: {len(coll_ttyia)} collision pos, {len(sums_ttyia)} sums")
    print(f"  zjgrp: {len(coll_zjgrp)} collision pos, {len(sums_zjgrp)} sums")
    print(f"  hand: {len(coll_hand)} collision pos, {len(sums_hand)} sums")

    # Precompute valid foot centers
    print("  Precomputing valid positions...")
    valid_centers = {}
    for fi in foot_globals:
        vp = get_valid_foot_positions(l5_snap, fi)
        valid_centers[fi] = {(fx + 2, fy + 2) for fx, fy in vp}
        print(f"    foot[{fi}]: {len(valid_centers[fi])} valid centers")

    init_centers = [(g.ftmaz[fi].x + 2, g.ftmaz[fi].y + 2) for fi in foot_globals]
    init_sum = tuple(sum(c[i] for c in init_centers) for i in range(2))

    # For each obstacle ordering, search for move sequences
    best = None
    max_clicks = 20

    for obs_order in permutations([(sums_ttyia, "ttyia"), (sums_zjgrp, "zjgrp")]):
        targets = list(obs_order) + [(sums_hand, "hand")]
        target_names = [t[1] for t in targets]
        print(f"\n  Trying order: {target_names}")

        # DFS: find move sequences that hit each target in order
        def dfs(centers, target_idx, last_foot_local, clicks, moves):
            nonlocal best
            if best and clicks >= best[0]:
                return
            if clicks > max_clicks:
                return

            target_sums, tname = targets[target_idx]
            cur_sum = (sum(c[0] for c in centers), sum(c[1] for c in centers))

            # Check if current position already hits this target
            if cur_sum in target_sums:
                if target_idx + 1 >= len(targets):
                    if best is None or clicks < best[0]:
                        best = (clicks, list(moves), list(centers), target_names[:])
                        print(f"    >>> {clicks} clicks! moves={len(moves)}")
                    return
                else:
                    dfs(centers, target_idx + 1, last_foot_local, clicks, moves)
                    # Also continue searching (might need to move more)

            # Try each foot move
            for fi_local in range(n):
                fi_global = foot_globals[fi_local]
                cost = 1 if fi_local == last_foot_local else 2
                if clicks + cost > max_clicks:
                    continue
                if best and clicks + cost >= best[0]:
                    continue

                old_cx, old_cy = centers[fi_local]

                for new_cx, new_cy in valid_centers[fi_global]:
                    if (new_cx, new_cy) == (old_cx, old_cy):
                        continue

                    new_sum = (cur_sum[0] - old_cx + new_cx, cur_sum[1] - old_cy + new_cy)

                    # Only proceed if this move hits the current target
                    # (greedy: each move must achieve something)
                    if new_sum not in target_sums:
                        continue

                    new_centers = list(centers)
                    new_centers[fi_local] = (new_cx, new_cy)

                    moves.append((fi_local, fi_global, new_cx - 2, new_cy - 2))

                    if target_idx + 1 >= len(targets):
                        if best is None or clicks + cost < best[0]:
                            best = (clicks + cost, list(moves), list(new_centers), target_names[:])
                            print(f"    >>> {clicks + cost} clicks! moves={len(moves)}")
                    else:
                        dfs(new_centers, target_idx + 1, fi_local, clicks + cost, moves)

                    moves.pop()

        # But the issue is: we might need 2 moves to reach a target (intermediate
        # move doesn't hit any target). So the greedy "each move must hit target"
        # fails. We need to allow intermediate moves.

        # Better approach: search for move sequences up to 2 moves per target stage.
        # For stage k, try all 1-move and 2-move combos that land in target_sums.

        def search_staged(stage_idx, centers, last_foot_local, total_clicks, all_moves):
            nonlocal best
            if best and total_clicks >= best[0]:
                return
            if stage_idx >= len(targets):
                if best is None or total_clicks < best[0]:
                    best = (total_clicks, list(all_moves), list(centers), target_names[:])
                    print(f"    >>> {total_clicks} clicks! moves={len(all_moves)}")
                return

            target_sums, tname = targets[stage_idx]
            cur_sum = (sum(c[0] for c in centers), sum(c[1] for c in centers))

            # Already at target?
            if cur_sum in target_sums:
                search_staged(stage_idx + 1, centers, last_foot_local, total_clicks, all_moves)

            # Try 1-move solutions
            for fi_local in range(n):
                fi_global = foot_globals[fi_local]
                cost = 1 if fi_local == last_foot_local else 2
                if total_clicks + cost >= (best[0] if best else max_clicks + 1):
                    continue

                old_cx, old_cy = centers[fi_local]
                for new_cx, new_cy in valid_centers[fi_global]:
                    if (new_cx, new_cy) == (old_cx, old_cy):
                        continue
                    new_sum = (cur_sum[0] - old_cx + new_cx, cur_sum[1] - old_cy + new_cy)
                    if new_sum not in target_sums:
                        continue

                    new_centers = list(centers)
                    new_centers[fi_local] = (new_cx, new_cy)
                    all_moves.append((fi_local, fi_global, new_cx - 2, new_cy - 2))
                    search_staged(stage_idx + 1, new_centers, fi_local,
                                  total_clicks + cost, all_moves)
                    all_moves.pop()

            # Try 2-move solutions (needed when 1 move can't reach target)
            # For each pair of moves:
            for fi1 in range(n):
                fi1_global = foot_globals[fi1]
                cost1 = 1 if fi1 == last_foot_local else 2
                if total_clicks + cost1 + 1 >= (best[0] if best else max_clicks + 1):
                    continue

                old1_cx, old1_cy = centers[fi1]

                # For each first move destination, compute intermediate sum
                # Then for each second move, check if final sum hits target
                # Optimization: for each second foot choice, the required
                # second position = target_sum - intermediate_sum + old_second_center
                for fi2 in range(n):
                    fi2_global = foot_globals[fi2]
                    cost2 = 1 if fi2 == fi1 else 2
                    total_cost = total_clicks + cost1 + cost2
                    if total_cost >= (best[0] if best else max_clicks + 1):
                        continue

                    if fi1 == fi2:
                        # Move same foot twice — second position overrides first
                        # Effectively just 1 move (skip, handled above)
                        # Unless the intermediate move accomplishes something else
                        # For now, skip (we only need 2 DIFFERENT feet)
                        continue

                    old2_cx, old2_cy = centers[fi2]

                    # For each first move of fi1:
                    for new1_cx, new1_cy in valid_centers[fi1_global]:
                        if (new1_cx, new1_cy) == (old1_cx, old1_cy):
                            continue
                        # Intermediate sum after move 1
                        int_sum_x = cur_sum[0] - old1_cx + new1_cx
                        int_sum_y = cur_sum[1] - old1_cy + new1_cy
                        # Required second foot center to hit each target sum
                        for tsx, tsy in target_sums:
                            need2_cx = tsx - int_sum_x + old2_cx
                            need2_cy = tsy - int_sum_y + old2_cy
                            if (need2_cx, need2_cy) in valid_centers[fi2_global]:
                                if (need2_cx, need2_cy) == (old2_cx, old2_cy):
                                    continue
                                new_centers = list(centers)
                                new_centers[fi1] = (new1_cx, new1_cy)
                                new_centers[fi2] = (need2_cx, need2_cy)
                                all_moves.append((fi1, fi1_global, new1_cx - 2, new1_cy - 2))
                                all_moves.append((fi2, fi2_global, need2_cx - 2, need2_cy - 2))
                                search_staged(stage_idx + 1, new_centers, fi2,
                                              total_cost, all_moves)
                                all_moves.pop()
                                all_moves.pop()

        search_staged(0, list(init_centers), 0, 0, [])

    return best


if __name__ == "__main__":
    if not replay_to_l5():
        print("Failed to reach L5")
        exit(1)

    l5_snap = copy.deepcopy(env._game)
    g = l5_snap

    # yukft solution (from v1): 4 clicks
    print("\n=== yukft: 4 clicks (known) ===")
    yukft_moves = [
        (1, 1, 4, 46),   # foot[1] -> (4,46)
        (1, 1, 48, 4),   # foot[1] -> (48,4)
        (1, 1, 1, 13),   # foot[1] -> (1,13)
    ]
    print("  Moves:")
    for fl, fg, fx, fy in yukft_moves:
        print(f"    foot[{fg}] -> ({fx},{fy})")

    # yukft-2 solution
    print("\n=== Solving yukft-2 ===")
    y2_sol = solve_yukft2(l5_snap)

    if y2_sol:
        clicks, moves, centers, order = y2_sol
        print(f"\n  YUKFT-2: {clicks} clicks, {len(moves)} moves, order={order}")
        for fl, fg, fx, fy in moves:
            print(f"    foot[{fg}] -> ({fx},{fy})")

        total = 4 + clicks
        print(f"\n=== TOTAL: {total} clicks (budget: 37) ===")

        # Full end-to-end verification
        print("\n=== Full verification ===")
        g2 = copy.deepcopy(l5_snap)
        env._game = g2

        # Play yukft moves
        all_clicks = []
        last_global = None
        for fl, fg, fx, fy in yukft_moves:
            foot = g2.ftmaz[fg]
            if fg != last_global:
                all_clicks.append((foot.x + 2, foot.y + 2))
            all_clicks.append((fx + 2, fy + 2))
            last_global = fg

        # Play yukft-2 moves
        for fl, fg, fx, fy in moves:
            foot = g2.ftmaz[fg]
            if fg != last_global:
                all_clicks.append((foot.x + 2, foot.y + 2))
            all_clicks.append((fx + 2, fy + 2))
            last_global = fg

        print(f"  Click sequence ({len(all_clicks)} clicks):")
        for i, (cx, cy) in enumerate(all_clicks):
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            state = "WIN" if obs.levels_completed >= 5 else f"lc={obs.levels_completed}"
            print(f"    {i+1}: ({cx},{cy}) -> {state}")
            if obs.levels_completed >= 5:
                print(f"\n  >>> L5 SOLVED in {i+1} clicks! <<<")
                break

        # Debug state
        for bname in ("yukft", "yukft-2"):
            kn = f"bdkaz-{bname}"
            absorbed = g2.fwqwj.get(kn, [])
            kignw = g2.brdck[bname]["kignw"]
            if kignw:
                c = {int(v) for v in np.unique(kignw.pixels) if v > 0}
                print(f"  {bname}: absorbed={absorbed}, body=({kignw.x},{kignw.y}), colors={c}")
        for hname, hdata in g2.dfugm.items():
            h = hdata["xwdrv"]
            hc = {int(v) for v in np.unique(h.pixels) if v > 0}
            print(f"  hand {hname}: ({h.x},{h.y}), colors={hc}, matched={hdata['wugiv']}")
    else:
        print("\n  YUKFT-2: NO SOLUTION FOUND")
