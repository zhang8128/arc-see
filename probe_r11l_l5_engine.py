"""R11L L5: game-engine-based search for yukft-2.

Uses deepcopy + actual env.step() for each candidate move.
Precomputes valid foot positions (wall-safe) first.
"""
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


def get_valid_centers(snap, fi_global, step=2):
    """Get wall-safe foot centers at given step size."""
    foot = snap.ftmaz[fi_global]
    fw, fh = foot.width, foot.height
    orig = (foot.x, foot.y)
    walls = snap.yhfnp
    valid = set()
    for fx in range(0, 64 - fw + 1, step):
        for fy in range(0, 64 - fh + 1, step):
            foot.set_position(fx, fy)
            if not any(foot.collides_with(w) for w in walls):
                valid.add((fx + 2, fy + 2))  # store as center
    foot.set_position(*orig)
    return valid


def body_pos(centers, n):
    sx = sum(c[0] for c in centers)
    sy = sum(c[1] for c in centers)
    return (sx // n - 2, sy // n - 2)


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


def required_sums(target_set, n):
    sums = set()
    for bx, by in target_set:
        for dx in range(n):
            for dy in range(n):
                sums.add((n * (bx + 2) + dx, n * (by + 2) + dy))
    return sums


def click_overlaps_foot(click_xy, foot_positions, skip_fi=None):
    """Check if click lands on any foot (5x5 bounding box)."""
    cx, cy = click_xy
    for fi, (fx, fy) in foot_positions.items():
        if fi == skip_fi:
            continue
        if fx <= cx < fx + 5 and fy <= cy < fy + 5:
            return fi
    return None


def solve_yukft2_staged(l5_snap, step=2):
    """Staged search: absorb ttyia, absorb zjgrp, reach hand."""
    g = l5_snap
    n = 3
    fi_globals = [2, 3, 4]
    kignw = g.brdck["yukft-2"]["kignw"]

    obs_ttyia = next(o for o in g.nxahg if "ttyia" in o.name)
    obs_zjgrp = next(o for o in g.nxahg if "zjgrp" in o.name)
    hand = g.dfugm["ttyiazjgrp"]["xwdrv"]

    coll_ttyia = get_collision_set(kignw, obs_ttyia)
    coll_zjgrp = get_collision_set(kignw, obs_zjgrp)
    coll_hand = get_collision_set(kignw, hand)

    sums_ttyia = required_sums(coll_ttyia, n)
    sums_zjgrp = required_sums(coll_zjgrp, n)
    sums_hand = required_sums(coll_hand, n)

    # Precompute valid centers for all feet
    print("  Precomputing valid centers...")
    valid = {}
    for fi in fi_globals:
        valid[fi] = get_valid_centers(l5_snap, fi, step=step)
        print(f"    foot[{fi}]: {len(valid[fi])} valid centers (step={step})")

    init_centers = {fi: (g.ftmaz[fi].x + 2, g.ftmaz[fi].y + 2) for fi in fi_globals}
    print(f"  Initial centers: {init_centers}")

    from itertools import permutations

    best = None
    max_clicks = 20

    for obs_order in permutations([
        ("ttyia", sums_ttyia),
        ("zjgrp", sums_zjgrp),
    ]):
        stages = list(obs_order) + [("hand", sums_hand)]
        print(f"\n  Order: {[s[0] for s in stages]}")

        def search(stage_idx, centers, last_fi, clicks, moves):
            nonlocal best
            if best and clicks >= best[0]:
                return
            if stage_idx >= len(stages):
                if best is None or clicks < best[0]:
                    best = (clicks, list(moves), dict(centers))
                    print(f"    >>> {clicks} clicks, {len(moves)} moves")
                return

            tname, target_sums = stages[stage_idx]
            cur_sum = tuple(sum(centers[fi][d] for fi in fi_globals) for d in range(2))

            # Already at target?
            if cur_sum in target_sums:
                search(stage_idx + 1, centers, last_fi, clicks, moves)

            # --- 1-move: move one foot to hit target ---
            for fi in fi_globals:
                cost = 1 if fi == last_fi else 2
                if clicks + cost >= (best[0] if best else max_clicks + 1):
                    continue
                old = centers[fi]
                for nc in valid[fi]:
                    if nc == old:
                        continue
                    new_sum = (cur_sum[0] - old[0] + nc[0], cur_sum[1] - old[1] + nc[1])
                    if new_sum not in target_sums:
                        continue
                    # Check click doesn't overlap other feet
                    foot_pos = {f: (centers[f][0]-2, centers[f][1]-2) for f in fi_globals}
                    if click_overlaps_foot(nc, foot_pos, skip_fi=fi):
                        continue
                    new_c = dict(centers)
                    new_c[fi] = nc
                    moves.append((fi, nc))
                    search(stage_idx + 1, new_c, fi, clicks + cost, moves)
                    moves.pop()

            # --- 2-move: move two different feet ---
            for fi1 in fi_globals:
                cost1 = 1 if fi1 == last_fi else 2
                for fi2 in fi_globals:
                    if fi2 == fi1:
                        continue
                    cost2 = 2  # always switch foot
                    total_cost = cost1 + cost2
                    if clicks + total_cost >= (best[0] if best else max_clicks + 1):
                        continue
                    old1 = centers[fi1]
                    old2 = centers[fi2]

                    for nc1 in valid[fi1]:
                        if nc1 == old1:
                            continue
                        # Check nc1 click doesn't overlap other feet
                        foot_pos = {f: (centers[f][0]-2, centers[f][1]-2) for f in fi_globals}
                        if click_overlaps_foot(nc1, foot_pos, skip_fi=fi1):
                            continue

                        int_sum = (cur_sum[0] - old1[0] + nc1[0], cur_sum[1] - old1[1] + nc1[1])

                        # For fi2: need nc2 such that int_sum - old2 + nc2 in target
                        for tsx, tsy in target_sums:
                            need_cx = tsx - int_sum[0] + old2[0]
                            need_cy = tsy - int_sum[1] + old2[1]
                            if (need_cx, need_cy) not in valid[fi2]:
                                continue
                            if (need_cx, need_cy) == old2:
                                continue
                            # Check nc2 click doesn't overlap fi1's new position or other feet
                            new_foot_pos = dict(foot_pos)
                            new_foot_pos[fi1] = (nc1[0]-2, nc1[1]-2)
                            if click_overlaps_foot((need_cx, need_cy), new_foot_pos, skip_fi=fi2):
                                continue

                            new_c = dict(centers)
                            new_c[fi1] = nc1
                            new_c[fi2] = (need_cx, need_cy)
                            moves.append((fi1, nc1))
                            moves.append((fi2, (need_cx, need_cy)))
                            search(stage_idx + 1, new_c, fi2, clicks + total_cost, moves)
                            moves.pop()
                            moves.pop()
                            # Early exit if we found something good
                            if best and clicks + total_cost >= best[0]:
                                return

        search(0, dict(init_centers), fi_globals[0], 0, [])

    return best


def main():
    if not replay_to_l5():
        print("Failed to reach L5")
        return

    l5_snap = copy.deepcopy(env._game)

    # === yukft: known solution (verified working) ===
    print("\n=== yukft: 4 clicks (verified) ===")
    yukft_moves = [(1, 9, 39), (1, 50, 7), (1, 11, 18)]

    # === yukft-2: search ===
    print("\n=== Solving yukft-2 ===")
    result = solve_yukft2_staged(l5_snap, step=2)

    if not result:
        print("  Trying step=1...")
        result = solve_yukft2_staged(l5_snap, step=1)

    if result:
        clicks, moves, final_centers = result
        print(f"\n  Solution: {clicks} clicks, {len(moves)} moves")
        for fi, (cx, cy) in moves:
            print(f"    foot[{fi}] -> center ({cx},{cy}) = foot ({cx-2},{cy-2})")

        # Verify with game engine
        print("\n=== Full verification ===")
        g = copy.deepcopy(l5_snap)
        env._game = g

        total_actions = 0
        last_fi = None

        # yukft moves
        for fi, tcx, tcy in yukft_moves:
            foot = g.ftmaz[fi]
            if fi != last_fi:
                obs = env.step(GameAction.ACTION6, data={"x": foot.x+2, "y": foot.y+2})
                total_actions += 1
            obs = env.step(GameAction.ACTION6, data={"x": tcx, "y": tcy})
            total_actions += 1
            last_fi = fi

        # yukft-2 moves
        for fi, (cx, cy) in moves:
            foot = g.ftmaz[fi]
            if fi != last_fi:
                obs = env.step(GameAction.ACTION6, data={"x": foot.x+2, "y": foot.y+2})
                total_actions += 1
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            total_actions += 1
            last_fi = fi
            # Check state after each move
            for bname in ("yukft-2",):
                kn = f"bdkaz-{bname}"
                absorbed = g.fwqwj.get(kn, [])
                kignw = g.brdck[bname]["kignw"]
                if absorbed or (kignw and any(v > 0 for v in np.unique(kignw.pixels))):
                    colors = {int(v) for v in np.unique(kignw.pixels) if v > 0} if kignw else set()
                    print(f"  After foot[{fi}]->({cx},{cy}): absorbed={absorbed} colors={colors} body=({kignw.x},{kignw.y})")
            if obs.levels_completed >= 5:
                print(f"\n  >>> L5 SOLVED! {total_actions} actions <<<")
                break

        if obs.levels_completed < 5:
            print(f"\n  NOT SOLVED after {total_actions} actions")
            for bname in ("yukft", "yukft-2"):
                kn = f"bdkaz-{bname}"
                absorbed = g.fwqwj.get(kn, [])
                kignw = g.brdck[bname]["kignw"]
                if kignw:
                    c = {int(v) for v in np.unique(kignw.pixels) if v > 0}
                    print(f"  {bname}: absorbed={absorbed} body=({kignw.x},{kignw.y}) colors={c}")
            for hname, hdata in g.dfugm.items():
                h = hdata["xwdrv"]
                hc = {int(v) for v in np.unique(h.pixels) if v > 0}
                print(f"  hand {hname}: ({h.x},{h.y}) colors={hc} matched={hdata['wugiv']}")
    else:
        print("\n  NO SOLUTION FOUND")


if __name__ == "__main__":
    main()
