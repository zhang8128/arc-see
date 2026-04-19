"""R11L L5 solver: fast wall checking via pixel mask, then analytical search."""
import copy
import numpy as np
import arc_agi
from arcengine import GameAction

arcade = arc_agi.Arcade()
env = arcade.make("r11l-aa269680", render_mode=None)
L1 = [(36, 13), (26, 61), (42, 30)]

def replay_to_l5():
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
    return obs.levels_completed >= 4

def build_wall_mask(snap):
    """Build a 64x64 boolean mask: True = wall pixel."""
    mask = np.zeros((64, 64), dtype=bool)
    for w in snap.yhfnp:
        px = w.pixels
        for dy in range(w.height):
            for dx in range(w.width):
                wx, wy = w.x + dx, w.y + dy
                if 0 <= wx < 64 and 0 <= wy < 64:
                    if px[dy, dx] != -1:  # non-transparent
                        mask[wy, wx] = True
    return mask

def build_foot_shape(snap, fi):
    """Get foot pixel shape (relative coords of non-transparent pixels)."""
    foot = snap.ftmaz[fi]
    px = foot.pixels
    shape = []
    for dy in range(foot.height):
        for dx in range(foot.width):
            if px[dy, dx] != -1:
                shape.append((dx, dy))
    return shape, foot.width, foot.height

def precompute_valid_foot_centers(wall_mask, foot_shape, fw, fh, step=2):
    """Fast valid center computation using numpy mask."""
    valid = set()
    for fx in range(0, 64 - fw + 1, step):
        for fy in range(0, 64 - fh + 1, step):
            blocked = False
            for dx, dy in foot_shape:
                if wall_mask[fy + dy, fx + dx]:
                    blocked = True
                    break
            if not blocked:
                valid.add((fx + 2, fy + 2))  # center coords
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
        if fx <= cx < fx + 5 and fy <= cy < fy + 5:
            return True
    return False

def solve_3foot(init_centers, fi_globals, valid_centers, target_sums_list, max_clicks=18):
    """Staged search: 1 or 2 moves per stage, with overlap + wall checking."""
    n = 3
    best = [None]

    def search(stage_idx, centers, last_fi, clicks, moves):
        if best[0] and clicks >= best[0][0]: return
        if stage_idx >= len(target_sums_list):
            if best[0] is None or clicks < best[0][0]:
                best[0] = (clicks, list(moves))
                print(f"    >>> {clicks} clicks, {len(moves)} moves", flush=True)
            return
        target = target_sums_list[stage_idx]
        cur_sum = (sum(centers[fi][0] for fi in fi_globals),
                   sum(centers[fi][1] for fi in fi_globals))

        if cur_sum in target:
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
                    int_sx = cur_sum[0] - old1[0] + nc1[0]
                    int_sy = cur_sum[1] - old1[1] + nc1[1]
                    for tsx, tsy in target:
                        nc2x = tsx - int_sx + old2[0]
                        nc2y = tsy - int_sy + old2[1]
                        if not (2 <= nc2x <= 61 and 2 <= nc2y <= 61): continue
                        if (nc2x, nc2y) == old2: continue
                        if (nc2x, nc2y) not in valid_centers[fi2]: continue
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
    if not replay_to_l5():
        print("Failed to reach L5"); return
    l5_snap = copy.deepcopy(env._game)
    g = l5_snap

    # Build wall mask (fast)
    print("Building wall mask...", flush=True)
    wall_mask = build_wall_mask(g)
    print(f"  Wall pixels: {wall_mask.sum()}/{64*64}", flush=True)

    # Foot shape (all feet have same shape)
    foot_shape, fw, fh = build_foot_shape(g, 2)
    print(f"  Foot shape: {len(foot_shape)} pixels, {fw}x{fh}", flush=True)

    # Precompute valid centers for each foot
    fi_y2 = [2, 3, 4]
    print("Precomputing valid centers (step=2)...", flush=True)
    valid = {}
    for fi in fi_y2:
        valid[fi] = precompute_valid_foot_centers(wall_mask, foot_shape, fw, fh, step=2)
        print(f"  foot[{fi}]: {len(valid[fi])} valid centers", flush=True)

    # Collision sets
    kignw = g.brdck["yukft-2"]["kignw"]
    obs_ttyia = next(o for o in g.nxahg if "ttyia" in o.name)
    obs_zjgrp = next(o for o in g.nxahg if "zjgrp" in o.name)
    hand = g.dfugm["ttyiazjgrp"]["xwdrv"]

    sums_ttyia = required_sums(get_collision_set(kignw, obs_ttyia), 3)
    sums_zjgrp = required_sums(get_collision_set(kignw, obs_zjgrp), 3)
    sums_hand = required_sums(get_collision_set(kignw, hand), 3)
    print(f"Target sums: ttyia={len(sums_ttyia)} zjgrp={len(sums_zjgrp)} hand={len(sums_hand)}", flush=True)

    init_centers = {fi: (g.ftmaz[fi].x + 2, g.ftmaz[fi].y + 2) for fi in fi_y2}
    print(f"Initial centers: {init_centers}", flush=True)

    from itertools import permutations
    best = None
    for order in permutations([("ttyia", sums_ttyia), ("zjgrp", sums_zjgrp)]):
        targets = [s for _, s in order] + [sums_hand]
        names = [n for n, _ in order] + ["hand"]
        print(f"\nOrder: {names}", flush=True)
        sol = solve_3foot(init_centers, fi_y2, valid, targets, 18)
        if sol and (best is None or sol[0] < best[0]):
            best = sol
            print(f"  Best: {sol[0]} clicks", flush=True)

    if not best:
        print("\nNO SOLUTION at step=2, trying step=1...", flush=True)
        for fi in fi_y2:
            valid[fi] = precompute_valid_foot_centers(wall_mask, foot_shape, fw, fh, step=1)
            print(f"  foot[{fi}]: {len(valid[fi])} valid centers (step=1)", flush=True)
        for order in permutations([("ttyia", sums_ttyia), ("zjgrp", sums_zjgrp)]):
            targets = [s for _, s in order] + [sums_hand]
            names = [n for n, _ in order] + ["hand"]
            print(f"\nOrder: {names}", flush=True)
            sol = solve_3foot(init_centers, fi_y2, valid, targets, 18)
            if sol and (best is None or sol[0] < best[0]):
                best = sol

    if best:
        clicks_count, moves = best
        print(f"\n=== YUKFT-2 SOLUTION: {clicks_count} clicks, {len(moves)} moves ===", flush=True)
        for fi, cx, cy in moves:
            print(f"  foot[{fi}] -> center ({cx},{cy}) = foot ({cx-2},{cy-2})", flush=True)

        # Verify with game engine
        print("\n=== FULL VERIFICATION ===", flush=True)
        g2 = copy.deepcopy(l5_snap)
        env._game = g2

        # yukft first (known good)
        yukft_moves = [(1, 9, 39), (1, 50, 7), (1, 11, 18)]
        last_fi = None
        total = 0
        for fi, tcx, tcy in yukft_moves:
            f = g2.ftmaz[fi]
            if fi != last_fi:
                env.step(GameAction.ACTION6, data={"x": f.x+2, "y": f.y+2}); total += 1
            env.step(GameAction.ACTION6, data={"x": tcx, "y": tcy}); total += 1
            last_fi = fi
        print(f"After yukft: {total} actions, hand matched={g2.dfugm['pgknepyzud']['xwdrv'] is not None}", flush=True)

        # yukft-2
        for fi, cx, cy in moves:
            f = g2.ftmaz[fi]
            if fi != last_fi:
                env.step(GameAction.ACTION6, data={"x": f.x+2, "y": f.y+2}); total += 1
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy}); total += 1
            last_fi = fi
            kn = "bdkaz-yukft-2"
            absorbed = g2.fwqwj.get(kn, [])
            kignw2 = g2.brdck["yukft-2"]["kignw"]
            colors = {int(v) for v in np.unique(kignw2.pixels) if v > 0} if kignw2 else set()
            print(f"  foot[{fi}]->({cx},{cy}): body=({kignw2.x},{kignw2.y}) absorbed={len(absorbed)} colors={colors}", flush=True)
            if obs.levels_completed >= 5:
                print(f"\n>>> L5 SOLVED! {total} actions (budget 37) <<<", flush=True)
                return

        print(f"\nNOT SOLVED after {total} actions", flush=True)
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
    else:
        print("\nNO SOLUTION FOUND", flush=True)

if __name__ == "__main__":
    main()
