"""R11L L2: map all reachable arm 1 foot positions at 1px resolution.

Then try 4-click: arm2_3click + arm1_single_click at 4px resolution.
"""
import numpy as np
import arc_agi
from arcengine import GameAction
import time
from collections import Counter

L1 = [(36, 13), (26, 61), (42, 30)]
ARM2_HIPS = [(45, 35), (54, 48)]


def sixes(g):
    return sorted([(int(x), int(y)) for y, x in np.argwhere(g == 6)])


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    def play(seq):
        env.reset()
        obs = None
        for px, py in L1:
            obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
        for cx, cy in seq:
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        return obs

    # Phase 1: map arm 1 foot positions via single click at 2px resolution
    print("=== Phase 1: arm 1 reachable map (2px grid) ===")
    arm1_positions = Counter()
    arm1_click_map = {}  # foot_pos → list of clicks that reach it
    grid1 = list(range(0, 64, 2))

    for cx in grid1:
        for cy in grid1:
            obs = play([(cx, cy)])
            g = np.array(obs.frame[-1], dtype=np.int64)
            s = sixes(g)
            arm1_pos = s[0]  # first six = arm 1 foot
            arm1_positions[arm1_pos] += 1
            if arm1_pos not in arm1_click_map:
                arm1_click_map[arm1_pos] = (cx, cy)

    print(f"Distinct arm 1 positions: {len(arm1_positions)}")
    for pos, count in arm1_positions.most_common():
        click = arm1_click_map[pos]
        print(f"  {pos}: {count} clicks reach it (e.g., {click})")

    # Phase 2: 4-click = (arm2 A, arm2 hip, arm2 B, arm1 click)
    # For each distinct arm 1 position, try arm 2 3-click patterns
    print("\n=== Phase 2: 4-click search (3 arm2 + 1 arm1) ===")
    non_default = [pos for pos, cnt in arm1_positions.most_common()
                   if cnt < 500]  # non-saturated positions
    print(f"Non-default arm 1 positions to try: {len(non_default)}")

    grid2 = list(range(0, 64, 8))  # 8px for arm 2 (64 positions)
    t0 = time.time()
    done = 0
    wins = []

    for arm1_pos in non_default:
        arm1_click = arm1_click_map[arm1_pos]
        for hip in ARM2_HIPS:
            for a_x in grid2:
                for a_y in grid2:
                    for b_x in grid2:
                        for b_y in grid2:
                            # 4 clicks: arm2 A, arm2 hip, arm2 B, arm1 last
                            obs = play([(a_x, a_y), hip, (b_x, b_y),
                                        arm1_click])
                            done += 1
                            if obs.levels_completed >= 2:
                                wins.append((arm1_click, (a_x, a_y),
                                             hip, (b_x, b_y)))
                                print(f"  WIN: arm1={arm1_click} "
                                      f"arm2=({a_x},{a_y})→{hip}→"
                                      f"({b_x},{b_y})")
                                if len(wins) >= 10:
                                    print(f"Done: {time.time()-t0:.0f}s")
                                    return
            if done % 2000 == 0:
                elapsed = time.time() - t0
                rate = done / elapsed if elapsed > 0 else 0
                remain = len(non_default) * 2 * len(grid2)**4 - done
                eta = remain / rate if rate > 0 else 0
                print(f"  [{done}] {elapsed:.0f}s, ~{eta:.0f}s remaining")

    # Phase 3: also try arm1 FIRST, then arm2
    print("\n=== Phase 3: 4-click (arm1 first, then arm2 3-click) ===")
    done2 = 0
    for arm1_pos in non_default:
        arm1_click = arm1_click_map[arm1_pos]
        for hip in ARM2_HIPS:
            for a_x in grid2:
                for a_y in grid2:
                    for b_x in grid2:
                        for b_y in grid2:
                            obs = play([arm1_click, (a_x, a_y), hip,
                                        (b_x, b_y)])
                            done2 += 1
                            if obs.levels_completed >= 2:
                                wins.append((arm1_click, (a_x, a_y),
                                             hip, (b_x, b_y)))
                                print(f"  WIN: arm1={arm1_click} first, "
                                      f"arm2=({a_x},{a_y})→{hip}→"
                                      f"({b_x},{b_y})")
                                if len(wins) >= 10:
                                    print(f"Done: {time.time()-t0:.0f}s")
                                    return
            if done2 % 2000 == 0:
                elapsed = time.time() - t0
                print(f"  [{done2}] {elapsed:.0f}s")

    print(f"\nTotal wins: {len(wins)} ({done+done2} trials, "
          f"{time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
