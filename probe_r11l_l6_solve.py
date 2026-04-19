"""R11L L6 solver: multi-obstacle paint puzzle with forbidden zone avoidance."""
import copy
import numpy as np
import arc_agi
from arcengine import GameAction
from itertools import permutations

arcade = arc_agi.Arcade()
env = arcade.make("r11l-aa269680", render_mode=None)
L1 = [(36, 13), (26, 61), (42, 30)]
L5_CLICKS = [
    (43,34), (9,39), (50,7), (11,18),
    (41,47), (48,36), (34,55), (58,44), (10,54),
    (52,55), (10,58), (50,6), (10,54), (48,2),
]

def replay_to_l6():
    env.reset(); env.reset()
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
                if obs.levels_completed >= level: break
    for cx, cy in L5_CLICKS:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        if obs.levels_completed >= 5: break
    print(f"At L6: lc={obs.levels_completed}", flush=True)
    return obs.levels_completed >= 5

def build_wall_mask(snap):
    mask = np.zeros((64, 64), dtype=bool)
    for w in snap.yhfnp:
        px = w.pixels
        for dy in range(w.height):
            for dx in range(w.width):
                wx, wy = w.x + dx, w.y + dy
                if 0 <= wx < 64 and 0 <= wy < 64 and px[dy, dx] != -1:
                    mask[wy, wx] = True
    return mask

def build_foot_shape(snap, fi):
    foot = snap.ftmaz[fi]
    px = foot.pixels
    shape = [(dx, dy) for dy in range(foot.height) for dx in range(foot.width) if px[dy, dx] != -1]
    return shape, foot.width, foot.height

def precompute_valid_centers(wall_mask, foot_shape, fw, fh, step=2):
    valid = set()
    for fx in range(0, 64 - fw + 1, step):
        for fy in range(0, 64 - fh + 1, step):
            if not any(wall_mask[fy + dy, fx + dx] for dx, dy in foot_shape):
                valid.add((fx + 2, fy + 2))
    return valid

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

def click_hits_foot(cx, cy, foot_positions, skip_fi=None):
    for fi, (fx, fy) in foot_positions.items():
        if fi == skip_fi: continue
        if fx <= cx < fx + 5 and fy <= cy < fy + 5: return True
    return False

def body_pos_from_sum(s, n):
    return (s[0] // n - 2, s[1] // n - 2)

def solve_body(init_centers, fi_globals, valid_centers, target_sums_list,
               forbidden_sums, n, max_clicks=20):
    """Staged search with forbidden zone avoidance.

    target_sums_list: ordered list of target sum sets
    forbidden_sums: set of (sum_x, sum_y) where body would hit a forbidden obstacle
    """
    best = [None]

    def search(stage_idx, centers, last_fi, clicks, moves):
        if best[0] and clicks >= best[0][0]: return
        if stage_idx >= len(target_sums_list):
            if best[0] is None or clicks < best[0][0]:
                best[0] = (clicks, list(moves))
                print(f"    >>> {clicks} clicks, {len(moves)} moves", flush=True)
            return

        target = target_sums_list[stage_idx]
        cur_sum = tuple(sum(centers[fi][d] for fi in fi_globals) for d in range(2))

        if cur_sum in target and cur_sum not in forbidden_sums:
            search(stage_idx + 1, centers, last_fi, clicks, moves)

        foot_pos = {fi: (centers[fi][0]-2, centers[fi][1]-2) for fi in fi_globals}

        # 1-move
        for fi in fi_globals:
            cost = 1 if fi == last_fi else 2
            if clicks + cost >= (best[0][0] if best[0] else max_clicks + 1): continue
            old = centers[fi]
            for tsx, tsy in target:
                ncx = tsx - cur_sum[0] + old[0]
                ncy = tsy - cur_sum[1] + old[1]
                if not (2 <= ncx <= 61 and 2 <= ncy <= 61): continue
                if (ncx, ncy) == old: continue
                if (ncx, ncy) not in valid_centers[fi]: continue
                if click_hits_foot(ncx, ncy, foot_pos, skip_fi=fi): continue
                # Check forbidden: body at new sum must not hit forbidden
                new_sum = (tsx, tsy)
                if new_sum in forbidden_sums: continue
                nc = dict(centers); nc[fi] = (ncx, ncy)
                moves.append((fi, ncx, ncy))
                search(stage_idx + 1, nc, fi, clicks + cost, moves)
                moves.pop()
                if best[0] and clicks + cost >= best[0][0]: return

        # 2-move
        for fi1 in fi_globals:
            cost1 = 1 if fi1 == last_fi else 2
            for fi2 in fi_globals:
                if fi2 == fi1: continue
                cost2 = 2
                tc = cost1 + cost2
                if clicks + tc >= (best[0][0] if best[0] else max_clicks + 1): continue
                old1, old2 = centers[fi1], centers[fi2]
                found = 0
                for nc1 in valid_centers[fi1]:
                    if nc1 == old1: continue
                    if click_hits_foot(nc1[0], nc1[1], foot_pos, skip_fi=fi1): continue
                    # Check intermediate position isn't forbidden
                    int_sum = (cur_sum[0] - old1[0] + nc1[0], cur_sum[1] - old1[1] + nc1[1])
                    if int_sum in forbidden_sums: continue
                    int_sx, int_sy = int_sum
                    for tsx, tsy in target:
                        nc2x = tsx - int_sx + old2[0]
                        nc2y = tsy - int_sy + old2[1]
                        if not (2 <= nc2x <= 61 and 2 <= nc2y <= 61): continue
                        if (nc2x, nc2y) == old2: continue
                        if (nc2x, nc2y) not in valid_centers[fi2]: continue
                        final_sum = (tsx, tsy)
                        if final_sum in forbidden_sums: continue
                        fp2 = dict(foot_pos); fp2[fi1] = (nc1[0]-2, nc1[1]-2)
                        if click_hits_foot(nc2x, nc2y, fp2, skip_fi=fi2): continue
                        nc = dict(centers); nc[fi1] = nc1; nc[fi2] = (nc2x, nc2y)
                        moves.append((fi1, nc1[0], nc1[1]))
                        moves.append((fi2, nc2x, nc2y))
                        search(stage_idx + 1, nc, fi2, clicks + tc, moves)
                        moves.pop(); moves.pop()
                        found += 1
                        if found >= 3 or (best[0] and clicks + tc >= best[0][0]): break
                    if found >= 3 or (best[0] and clicks + tc >= best[0][0]): break

    search(0, dict(init_centers), fi_globals[0], 0, [])
    return best[0]


def main():
    if not replay_to_l6():
        print("Failed"); return

    l6_snap = copy.deepcopy(env._game)
    g = l6_snap

    print("Building wall mask...", flush=True)
    wall_mask = build_wall_mask(g)
    foot_shape, fw, fh = build_foot_shape(g, 0)
    print(f"  Foot: {len(foot_shape)} pixels, {fw}x{fh}", flush=True)

    # Valid centers
    all_fi = [0, 1, 2, 3, 4]
    valid = {}
    for fi in all_fi:
        valid[fi] = precompute_valid_centers(wall_mask, foot_shape, fw, fh, step=2)
    print(f"  Valid centers: {len(valid[0])} per foot (step=2)", flush=True)

    # Body sprites
    kignw_y = g.brdck["yukft"]["kignw"]
    kignw_y2 = g.brdck["yukft-2"]["kignw"]

    # Target assignments
    # yukft -> hand ttyiaPinkpgkne colors {10,11,6}
    yukft_target_obs = [
        next(o for o in g.nxahg if o.name == "xigcb-gigctpgknezzepw"),  # color 10
        next(o for o in g.nxahg if o.name == "xigcb-ttyiazzepw"),       # color 11
        next(o for o in g.nxahg if o.name == "xigcb-txxvzPink"),        # color 6
    ]
    yukft_hand = g.dfugm["ttyiaPinkpgkne"]["xwdrv"]

    # yukft-2 -> hand kpaaczjgrppgkne colors {9,14,15}
    y2_target_obs = [
        next(o for o in g.nxahg if o.name == "xigcb-txxvzpgkneBottom"),  # color 9
        next(o for o in g.nxahg if o.name == "xigcb-zjgrp"),             # color 14
        next(o for o in g.nxahg if o.name == "xigcb-kpaaczzepw"),        # color 15
    ]
    y2_hand = g.dfugm["kpaaczjgrppgkne"]["xwdrv"]

    # Forbidden obstacles (not targets for either body, plus the other body's targets)
    all_obs = set(o.name for o in g.nxahg)
    yukft_target_names = set(o.name for o in yukft_target_obs)
    y2_target_names = set(o.name for o in y2_target_obs)

    yukft_forbidden = [o for o in g.nxahg if o.name not in yukft_target_names]
    y2_forbidden = [o for o in g.nxahg if o.name not in y2_target_names]

    print(f"\n  yukft targets: {[o.name for o in yukft_target_obs]}")
    print(f"  yukft forbidden: {[o.name for o in yukft_forbidden]}")
    print(f"  y2 targets: {[o.name for o in y2_target_obs]}")
    print(f"  y2 forbidden: {[o.name for o in y2_forbidden]}")

    # Compute collision and forbidden sum sets
    def compute_forbidden_sums(kignw, forbidden_obs, n):
        forbidden = set()
        for obs in forbidden_obs:
            coll = get_collision_set(kignw, obs)
            forbidden |= required_sums(coll, n)
        return forbidden

    print("\nComputing collision sets...", flush=True)

    # yukft (n=2)
    yukft_fi = [3, 4]
    yukft_coll = [get_collision_set(kignw_y, obs) for obs in yukft_target_obs]
    yukft_hand_coll = get_collision_set(kignw_y, yukft_hand)
    yukft_target_sums = [required_sums(c, 2) for c in yukft_coll]
    yukft_hand_sums = required_sums(yukft_hand_coll, 2)
    yukft_forbidden_sums = compute_forbidden_sums(kignw_y, yukft_forbidden, 2)
    print(f"  yukft: targets={[len(s) for s in yukft_target_sums]} hand={len(yukft_hand_sums)} forbidden={len(yukft_forbidden_sums)}", flush=True)

    # yukft-2 (n=3)
    y2_fi = [0, 1, 2]
    y2_coll = [get_collision_set(kignw_y2, obs) for obs in y2_target_obs]
    y2_hand_coll = get_collision_set(kignw_y2, y2_hand)
    y2_target_sums = [required_sums(c, 3) for c in y2_coll]
    y2_hand_sums = required_sums(y2_hand_coll, 3)
    y2_forbidden_sums = compute_forbidden_sums(kignw_y2, y2_forbidden, 3)
    print(f"  y2: targets={[len(s) for s in y2_target_sums]} hand={len(y2_hand_sums)} forbidden={len(y2_forbidden_sums)}", flush=True)

    # Solve yukft
    print("\n=== Solving yukft (2 feet) ===", flush=True)
    yukft_centers = {fi: (g.ftmaz[fi].x + 2, g.ftmaz[fi].y + 2) for fi in yukft_fi}
    print(f"  Centers: {yukft_centers}", flush=True)

    best_yukft = None
    for order in permutations(range(3)):
        targets = [yukft_target_sums[i] for i in order] + [yukft_hand_sums]
        names = [yukft_target_obs[i].name[:15] for i in order] + ["hand"]
        print(f"  Order: {names}", flush=True)
        sol = solve_body(yukft_centers, yukft_fi, valid, targets, yukft_forbidden_sums, 2, 18)
        if sol and (best_yukft is None or sol[0] < best_yukft[0]):
            best_yukft = sol
            print(f"  Best: {sol[0]} clicks", flush=True)

    # Solve yukft-2
    print("\n=== Solving yukft-2 (3 feet) ===", flush=True)
    y2_centers = {fi: (g.ftmaz[fi].x + 2, g.ftmaz[fi].y + 2) for fi in y2_fi}
    print(f"  Centers: {y2_centers}", flush=True)

    best_y2 = None
    for order in permutations(range(3)):
        targets = [y2_target_sums[i] for i in order] + [y2_hand_sums]
        names = [y2_target_obs[i].name[:15] for i in order] + ["hand"]
        print(f"  Order: {names}", flush=True)
        sol = solve_body(y2_centers, y2_fi, valid, targets, y2_forbidden_sums, 3, 18)
        if sol and (best_y2 is None or sol[0] < best_y2[0]):
            best_y2 = sol
            print(f"  Best: {sol[0]} clicks", flush=True)

    if not best_yukft or not best_y2:
        print("\nNO SOLUTION for one or both bodies", flush=True)
        return

    total = best_yukft[0] + best_y2[0]
    print(f"\n=== TOTAL: {total} clicks (budget: 45) ===", flush=True)
    print(f"  yukft: {best_yukft[0]} clicks, {len(best_yukft[1])} moves", flush=True)
    for fi, cx, cy in best_yukft[1]:
        print(f"    foot[{fi}] -> ({cx},{cy})", flush=True)
    print(f"  y2: {best_y2[0]} clicks, {len(best_y2[1])} moves", flush=True)
    for fi, cx, cy in best_y2[1]:
        print(f"    foot[{fi}] -> ({cx},{cy})", flush=True)

    # Full verification
    print("\n=== Verification ===", flush=True)
    g2 = copy.deepcopy(l6_snap)
    env._game = g2
    last_fi = None; total_actions = 0

    for body_moves, fi_list in [(best_yukft[1], yukft_fi), (best_y2[1], y2_fi)]:
        for fi_local_or_global, cx, cy in body_moves:
            fi = fi_local_or_global
            f = g2.ftmaz[fi]
            if fi != last_fi:
                env.step(GameAction.ACTION6, data={"x": f.x+2, "y": f.y+2})
                total_actions += 1
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            total_actions += 1
            last_fi = fi
            if obs.levels_completed >= 6:
                print(f"\n>>> L6 SOLVED! {total_actions} actions <<<", flush=True)
                print(f">>> ALL 6 LEVELS COMPLETE! <<<", flush=True)
                return

    print(f"\nNOT SOLVED after {total_actions} actions", flush=True)
    for bname in ("yukft", "yukft-2"):
        kn = f"bdkaz-{bname}"
        absorbed = g2.fwqwj.get(kn, [])
        kignw = g2.brdck[bname]["kignw"]
        c = {int(v) for v in np.unique(kignw.pixels) if v > 0} if kignw else set()
        print(f"  {bname}: absorbed={absorbed} colors={c}", flush=True)
    for hname, hdata in g2.dfugm.items():
        h = hdata["xwdrv"]
        hc = {int(v) for v in np.unique(h.pixels) if v > 0}
        print(f"  hand {hname}: colors={hc} matched={hdata['wugiv']}", flush=True)

if __name__ == "__main__":
    main()
