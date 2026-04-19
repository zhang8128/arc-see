"""R11L L6: fix wall mask by using kignw sprite shape (known 21px cross)."""
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
    return obs.levels_completed >= 5

# Reuse the solver from probe_r11l_l5_fast2 / probe_r11l_l6_solve
# but fix the foot shape

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

def precompute_valid_centers_engine(snap, fi, step=2):
    """Use actual collides_with for accurate wall checking."""
    foot = snap.ftmaz[fi]
    fw, fh = foot.width, foot.height
    orig = (foot.x, foot.y)
    walls = snap.yhfnp
    valid = set()
    for fx in range(0, 64 - fw + 1, step):
        for fy in range(0, 64 - fh + 1, step):
            foot.set_position(fx, fy)
            if not any(foot.collides_with(w) for w in walls):
                valid.add((fx + 2, fy + 2))
    foot.set_position(*orig)
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

def solve_body(init_centers, fi_globals, valid_centers, target_sums_list,
               forbidden_sums, n, max_clicks=20):
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
                new_sum = (tsx, tsy)
                if new_sum in forbidden_sums: continue
                nc = dict(centers); nc[fi] = (ncx, ncy)
                moves.append((fi, ncx, ncy))
                search(stage_idx + 1, nc, fi, clicks + cost, moves)
                moves.pop()
                if best[0] and clicks + cost >= best[0][0]: return
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
                    int_sum = (cur_sum[0] - old1[0] + nc1[0], cur_sum[1] - old1[1] + nc1[1])
                    if int_sum in forbidden_sums: continue
                    for tsx, tsy in target:
                        nc2x = tsx - int_sum[0] + old2[0]
                        nc2y = tsy - int_sum[1] + old2[1]
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

    # Use actual collides_with for wall checking (slower but accurate)
    print("Precomputing valid centers (engine-based, step=2)...", flush=True)
    all_fi = [0, 1, 2, 3, 4]
    valid = {}
    for fi in all_fi:
        valid[fi] = precompute_valid_centers_engine(l6_snap, fi, step=2)
        print(f"  foot[{fi}]: {len(valid[fi])} valid centers", flush=True)

    kignw_y = g.brdck["yukft"]["kignw"]
    kignw_y2 = g.brdck["yukft-2"]["kignw"]

    yukft_target_obs = [
        next(o for o in g.nxahg if "gigctpgknezzepw" in o.name),
        next(o for o in g.nxahg if "ttyiazzepw" in o.name),
        next(o for o in g.nxahg if "txxvzPink" in o.name),
    ]
    yukft_hand = g.dfugm["ttyiaPinkpgkne"]["xwdrv"]
    y2_target_obs = [
        next(o for o in g.nxahg if "txxvzpgkneBottom" in o.name),
        next(o for o in g.nxahg if o.name == "xigcb-zjgrp"),
        next(o for o in g.nxahg if "kpaaczzepw" in o.name),
    ]
    y2_hand = g.dfugm["kpaaczjgrppgkne"]["xwdrv"]

    yukft_target_names = set(o.name for o in yukft_target_obs)
    y2_target_names = set(o.name for o in y2_target_obs)
    yukft_forbidden = [o for o in g.nxahg if o.name not in yukft_target_names]
    y2_forbidden = [o for o in g.nxahg if o.name not in y2_target_names]

    def compute_forbidden_sums(kignw, forbidden_obs, n):
        forbidden = set()
        for obs in forbidden_obs:
            coll = get_collision_set(kignw, obs)
            forbidden |= required_sums(coll, n)
        return forbidden

    print("Computing collision/forbidden sets...", flush=True)
    yukft_fi = [3, 4]
    yukft_target_sums = [required_sums(get_collision_set(kignw_y, o), 2) for o in yukft_target_obs]
    yukft_hand_sums = required_sums(get_collision_set(kignw_y, yukft_hand), 2)
    yukft_forbidden_sums = compute_forbidden_sums(kignw_y, yukft_forbidden, 2)

    y2_fi = [0, 1, 2]
    y2_target_sums = [required_sums(get_collision_set(kignw_y2, o), 3) for o in y2_target_obs]
    y2_hand_sums = required_sums(get_collision_set(kignw_y2, y2_hand), 3)
    y2_forbidden_sums = compute_forbidden_sums(kignw_y2, y2_forbidden, 3)

    print(f"  yukft forbidden: {len(yukft_forbidden_sums)}", flush=True)
    print(f"  y2 forbidden: {len(y2_forbidden_sums)}", flush=True)

    # Solve yukft
    print("\n=== Solving yukft ===", flush=True)
    yukft_centers = {fi: (g.ftmaz[fi].x + 2, g.ftmaz[fi].y + 2) for fi in yukft_fi}
    best_yukft = None
    for order in permutations(range(3)):
        targets = [yukft_target_sums[i] for i in order] + [yukft_hand_sums]
        sol = solve_body(yukft_centers, yukft_fi, valid, targets, yukft_forbidden_sums, 2, 18)
        if sol and (best_yukft is None or sol[0] < best_yukft[0]):
            best_yukft = sol

    # Solve yukft-2
    print("\n=== Solving yukft-2 ===", flush=True)
    y2_centers = {fi: (g.ftmaz[fi].x + 2, g.ftmaz[fi].y + 2) for fi in y2_fi}
    best_y2 = None
    for order in permutations(range(3)):
        targets = [y2_target_sums[i] for i in order] + [y2_hand_sums]
        sol = solve_body(y2_centers, y2_fi, valid, targets, y2_forbidden_sums, 3, 18)
        if sol and (best_y2 is None or sol[0] < best_y2[0]):
            best_y2 = sol

    if not best_yukft or not best_y2:
        print("NO SOLUTION"); return

    total = best_yukft[0] + best_y2[0]
    print(f"\n=== TOTAL: {total} clicks (budget: 45) ===", flush=True)
    for label, sol, fi_list in [("yukft", best_yukft, yukft_fi), ("y2", best_y2, y2_fi)]:
        print(f"  {label}: {sol[0]} clicks, {len(sol[1])} moves", flush=True)
        for fi, cx, cy in sol[1]:
            print(f"    foot[{fi}] -> ({cx},{cy})", flush=True)

    # Verification
    print("\n=== Verification ===", flush=True)
    g2 = copy.deepcopy(l6_snap)
    env._game = g2
    last_fi = None; total_actions = 0
    # Execute yukft-2 FIRST (feet 0,1,2 in upper-left), then yukft (feet 3,4 in lower-right)
    # to avoid cross-body foot overlap on clicks
    for body_moves, _ in [(best_y2[1], y2_fi), (best_yukft[1], yukft_fi)]:
        for fi, cx, cy in body_moves:
            f = g2.ftmaz[fi]
            if fi != last_fi:
                env.step(GameAction.ACTION6, data={"x": f.x+2, "y": f.y+2})
                total_actions += 1
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            total_actions += 1
            last_fi = fi
            f_after = g2.ftmaz[fi]
            print(f"  foot[{fi}]->({cx},{cy}): foot now at ({f_after.x},{f_after.y})", flush=True)
            if obs.levels_completed >= 6:
                print(f"\n>>> ALL 6 LEVELS SOLVED! {total_actions} actions <<<", flush=True)
                return

    print(f"\nNOT SOLVED ({total_actions} actions)", flush=True)
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
