"""General R11L level solver — works for any level with the foot-centroid mechanic.

Usage: python solve_r11l_general.py
Solves from L1 through L6 automatically.
"""
import copy
import arc_agi
from arcengine import GameAction
from collections import defaultdict

arcade = arc_agi.Arcade()
env = arcade.make("r11l-aa269680", render_mode=None)

L1_SOLUTION = [(36, 13), (26, 61), (42, 30)]


def solve_level(env, snap, level_num, target_lc):
    """Solve the current level by moving feet to get body centroids at hands."""
    g = env._game

    # Identify bodies, feet, hands
    bodies = list(g.brdck.keys())
    print(f"\n=== SOLVING L{level_num} ({len(bodies)} bodies) ===", flush=True)

    # Identify which ftmaz feet belong to which body
    body_feet = {}  # body_name → list of ftmaz indices
    for body_name in bodies:
        mdpcc = g.brdck[body_name]["mdpcc"]
        indices = []
        for mi, m in enumerate(mdpcc):
            for fi, f in enumerate(g.ftmaz):
                if f is m:
                    indices.append(fi)
                    break
        body_feet[body_name] = indices
        hand = g.dfugm[body_name]["xwdrv"]
        kignw = g.brdck[body_name]["kignw"]
        if hand:
            print(f"  {body_name}: hand=({hand.x},{hand.y}) kignw={'(' + str(kignw.x) + ',' + str(kignw.y) + ')' if kignw else 'None'} feet={indices}", flush=True)

    # Get valid body positions for each body (pixel-perfect collision check)
    obs_sprites = [s for s in g.current_level.get_sprites() if s.name.startswith("qtwnv")]

    # Collect reachable positions for each foot at 2px
    print("  Mapping reachable positions...", flush=True)
    foot_centers = {}  # fi → set of (cx, cy) centers
    foot_clicks = {}   # fi → {center: click}

    for fi in range(len(g.ftmaz)):
        f_init = (g.ftmaz[fi].x, g.ftmaz[fi].y)
        f_sel = (f_init[0] + 2, f_init[1] + 2)
        centers = set()
        clicks = {}

        for x in range(0, 64, 2):
            for y in range(0, 64, 2):
                env._game = copy.deepcopy(snap)
                if fi > 0:
                    env.step(GameAction.ACTION6, data={"x": f_sel[0], "y": f_sel[1]})
                env.step(GameAction.ACTION6, data={"x": x, "y": y})
                f = (env._game.ftmaz[fi].x, env._game.ftmaz[fi].y)
                c = (f[0] + 2, f[1] + 2)
                if f != f_init:
                    centers.add(c)
                    if c not in clicks:
                        clicks[c] = (x, y)

        init_c = (f_init[0] + 2, f_init[1] + 2)
        centers.add(init_c)
        clicks[init_c] = None
        foot_centers[fi] = centers
        foot_clicks[fi] = clicks

    # Solve each body
    all_clicks = []

    for body_name in bodies:
        hand = g.dfugm[body_name]["xwdrv"]
        kignw = g.brdck[body_name]["kignw"]
        if not hand or not kignw:
            continue

        feet_idx = body_feet[body_name]
        n = len(feet_idx)

        # Find valid body positions
        valid_body = set()
        for bx in range(0, 64):
            for by in range(0, 64):
                kignw.set_position(bx, by)
                if kignw.collides_with(hand) and not any(kignw.collides_with(o) for o in obs_sprites):
                    valid_body.add((bx, by))
        # Restore
        orig_pos = None
        for bx, by in valid_body:
            kignw.set_position(bx, by)
            orig_pos = (bx, by)
            break

        print(f"  {body_name}: {len(valid_body)} valid body positions, {n} feet", flush=True)

        if n == 2:
            # 2 feet: simple enumeration
            fi0, fi1 = feet_idx
            found = False
            for c0 in foot_centers[fi0]:
                for c1 in foot_centers[fi1]:
                    sx, sy = c0[0] + c1[0], c0[1] + c1[1]
                    bx = sx // 2 - 2
                    by = sy // 2 - 2
                    if (bx, by) in valid_body:
                        # Verify with actual collision
                        env._game = copy.deepcopy(snap)
                        for prev_click in all_clicks:
                            env.step(GameAction.ACTION6, data={"x": prev_click[0], "y": prev_click[1]})
                        # Apply these foot moves
                        cl0 = foot_clicks[fi0][c0]
                        cl1 = foot_clicks[fi1][c1]
                        test_clicks = []
                        if cl0:
                            if fi0 > 0:
                                f = g.ftmaz[fi0]
                                test_clicks.append((f.x + 2, f.y + 2))
                            test_clicks.append(cl0)
                        if cl1:
                            f = g.ftmaz[fi1]
                            test_clicks.append((f.x + 2, f.y + 2))
                            test_clicks.append(cl1)

                        # Build solution clicks
                        clicks_for_body = []
                        if cl0:
                            clicks_for_body.append(("sel" if fi0 > 0 else "skip", fi0))
                            clicks_for_body.append(("move", cl0))
                        if cl1:
                            clicks_for_body.append(("sel", fi1))
                            clicks_for_body.append(("move", cl1))

                        print(f"    Solution: foot[{fi0}]→{c0} foot[{fi1}]→{c1} → body ({bx},{by})", flush=True)

                        result_clicks = []
                        if cl0:
                            f_init = (g.ftmaz[fi0].x, g.ftmaz[fi0].y)
                            if fi0 != 0 or all_clicks:  # need selection
                                result_clicks.append((f_init[0] + 2, f_init[1] + 2))
                            result_clicks.append(cl0)
                        if cl1:
                            f_init = (g.ftmaz[fi1].x, g.ftmaz[fi1].y)
                            result_clicks.append((f_init[0] + 2, f_init[1] + 2))
                            result_clicks.append(cl1)

                        all_clicks.extend(result_clicks)
                        found = True
                        break
                if found:
                    break
            if not found:
                print(f"    NO SOLUTION for {body_name}!", flush=True)

        elif n >= 3:
            # Meet in the middle for 3+ feet
            half = n // 2
            first_half = feet_idx[:half]
            second_half = feet_idx[half:]

            # Build pair sums for first half
            from itertools import product as iprod
            pair1 = defaultdict(list)
            centers1 = [list(foot_centers[fi]) for fi in first_half]
            for combo in iprod(*centers1):
                sx = sum(c[0] for c in combo)
                sy = sum(c[1] for c in combo)
                pair1[(sx, sy)].append(combo)

            # For each valid body, find matching second half
            found = False
            for bx, by in sorted(valid_body):
                target_s = (n * (bx + 2), n * (by + 2))
                for dx in range(n):
                    for dy in range(n):
                        need_total = (target_s[0] + dx, target_s[1] + dy)
                        # Try each first-half sum
                        for s1, combos1 in pair1.items():
                            need2 = (need_total[0] - s1[0], need_total[1] - s1[1])
                            # Check if second half can achieve need2
                            centers2 = [list(foot_centers[fi]) for fi in second_half]
                            for combo2 in iprod(*centers2):
                                s2 = (sum(c[0] for c in combo2), sum(c[1] for c in combo2))
                                if s2 == need2:
                                    combo_full = combos1[0] + combo2
                                    print(f"    Solution: body ({bx},{by})", flush=True)

                                    result_clicks = []
                                    for j, fi in enumerate(feet_idx):
                                        c = combo_full[j]
                                        cl = foot_clicks[fi][c]
                                        if cl:
                                            f_init = (g.ftmaz[fi].x, g.ftmaz[fi].y)
                                            if fi != 0 or all_clicks or j > 0:
                                                result_clicks.append((f_init[0] + 2, f_init[1] + 2))
                                            result_clicks.append(cl)
                                        print(f"      foot[{fi}] → {c} via {cl}", flush=True)

                                    all_clicks.extend(result_clicks)
                                    found = True
                                    break
                            if found:
                                break
                        if found:
                            break
                    if found:
                        break
                if found:
                    break
            if not found:
                print(f"    NO SOLUTION for {body_name}! Trying random...", flush=True)

    return all_clicks


def main():
    env.reset()
    env.reset()

    # L1
    print("=== L1: known solution ===", flush=True)
    for px, py in L1_SOLUTION:
        obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
    print(f"  L1 done: lc={obs.levels_completed}", flush=True)

    # L2-L6
    prev_clicks = list(L1_SOLUTION)
    for level in range(2, 7):
        snap = copy.deepcopy(env._game)
        clicks = solve_level(env, snap, level, level)

        # Execute the solution
        env._game = copy.deepcopy(snap)
        for cx, cy in clicks:
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            if obs.levels_completed >= level:
                print(f"  >>> L{level} SOLVED! lc={obs.levels_completed} in {len(clicks)} clicks <<<", flush=True)
                break

        if obs.levels_completed < level:
            print(f"  L{level} NOT solved. lc={obs.levels_completed}", flush=True)
            break

        prev_clicks.extend(clicks)

    print(f"\nFinal: levels_completed={obs.levels_completed} state={obs.state.name}", flush=True)
    if obs.levels_completed >= 6:
        print(">>> ALL LEVELS SOLVED! <<<", flush=True)


if __name__ == "__main__":
    main()
