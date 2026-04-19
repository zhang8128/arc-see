"""R11L solver v2: solves all levels with execution verification.

Uses meet-in-the-middle for foot placement, verifies by actually
running the clicks, and retries with different solutions if needed.
"""
import copy
import sys
import arc_agi
from arcengine import GameAction
from collections import defaultdict

arcade = arc_agi.Arcade()
env = arcade.make("r11l-aa269680", render_mode=None)

L1 = [(36, 13), (26, 61), (42, 30)]


def map_foot_reachable(fi, snap, step=2):
    """Map reachable centers for foot fi at given pixel step."""
    f_init = (snap.ftmaz[fi].x, snap.ftmaz[fi].y)
    f_sel = (f_init[0] + 2, f_init[1] + 2)
    centers = {}
    for x in range(0, 64, step):
        for y in range(0, 64, step):
            env._game = copy.deepcopy(snap)
            if fi > 0:
                env.step(GameAction.ACTION6, data={"x": f_sel[0], "y": f_sel[1]})
            env.step(GameAction.ACTION6, data={"x": x, "y": y})
            f = (env._game.ftmaz[fi].x, env._game.ftmaz[fi].y)
            c = (f[0] + 2, f[1] + 2)
            if f != f_init and c not in centers:
                centers[c] = (x, y)
    centers[(f_init[0] + 2, f_init[1] + 2)] = None
    return centers


def valid_body_positions(body_name, snap):
    """Find all positions where body collides with hand, not obstacle."""
    kignw = snap.brdck[body_name]["kignw"]
    hand = snap.dfugm[body_name]["xwdrv"]
    obs_sprites = [s for s in snap.current_level.get_sprites()
                   if s.name.startswith("qtwnv")]
    valid = set()
    for bx in range(0, 64):
        for by in range(0, 64):
            kignw.set_position(bx, by)
            if (kignw.collides_with(hand) and
                    not any(kignw.collides_with(o) for o in obs_sprites)):
                valid.add((bx, by))
    return valid


def solve_body(body_name, feet_idx, snap, step=2):
    """Find click sequences for one body. Returns list of (clicks, body_pos)."""
    n = len(feet_idx)
    kignw = snap.brdck[body_name].get("kignw")
    if not kignw or n == 0:
        # No body sprite or no feet — can't solve with standard mechanic
        return []
    fc = {fi: map_foot_reachable(fi, snap, step) for fi in feet_idx}
    valid = valid_body_positions(body_name, snap)
    hand = snap.dfugm[body_name]["xwdrv"]
    hand_center = (hand.x + hand.width // 2, hand.y + hand.height // 2)

    # Sort valid by distance to hand center (prefer solutions closer to center)
    valid_sorted = sorted(valid,
                          key=lambda p: (p[0] + 2 - hand_center[0])**2 +
                                        (p[1] + 2 - hand_center[1])**2)

    solutions = []

    if n == 2:
        fi0, fi1 = feet_idx
        for c0, cl0 in fc[fi0].items():
            for c1, cl1 in fc[fi1].items():
                bx = (c0[0] + c1[0]) // 2 - 2
                by = (c0[1] + c1[1]) // 2 - 2
                if (bx, by) in valid:
                    clicks = []
                    if cl0:
                        f = snap.ftmaz[fi0]
                        clicks.append((f.x + 2, f.y + 2))
                        clicks.append(cl0)
                    if cl1:
                        f = snap.ftmaz[fi1]
                        clicks.append((f.x + 2, f.y + 2))
                        clicks.append(cl1)
                    dist = (bx + 2 - hand_center[0])**2 + (by + 2 - hand_center[1])**2
                    solutions.append((dist, clicks, (bx, by)))

    elif n >= 3:
        # Meet in the middle: split feet into two halves
        half = n // 2
        first_half = feet_idx[:half]
        second_half = feet_idx[half:]

        # Build pair sums for first half
        pair1 = defaultdict(list)
        from itertools import product as iprod
        items1 = [list(fc[fi].items()) for fi in first_half]
        for combo in iprod(*items1):
            centers = [c for c, cl in combo]
            cls = [cl for c, cl in combo]
            sx = sum(c[0] for c in centers)
            sy = sum(c[1] for c in centers)
            pair1[(sx, sy)].append(list(zip(first_half, centers, cls)))

        # Build pair sums for second half
        pair2 = defaultdict(list)
        items2 = [list(fc[fi].items()) for fi in second_half]
        for combo in iprod(*items2):
            centers = [c for c, cl in combo]
            cls = [cl for c, cl in combo]
            sx = sum(c[0] for c in centers)
            sy = sum(c[1] for c in centers)
            pair2[(sx, sy)].append(list(zip(second_half, centers, cls)))

        for bx, by in valid_sorted:
            for dx in range(n):
                for dy in range(n):
                    total = (n * (bx + 2) + dx, n * (by + 2) + dy)
                    for s1, combos1 in pair1.items():
                        need2 = (total[0] - s1[0], total[1] - s1[1])
                        if need2 in pair2:
                            combo = combos1[0] + pair2[need2][0]
                            clicks = []
                            for fi, c, cl in combo:
                                if cl:
                                    f = snap.ftmaz[fi]
                                    clicks.append((f.x + 2, f.y + 2))
                                    clicks.append(cl)
                            dist = (bx + 2 - hand_center[0])**2 + (by + 2 - hand_center[1])**2
                            solutions.append((dist, clicks, (bx, by)))
                            if len(solutions) >= 50:
                                return sorted(solutions)
                    if solutions:
                        break
                if solutions:
                    break
            if solutions:
                break

    solutions.sort()  # closest to hand center first
    return solutions


def solve_level(snap, level_num, target_lc):
    """Solve one level. Returns click sequence or None."""
    g = snap
    # Find bodies with feet (the walkers) and bodies with hands but no kignw (targets)
    walkers = []
    targets = []
    for b in g.brdck:
        if "anqcf" in b:
            continue
        kignw = g.brdck[b].get("kignw")
        hand = g.dfugm.get(b, {}).get("xwdrv")
        mdpcc = g.brdck[b].get("mdpcc", [])
        if kignw and len(mdpcc) > 0:
            walkers.append(b)
        elif hand and not kignw:
            targets.append(b)

    # If there are target bodies (kignw=None), pair walkers with target hands
    # The fwqwj fallback checks if walker body collides with target hand
    if targets and walkers:
        # Pair walkers with target hands
        bodies = []
        for i, walker in enumerate(walkers):
            if i < len(targets):
                # Use the target's hand as this walker's goal
                target_hand = g.dfugm[targets[i]]["xwdrv"]
                # Override: treat the walker as needing to reach target's hand
                bodies.append((walker, [], target_hand))
            else:
                bodies.append((walker, [], None))
    else:
        bodies = [(b, [], None) for b in g.brdck
                  if "anqcf" not in b and g.dfugm.get(b, {}).get("xwdrv")]

    # Map feet to bodies
    for i, (body_name, _, override_hand) in enumerate(bodies):
        indices = []
        for m in g.brdck[body_name]["mdpcc"]:
            for fi, f in enumerate(g.ftmaz):
                if f is m:
                    indices.append(fi)
                    break
        bodies[i] = (body_name, indices, override_hand)

    print(f"\n=== L{level_num}: {len(bodies)} bodies ===", flush=True)
    for body_name, feet_idx, _oh in bodies:
        hand = g.dfugm[body_name]["xwdrv"]
        print(f"  {body_name[:15]}: hand=({hand.x},{hand.y}) feet={feet_idx}", flush=True)

    # Solve each body and collect solutions
    body_solutions = {}
    for body_name, feet_idx, _oh in bodies:
        sols = solve_body(body_name, feet_idx, snap)
        body_solutions[body_name] = sols
        print(f"  {body_name[:15]}: {len(sols)} solutions", flush=True)
        if not sols:
            # Check if this body has no kignw (skip in win check)
            kignw = g.brdck[body_name].get("kignw")
            if not kignw:
                print(f"    (no body sprite — may use fallback)", flush=True)
            else:
                print(f"    NO SOLUTION!", flush=True)
                return None

    # Try combinations: pick one solution per body, execute, verify
    # Use the best (closest to center) for each body
    for attempt in range(min(10, max(len(s) for s in body_solutions.values()))):
        all_clicks = []
        for body_name, feet_idx, _oh in bodies:
            sols = body_solutions[body_name]
            idx = min(attempt, len(sols) - 1)
            _, clicks, bpos = sols[idx]
            all_clicks.extend(clicks)

        # Execute and verify
        env._game = copy.deepcopy(snap)
        for cx, cy in all_clicks:
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            if obs.levels_completed >= target_lc:
                print(f"  >>> L{level_num} SOLVED in {len(all_clicks)} clicks! <<<",
                      flush=True)
                return all_clicks

    print(f"  L{level_num} NOT solved after {attempt + 1} attempts", flush=True)
    return None


def main():
    env.reset()
    env.reset()

    # L1
    for px, py in L1:
        obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
    print(f"L1: lc={obs.levels_completed}", flush=True)

    all_solutions = [L1]

    for level in range(2, 7):
        snap = copy.deepcopy(env._game)
        clicks = solve_level(snap, level, level)
        if clicks:
            all_solutions.append(clicks)
            # Re-execute from snap
            env._game = copy.deepcopy(snap)
            for cx, cy in clicks:
                obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
                if obs.levels_completed >= level:
                    break
        else:
            print(f"STUCK at L{level}", flush=True)
            break

    print(f"\nFinal: lc={obs.levels_completed} state={obs.state.name}", flush=True)
    if obs.levels_completed >= 6:
        print(">>> ALL 6 LEVELS SOLVED! <<<", flush=True)
        print("\nSolutions:", flush=True)
        for i, sol in enumerate(all_solutions):
            print(f"  L{i + 1}: {sol}", flush=True)


if __name__ == "__main__":
    main()
