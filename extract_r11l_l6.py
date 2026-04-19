#!/usr/bin/env python3
"""Capture exact L6 click sequence from probe_r11l_l6_fix by monkey-patching env.step."""
import copy, sys
import arc_agi
from arcengine import GameAction

CLICK = GameAction.ACTION6

# --- Replay L1-L5 using known sequences ---
arcade = arc_agi.Arcade()
env = arcade.make("r11l-aa269680", render_mode=None)
env.reset(); env.reset()

L1 = [(36, 13), (26, 61), (42, 30)]
for x, y in L1:
    obs = env.step(CLICK, data={"x": x, "y": y})
print(f"L1: levels_completed={obs.levels_completed}", file=sys.stderr)

from solve_r11l_v2 import solve_level
for level in range(2, 5):
    snap = copy.deepcopy(env._game)
    clicks = solve_level(snap, level, level)
    env._game = copy.deepcopy(snap)
    for cx, cy in clicks:
        obs = env.step(CLICK, data={"x": cx, "y": cy})
        if obs.levels_completed >= level:
            break
    print(f"L{level}: levels_completed={obs.levels_completed}", file=sys.stderr)

L5 = [(43,34), (9,39), (50,7), (11,18),
      (41,47), (48,36), (34,55), (58,44), (10,54),
      (52,55), (10,58), (50,6), (10,54), (48,2)]
for x, y in L5:
    obs = env.step(CLICK, data={"x": x, "y": y})
print(f"L5: levels_completed={obs.levels_completed}", file=sys.stderr)

# --- Capture L6 clicks by patching env.step ---
l6_clicks = []
original_step = env.step

def capturing_step(action, data=None):
    if data and 'x' in data and 'y' in data:
        l6_clicks.append((data['x'], data['y']))
    return original_step(action, data=data)

env.step = capturing_step

# Run L6 solver from probe_r11l_l6_fix
# We need to import and call its main() but it uses the global env
# Easier: inline the L6 solver call
from itertools import permutations
import numpy as np

l6_snap = copy.deepcopy(env._game)
g = l6_snap

def precompute_valid_centers_engine(snap, fi, step=2):
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

def get_collision_set(kignw, obs_sprite):
    coll = set()
    for yy in range(obs_sprite.height):
        for xx in range(obs_sprite.width):
            if obs_sprite.pixels[yy][xx] != -1:
                coll.add((obs_sprite.x + xx, obs_sprite.y + yy))
    return coll

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
                if (tsx, tsy) in forbidden_sums: continue
                nc = dict(centers); nc[fi] = (ncx, ncy)
                moves.append((fi, ncx, ncy))
                search(stage_idx + 1, nc, fi, clicks + cost, moves)
                moves.pop()
                if best[0] and clicks + cost >= best[0][0]: return
        for fi1 in fi_globals:
            cost1 = 1 if fi1 == last_fi else 2
            for fi2 in fi_globals:
                if fi2 == fi1: continue
                tc = cost1 + 2
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
                        if (tsx, tsy) in forbidden_sums: continue
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

def compute_forbidden_sums(kignw, forbidden_obs, n):
    forbidden = set()
    for obs_s in forbidden_obs:
        coll = get_collision_set(kignw, obs_s)
        forbidden |= required_sums(coll, n)
    return forbidden

print("L6: Precomputing valid centers...", file=sys.stderr)
all_fi = [0, 1, 2, 3, 4]
valid = {}
for fi in all_fi:
    valid[fi] = precompute_valid_centers_engine(l6_snap, fi, step=2)
    print(f"  foot[{fi}]: {len(valid[fi])} valid", file=sys.stderr)

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

yukft_fi = [3, 4]
yukft_target_sums = [required_sums(get_collision_set(kignw_y, o), 2) for o in yukft_target_obs]
yukft_hand_sums = required_sums(get_collision_set(kignw_y, yukft_hand), 2)
yukft_forbidden_sums = compute_forbidden_sums(kignw_y, yukft_forbidden, 2)

y2_fi = [0, 1, 2]
y2_target_sums = [required_sums(get_collision_set(kignw_y2, o), 3) for o in y2_target_obs]
y2_hand_sums = required_sums(get_collision_set(kignw_y2, y2_hand), 3)
y2_forbidden_sums = compute_forbidden_sums(kignw_y2, y2_forbidden, 3)

print("L6: Solving bodies...", file=sys.stderr)
yukft_centers = {fi: (g.ftmaz[fi].x + 2, g.ftmaz[fi].y + 2) for fi in yukft_fi}
best_yukft = None
for order in permutations(range(3)):
    targets = [yukft_target_sums[i] for i in order] + [yukft_hand_sums]
    sol = solve_body(yukft_centers, yukft_fi, valid, targets, yukft_forbidden_sums, 2, 18)
    if sol and (best_yukft is None or sol[0] < best_yukft[0]):
        best_yukft = sol

y2_centers = {fi: (g.ftmaz[fi].x + 2, g.ftmaz[fi].y + 2) for fi in y2_fi}
best_y2 = None
for order in permutations(range(3)):
    targets = [y2_target_sums[i] for i in order] + [y2_hand_sums]
    sol = solve_body(y2_centers, y2_fi, valid, targets, y2_forbidden_sums, 3, 18)
    if sol and (best_y2 is None or sol[0] < best_y2[0]):
        best_y2 = sol

if not best_yukft or not best_y2:
    print("L6: NO SOLUTION", file=sys.stderr)
    sys.exit(1)

# Execute L6 via capturing_step
g2 = copy.deepcopy(l6_snap)
env._game = g2
last_fi = None
for body_moves in [best_y2[1], best_yukft[1]]:
    for fi, cx, cy in body_moves:
        f = g2.ftmaz[fi]
        if fi != last_fi:
            capturing_step(CLICK, data={"x": f.x + 2, "y": f.y + 2})
        obs = capturing_step(CLICK, data={"x": cx, "y": cy})
        last_fi = fi
        if obs.levels_completed >= 6:
            break
    if obs.levels_completed >= 6:
        break

print(f"L6: {len(l6_clicks)} clicks, levels_completed={obs.levels_completed}, state={obs.state}", file=sys.stderr)

# Output L6 clicks
print(f"L6_CLICKS = {l6_clicks}")
print(f"# {len(l6_clicks)} clicks")
