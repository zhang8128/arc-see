"""R11L L2: find arm 1's distinct reachable positions.

Many L2 clicks saturate arm 1 at (31, 14). The clicks that DON'T saturate
must be hitting something structural. Enumerate them and see if they cluster
into "diamond" regions like L1 had.
"""
import copy
import numpy as np
import arc_agi
from arcengine import GameAction


def sixes(g):
    return sorted([(int(x), int(y)) for y, x in np.argwhere(g == 6)])


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    snap = copy.deepcopy(env._game)

    # Scan all 4096 single clicks, record arm 1 position (first entry of sixes)
    arm1_map: dict[tuple[int, int], tuple[int, int]] = {}
    for cy in range(64):
        for cx in range(64):
            env._game = copy.deepcopy(snap)
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            g = np.array(obs.frame[-1], dtype=np.int64)
            s = sixes(g)
            # Arm 1 is the foot that ISN'T (49, 41). If (49, 41) absent,
            # something weird happened.
            arm1 = None
            for p in s:
                if p != (49, 41):
                    arm1 = p
                    break
            if arm1:
                arm1_map[(cx, cy)] = arm1

    # Distinct arm 1 positions
    distinct = set(arm1_map.values())
    print(f"distinct arm 1 positions: {len(distinct)}")

    # Count how many clicks map to each position
    from collections import Counter
    counts = Counter(arm1_map.values())
    print(f"top 10 most common arm 1 positions:")
    for pos, c in counts.most_common(10):
        print(f"  {pos}: {c} clicks")

    # Interesting: the positions that are NOT the top saturated one
    # Show each distinct position, with the click that achieves it
    if (31, 14) in counts:
        top = (31, 14)
    else:
        top = counts.most_common(1)[0][0]
    print(f"\nsaturated position: {top} ({counts[top]} clicks)")
    non_sat = [(p, c) for p, c in counts.items() if p != top]
    non_sat.sort(key=lambda x: -x[1])
    print(f"NON-saturated distinct positions: {len(non_sat)}")
    for pos, c in non_sat[:30]:
        sample_clicks = [click for click, p in arm1_map.items() if p == pos][:3]
        print(f"  {pos}: {c} clicks  e.g. {sample_clicks}")

    # Compute the bounding box of all non-saturated positions
    ns_positions = [p for p, _ in non_sat]
    if ns_positions:
        xs = [p[0] for p in ns_positions]
        ys = [p[1] for p in ns_positions]
        print(f"\nnon-sat bbox: x {min(xs)}..{max(xs)}, y {min(ys)}..{max(ys)}")

    # Visualize: plot arm 1 positions (non-saturated) on a grid
    print("\narm 1 non-saturated reachable positions:")
    pos_set = set(ns_positions)
    for y in range(0, 32, 1):
        row = ""
        for x in range(0, 48, 1):
            row += "#" if (x, y) in pos_set else "."
        print(f"  y={y:2d}: {row}")


if __name__ == "__main__":
    main()
