"""R11L L5 solver v3: fast sum-space approach.

Skip wall collision during search (89% of positions are valid).
Verify solutions with actual game engine.
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


def required_sums(target_set, n):
    sums = set()
    for bx, by in target_set:
        for dx in range(n):
            for dy in range(n):
                sums.add((n * (bx + 2) + dx, n * (by + 2) + dy))
    return sums


# Foot centers range: foot 5x5 on 64x64 grid → foot x in [0,59], center in [2,61]
CENTER_MIN, CENTER_MAX = 2, 61


def solve_3foot(init_centers, target_sums_list, max_total_clicks=15):
    """Solve 3-foot body: find move sequence that hits targets in order.

    init_centers: [(cx0,cy0), (cx1,cy1), (cx2,cy2)]
    target_sums_list: [set_of_sums_for_target1, set_of_sums_for_target2, ...]
    max_total_clicks: budget

    Returns: (total_clicks, list_of_moves) where each move is (foot_local, new_center)
    """
    n = 3
    best = [None]  # mutable for closure

    def cur_sum(centers):
        return (sum(c[0] for c in centers), sum(c[1] for c in centers))

    def search(stage, centers, last_foot, clicks, moves):
        if best[0] and clicks >= best[0][0]:
            return
        if stage >= len(target_sums_list):
            if best[0] is None or clicks < best[0][0]:
                best[0] = (clicks, list(moves))
                print(f"    >>> {clicks} clicks, {len(moves)} moves")
            return

        target = target_sums_list[stage]
        s = cur_sum(centers)

        # Already at target?
        if s in target:
            search(stage + 1, centers, last_foot, clicks, moves)

        # --- 1-move solutions ---
        for fi in range(n):
            cost = 1 if fi == last_foot else 2
            if clicks + cost >= (best[0][0] if best[0] else max_total_clicks + 1):
                continue
            old_cx, old_cy = centers[fi]
            # We need (s[0] - old_cx + new_cx, s[1] - old_cy + new_cy) in target
            # So for each target sum (tsx, tsy):
            # new_cx = tsx - s[0] + old_cx
            # new_cy = tsy - s[1] + old_cy
            seen = set()
            for tsx, tsy in target:
                new_cx = tsx - s[0] + old_cx
                new_cy = tsy - s[1] + old_cy
                if CENTER_MIN <= new_cx <= CENTER_MAX and CENTER_MIN <= new_cy <= CENTER_MAX:
                    if (new_cx, new_cy) != (old_cx, old_cy) and (new_cx, new_cy) not in seen:
                        seen.add((new_cx, new_cy))
                        new_centers = list(centers)
                        new_centers[fi] = (new_cx, new_cy)
                        moves.append((fi, new_cx, new_cy))
                        search(stage + 1, new_centers, fi, clicks + cost, moves)
                        moves.pop()
                        # Limit branching: if we found a good solution, stop exploring
                        if best[0] and clicks + cost + 1 >= best[0][0]:
                            break

        # --- 2-move solutions (only if no 1-move found or improving) ---
        for fi1 in range(n):
            cost1 = 1 if fi1 == last_foot else 2
            for fi2 in range(n):
                if fi1 == fi2:
                    continue
                cost2 = 1 if fi2 == fi1 else 2  # always 2 since fi2 != fi1
                total_cost = cost1 + cost2
                if clicks + total_cost >= (best[0][0] if best[0] else max_total_clicks + 1):
                    continue

                old1_cx, old1_cy = centers[fi1]
                old2_cx, old2_cy = centers[fi2]

                # For each target sum (tsx, tsy):
                # new1_cx + new2_cx = tsx - s[0] + old1_cx + old2_cx ≡ K_x
                # new1_cy + new2_cy = tsy - s[1] + old1_cy + old2_cy ≡ K_y
                # For each valid new1_cx: new2_cx = K_x - new1_cx
                # For each valid new1_cy: new2_cy = K_y - new1_cy
                # Both new1 and new2 must be in [CENTER_MIN, CENTER_MAX]

                found_2move = 0
                for tsx, tsy in target:
                    if found_2move >= 3:
                        break
                    K_x = tsx - s[0] + old1_cx + old2_cx
                    K_y = tsy - s[1] + old1_cy + old2_cy

                    # new1_cx range: max(CENTER_MIN, K_x-CENTER_MAX) to min(CENTER_MAX, K_x-CENTER_MIN)
                    lo_x = max(CENTER_MIN, K_x - CENTER_MAX)
                    hi_x = min(CENTER_MAX, K_x - CENTER_MIN)
                    lo_y = max(CENTER_MIN, K_y - CENTER_MAX)
                    hi_y = min(CENTER_MAX, K_y - CENTER_MIN)

                    if lo_x > hi_x or lo_y > hi_y:
                        continue

                    # Pick middle of range (likely valid and balanced)
                    new1_cx = (lo_x + hi_x) // 2
                    new1_cy = (lo_y + hi_y) // 2
                    new2_cx = K_x - new1_cx
                    new2_cy = K_y - new1_cy

                    if (new1_cx, new1_cy) == (old1_cx, old1_cy):
                        new1_cx = lo_x if lo_x != old1_cx else hi_x
                        new2_cx = K_x - new1_cx
                    if (new2_cx, new2_cy) == (old2_cx, old2_cy):
                        continue
                    if not (CENTER_MIN <= new2_cx <= CENTER_MAX and CENTER_MIN <= new2_cy <= CENTER_MAX):
                        continue

                    new_centers = list(centers)
                    new_centers[fi1] = (new1_cx, new1_cy)
                    new_centers[fi2] = (new2_cx, new2_cy)
                    moves.append((fi1, new1_cx, new1_cy))
                    moves.append((fi2, new2_cx, new2_cy))
                    search(stage + 1, new_centers, fi2, clicks + total_cost, moves)
                    moves.pop()
                    moves.pop()
                    found_2move += 1

    search(0, list(init_centers), 0, 0, [])
    return best[0]


def solve_2foot(init_centers, target_sums_list, max_total_clicks=10):
    """Solve 2-foot body."""
    n = 2
    best = [None]

    def cur_sum(centers):
        return (sum(c[0] for c in centers), sum(c[1] for c in centers))

    def search(stage, centers, last_foot, clicks, moves):
        if best[0] and clicks >= best[0][0]:
            return
        if stage >= len(target_sums_list):
            if best[0] is None or clicks < best[0][0]:
                best[0] = (clicks, list(moves))
                print(f"    >>> {clicks} clicks, {len(moves)} moves")
            return

        target = target_sums_list[stage]
        s = cur_sum(centers)

        if s in target:
            search(stage + 1, centers, last_foot, clicks, moves)

        for fi in range(n):
            cost = 1 if fi == last_foot else 2
            if clicks + cost >= (best[0][0] if best[0] else max_total_clicks + 1):
                continue
            old_cx, old_cy = centers[fi]
            seen = set()
            for tsx, tsy in target:
                new_cx = tsx - s[0] + old_cx
                new_cy = tsy - s[1] + old_cy
                if CENTER_MIN <= new_cx <= CENTER_MAX and CENTER_MIN <= new_cy <= CENTER_MAX:
                    if (new_cx, new_cy) != (old_cx, old_cy) and (new_cx, new_cy) not in seen:
                        seen.add((new_cx, new_cy))
                        new_centers = list(centers)
                        new_centers[fi] = (new_cx, new_cy)
                        moves.append((fi, new_cx, new_cy))
                        search(stage + 1, new_centers, fi, clicks + cost, moves)
                        moves.pop()
                        if best[0] and clicks + cost + 1 >= best[0][0]:
                            break

    search(0, list(init_centers), 0, 0, [])
    return best[0]


def verify_body_with_engine(l5_snap, body_name, foot_globals, moves):
    """Execute moves through the actual game engine and check results."""
    g = copy.deepcopy(l5_snap)
    env._game = g

    last_global = None
    clicks = []
    for fi_local, new_cx, new_cy in moves:
        fi_global = foot_globals[fi_local]
        foot = g.ftmaz[fi_global]
        # Select foot if different
        if fi_global != last_global:
            clicks.append((foot.x + 2, foot.y + 2))
        # Move foot (click on center)
        clicks.append((new_cx, new_cy))
        last_global = fi_global

    for cx, cy in clicks:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})

    kn = f"bdkaz-{body_name}"
    absorbed = list(g.fwqwj.get(kn, []))
    kignw = g.brdck[body_name]["kignw"]
    if kignw:
        colors = {int(c) for c in np.unique(kignw.pixels) if c > 0}
        bpos = (kignw.x, kignw.y)
    else:
        colors = set()
        bpos = None

    return absorbed, bpos, colors, clicks, obs


def main():
    if not replay_to_l5():
        print("Failed to reach L5")
        return

    l5_snap = copy.deepcopy(env._game)
    g = l5_snap

    kignw_y = g.brdck["yukft"]["kignw"]
    kignw_y2 = g.brdck["yukft-2"]["kignw"]

    # Collision sets
    obs_pgkne = next(o for o in g.nxahg if "pgkne" in o.name)
    obs_pyzud = next(o for o in g.nxahg if "pyzud" in o.name)
    obs_ttyia = next(o for o in g.nxahg if "ttyia" in o.name)
    obs_zjgrp = next(o for o in g.nxahg if "zjgrp" in o.name)
    hand_yukft = g.dfugm["pgknepyzud"]["xwdrv"]
    hand_y2 = g.dfugm["ttyiazjgrp"]["xwdrv"]

    coll_pgkne = get_collision_set(kignw_y, obs_pgkne)
    coll_pyzud = get_collision_set(kignw_y, obs_pyzud)
    coll_hand_y = get_collision_set(kignw_y, hand_yukft)
    coll_ttyia = get_collision_set(kignw_y2, obs_ttyia)
    coll_zjgrp = get_collision_set(kignw_y2, obs_zjgrp)
    coll_hand_y2 = get_collision_set(kignw_y2, hand_y2)

    print(f"\nCollision sets: pgkne={len(coll_pgkne)} pyzud={len(coll_pyzud)} "
          f"hand_y={len(coll_hand_y)} ttyia={len(coll_ttyia)} "
          f"zjgrp={len(coll_zjgrp)} hand_y2={len(coll_hand_y2)}")

    # Required sums
    sums_pgkne = required_sums(coll_pgkne, 2)
    sums_pyzud = required_sums(coll_pyzud, 2)
    sums_hand_y = required_sums(coll_hand_y, 2)
    sums_ttyia = required_sums(coll_ttyia, 3)
    sums_zjgrp = required_sums(coll_zjgrp, 3)
    sums_hand_y2 = required_sums(coll_hand_y2, 3)

    print(f"Sum sets: pgkne={len(sums_pgkne)} pyzud={len(sums_pyzud)} "
          f"hand_y={len(sums_hand_y)} ttyia={len(sums_ttyia)} "
          f"zjgrp={len(sums_zjgrp)} hand_y2={len(sums_hand_y2)}")

    # === yukft (2 feet) ===
    print("\n=== Solving yukft (2 feet) ===")
    yukft_fi = [0, 1]
    yukft_centers = [(g.ftmaz[fi].x + 2, g.ftmaz[fi].y + 2) for fi in yukft_fi]
    print(f"  Centers: {yukft_centers}")

    best_yukft = None
    for obs_order in permutations([
        (sums_pgkne, "pgkne"), (sums_pyzud, "pyzud")
    ]):
        targets = [s for s, _ in obs_order] + [sums_hand_y]
        names = [n for _, n in obs_order] + ["hand"]
        print(f"  Order: {names}")
        sol = solve_2foot(yukft_centers, targets, 10)
        if sol and (best_yukft is None or sol[0] < best_yukft[0]):
            best_yukft = sol
            print(f"  Best so far: {sol[0]} clicks")

    if best_yukft:
        clicks, moves = best_yukft
        print(f"\n  YUKFT: {clicks} clicks, {len(moves)} moves")
        for fi, cx, cy in moves:
            print(f"    foot[{yukft_fi[fi]}] -> center ({cx},{cy}) = foot ({cx-2},{cy-2})")

        absorbed, bpos, colors, click_seq, obs = verify_body_with_engine(
            l5_snap, "yukft", yukft_fi, moves)
        print(f"  Verify: absorbed={absorbed}, body={bpos}, colors={colors}")
        if not absorbed:
            print(f"  *** VERIFICATION FAILED: no absorption! ***")
    else:
        print("  YUKFT: NO SOLUTION")
        return

    # === yukft-2 (3 feet) ===
    print("\n=== Solving yukft-2 (3 feet) ===")
    y2_fi = [2, 3, 4]
    y2_centers = [(g.ftmaz[fi].x + 2, g.ftmaz[fi].y + 2) for fi in y2_fi]
    print(f"  Centers: {y2_centers}")

    best_y2 = None
    for obs_order in permutations([
        (sums_ttyia, "ttyia"), (sums_zjgrp, "zjgrp")
    ]):
        targets = [s for s, _ in obs_order] + [sums_hand_y2]
        names = [n for _, n in obs_order] + ["hand"]
        print(f"  Order: {names}")
        sol = solve_3foot(y2_centers, targets, 15)
        if sol and (best_y2 is None or sol[0] < best_y2[0]):
            best_y2 = sol
            print(f"  Best so far: {sol[0]} clicks")

    if best_y2:
        clicks, moves = best_y2
        print(f"\n  YUKFT-2: {clicks} clicks, {len(moves)} moves")
        for fi, cx, cy in moves:
            print(f"    foot[{y2_fi[fi]}] -> center ({cx},{cy}) = foot ({cx-2},{cy-2})")

        absorbed, bpos, colors, click_seq, obs = verify_body_with_engine(
            l5_snap, "yukft-2", y2_fi, moves)
        print(f"  Verify: absorbed={absorbed}, body={bpos}, colors={colors}")
        if not absorbed:
            print(f"  *** VERIFICATION FAILED: no absorption! ***")
    else:
        print("  YUKFT-2: NO SOLUTION")
        return

    # === Combined verification ===
    total = best_yukft[0] + best_y2[0]
    print(f"\n=== TOTAL: {total} clicks (budget: 37) ===")

    print("\n=== Full end-to-end verification ===")
    g2 = copy.deepcopy(l5_snap)
    env._game = g2

    all_clicks = []
    last_global = None

    for body_moves, fi_list in [(best_yukft[1], yukft_fi), (best_y2[1], y2_fi)]:
        for fi_local, new_cx, new_cy in body_moves:
            fi_global = fi_list[fi_local]
            foot = g2.ftmaz[fi_global]
            if fi_global != last_global:
                all_clicks.append((foot.x + 2, foot.y + 2))
            all_clicks.append((new_cx, new_cy))
            last_global = fi_global

    print(f"Click sequence ({len(all_clicks)} raw clicks):")
    for i, (cx, cy) in enumerate(all_clicks):
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        state_str = "WIN" if obs.levels_completed >= 5 else f"lc={obs.levels_completed}"
        print(f"  {i+1}: ({cx},{cy}) -> {state_str}")
        if obs.levels_completed >= 5:
            print(f"\n  >>> L5 SOLVED in {i+1} clicks! <<<")
            all_clicks = all_clicks[:i+1]
            break

    if obs.levels_completed < 5:
        print(f"\n  Not solved! Debugging...")
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

    return all_clicks


if __name__ == "__main__":
    main()
