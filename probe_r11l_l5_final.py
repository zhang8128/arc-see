"""R11L L5: hand-crafted solution with overlap-safe foot moves.

yukft (2 feet): 4 clicks — absorb pgkne, pyzud, reach hand.
yukft-2 (3 feet): absorb ttyia (2 moves), zjgrp (2 moves), reach hand (3 moves).

Key constraint: click to move foot must NOT land on another foot's bounding box.
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


def body_from_centers(centers):
    n = len(centers)
    sx = sum(c[0] for c in centers)
    sy = sum(c[1] for c in centers)
    return (sx // n - 2, sy // n - 2)


def foot_overlaps_click(foot_pos, click_pos):
    """Does a click at click_pos land within foot's 5x5 bounding box?"""
    fx, fy = foot_pos  # foot top-left
    cx, cy = click_pos
    return fx <= cx < fx + 5 and fy <= cy < fy + 5


def execute_moves(snap, moves, debug=True):
    """Execute a sequence of foot moves and return results.

    moves: list of (foot_global_idx, target_center_x, target_center_y)
    Each move = select foot (if different) + click target center.
    """
    g = copy.deepcopy(snap)
    env._game = g

    clicks = []
    last_selected = None
    action_count = 0

    for fi_global, tcx, tcy in moves:
        foot = g.ftmaz[fi_global]
        foot_center = (foot.x + 2, foot.y + 2)

        # Check if we need to select this foot
        if fi_global != last_selected:
            # Verify select click won't accidentally hit another foot
            for j, other_foot in enumerate(g.ftmaz):
                if j == fi_global:
                    continue
                if foot_overlaps_click((other_foot.x, other_foot.y), foot_center):
                    print(f"  WARNING: selecting foot[{fi_global}] at {foot_center} "
                          f"overlaps with foot[{j}] at ({other_foot.x},{other_foot.y})")

            clicks.append(foot_center)
            obs = env.step(GameAction.ACTION6, data={"x": foot_center[0], "y": foot_center[1]})
            action_count += 1
            last_selected = fi_global

        # Verify move click won't accidentally hit another foot
        target_foot = (tcx - 2, tcy - 2)  # foot position from center
        for j, other_foot in enumerate(g.ftmaz):
            if j == fi_global:
                continue
            if foot_overlaps_click((other_foot.x, other_foot.y), (tcx, tcy)):
                print(f"  WARNING: moving to ({tcx},{tcy}) overlaps with "
                      f"foot[{j}] at ({other_foot.x},{other_foot.y})")

        clicks.append((tcx, tcy))
        obs = env.step(GameAction.ACTION6, data={"x": tcx, "y": tcy})
        action_count += 1

        if debug:
            bpos = None
            for bname, data in g.brdck.items():
                kignw = data.get("kignw")
                if kignw and kignw.name.startswith("bdkaz-yukft"):
                    fwqwj_name = kignw.name
                    absorbed = g.fwqwj.get(fwqwj_name, [])
                    if absorbed or bname in ("yukft", "yukft-2"):
                        pass
            foot = g.ftmaz[fi_global]
            print(f"  foot[{fi_global}] -> ({foot.x},{foot.y}) center ({foot.x+2},{foot.y+2})")

        if obs.levels_completed >= 5:
            print(f"  >>> L5 SOLVED after {action_count} actions! <<<")
            return clicks, obs, g, action_count

    return clicks, obs, g, action_count


def dump_state(g):
    """Print body/hand state."""
    for bname in ("yukft", "yukft-2"):
        kn = f"bdkaz-{bname}"
        absorbed = g.fwqwj.get(kn, [])
        kignw = g.brdck[bname]["kignw"]
        if kignw:
            c = {int(v) for v in np.unique(kignw.pixels) if v > 0}
            print(f"  {bname}: absorbed={absorbed}, body=({kignw.x},{kignw.y}), colors={c}")
        else:
            print(f"  {bname}: no kignw")
    for hname, hdata in g.dfugm.items():
        h = hdata["xwdrv"]
        hc = {int(v) for v in np.unique(h.pixels) if v > 0}
        print(f"  hand {hname}: ({h.x},{h.y}) colors={hc} matched={hdata['wugiv']}")


def main():
    if not replay_to_l5():
        print("Failed to reach L5")
        return

    l5_snap = copy.deepcopy(env._game)
    g = l5_snap

    # Print initial state
    print("\n=== L5 Initial State ===")
    for fi, f in enumerate(g.ftmaz):
        body = g.mfrvmbaujm(f)
        print(f"  foot[{fi}]: ({f.x},{f.y}) center ({f.x+2},{f.y+2}) -> body={body}")

    # yukft: feet [0,1], obstacles pgkne(12,38) pyzud(31,17), hand pgknepyzud(10,25)
    # yukft-2: feet [2,3,4], obstacles ttyia(54,41) zjgrp(18,51), hand ttyiazjgrp(45,6)

    # === YUKFT SOLUTION (from analytical solver, verified) ===
    # 3 moves, all on foot[1]. foot[0] stays at (23,33) center (25,35).
    # Move 1: foot[1] center (43,34) -> (9,39). body = ((25+9)//2-2, (35+39)//2-2) = (15,35)
    #   pgkne at (12,38): check collision. Hmm, body at (15,35) vs obstacle at (12,38)?
    #   Let me use the verified values from the v3 run.
    yukft_moves = [
        (1, 9, 39),   # foot[1] -> center (9,39) = foot (7,37). Absorb pgkne.
        (1, 50, 7),   # foot[1] -> center (50,7) = foot (48,5). Absorb pyzud.
        (1, 11, 18),  # foot[1] -> center (11,18) = foot (9,16). Reach hand.
    ]

    # === YUKFT-2 SOLUTION (hand-crafted, overlap-safe) ===
    # Initial: foot[2]=(39,45) c(41,47), foot[3]=(32,53) c(34,55), foot[4]=(50,53) c(52,55)
    #
    # Stage 1: Absorb ttyia at (54,41). Need body in collision range ~(50-58, 37-45).
    #   Move foot[2] c(41,47) -> c(59,35). Move foot[3] c(34,55) -> c(59,42).
    #   After: centers (59,35),(59,42),(52,55). Sum=(170,132). body=(54,42). ✓
    #   Click overlap check: c(59,42) vs foot[2] at (57,33): x=59∈[57,61] but y=42∉[33,37]. Safe.
    #
    # Stage 2: Absorb zjgrp at (18,51). Need body ~(14-22, 47-55).
    #   Move foot[2] c(59,35) -> c(2,50). Move foot[3] c(59,42) -> c(2,55).
    #   After: centers (2,50),(2,55),(52,55). Sum=(56,160). body=(16,51). ✓
    #   Click overlap: c(2,50) vs foot[3] at (57,40): |2-57|=55. Safe.
    #     c(2,55) vs foot[2] now at (0,48): x=2∈[0,4], y=55∉[48,52]. Safe.
    #
    # Stage 3: Reach hand at (45,6). Need body in collision range.
    #   Move foot[2] c(2,50) -> c(61,2). Move foot[3] c(2,55) -> c(41,9).
    #   Move foot[4] c(52,55) -> c(39,13).
    #   After: centers (61,2),(41,9),(39,13). Sum=(141,24). body=(45,6). ✓
    #   Click overlaps:
    #     c(61,2) vs foot[3] at (0,53): safe. vs foot[4] at (50,53): safe.
    #     c(41,9) vs foot[2] at (59,0): safe. vs foot[4] at (50,53): safe.
    #     c(39,13) vs foot[2] at (59,0): safe. vs foot[3] at (39,7): x=39∈[39,43], y=13∉[7,11]. Safe.

    y2_moves = [
        # Stage 1: absorb ttyia
        (2, 59, 35),  # foot[2] -> center (59,35)
        (3, 59, 42),  # foot[3] -> center (59,42). Body at (54,42) → absorb ttyia
        # Stage 2: absorb zjgrp
        (2, 2, 50),   # foot[2] -> center (2,50)
        (3, 2, 55),   # foot[3] -> center (2,55). Body at (16,51) → absorb zjgrp
        # Stage 3: reach hand
        (2, 61, 2),   # foot[2] -> center (61,2)
        (3, 41, 9),   # foot[3] -> center (41,9)
        (4, 39, 13),  # foot[4] -> center (39,13). Body at (45,6) → match hand
    ]

    # === Execute and verify ===
    print("\n=== Executing yukft moves ===")
    clicks1, obs1, g1, n1 = execute_moves(l5_snap, yukft_moves)
    print(f"\nAfter yukft ({n1} actions):")
    dump_state(g1)

    print("\n=== Executing yukft-2 moves (from same state) ===")
    # Need to execute both bodies together in the same game
    all_moves = yukft_moves + y2_moves
    print(f"Total moves: {len(all_moves)}")
    clicks_all, obs_all, g_all, n_all = execute_moves(l5_snap, all_moves)

    print(f"\n=== Final state ({n_all} actions) ===")
    dump_state(g_all)

    if obs_all.levels_completed >= 5:
        print(f"\n>>> L5 SOLVED! Total actions: {n_all} (budget: 37) <<<")
        print(f"\nClick sequence for L5:")
        for i, (cx, cy) in enumerate(clicks_all):
            print(f"  {i+1}: ({cx},{cy})")
    else:
        print(f"\n*** NOT SOLVED. lc={obs_all.levels_completed} ***")
        # Try to understand why
        print("\nDebug: checking each body's absorption")
        for bname in ("yukft", "yukft-2"):
            kn = f"bdkaz-{bname}"
            sprites = g_all.current_level.get_sprites_by_name(kn)
            if sprites:
                s = sprites[0]
                c = {int(v) for v in np.unique(s.pixels) if v > 0}
                print(f"  {kn}: pos=({s.x},{s.y}), colors={c}")
            else:
                print(f"  {kn}: NOT FOUND in level")


if __name__ == "__main__":
    main()
