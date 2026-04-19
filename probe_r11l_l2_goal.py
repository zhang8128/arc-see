"""R11L L2: test the 'foot → static goal at (49, 41)' hypothesis.

If hip is one of the 4 color-3 clusters, then foot = midpoint(hip, click).
To land foot at (49, 41), click = 2*(49,41) - hip = (98-Hx, 82-Hy).

For hip (45, 35): click = (53, 47). In bounds.
For hip (54, 48): click = (44, 34). In bounds.
For hip (49, 9):  click = (49, 73). Out of bounds (y too large).
For hip (8, 21):  click = (90, 61). Out of bounds.

Also: maybe the goal is to bring the head (at (17, 6)) to the foot-goal at
(49, 41). To place head at (49, 41), click (48, 40).
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def foot_positions(g):
    sixes = np.argwhere(g == 6)
    return [(int(x), int(y)) for y, x in sixes]


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]

    targeted_clicks = [
        (53, 47),  # hip (45, 35) → foot (49, 41)
        (44, 34),  # hip (54, 48) → foot (49, 41)
        (48, 40),  # head = (49, 41)
        (49, 41),  # direct click on goal
        # Also try clicks near static foot
        (50, 42), (47, 39), (51, 43),
    ]

    for (cx, cy) in targeted_clicks:
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(obs2)
        feet = foot_positions(g)
        print(f"click({cx},{cy}): feet={feet}  lc={obs2.levels_completed}")

    # Try 2 clicks: place head near goal, then click away
    print("\n-- 2-click patterns --")
    for c1 in [(48, 40), (49, 41), (53, 47), (44, 34)]:
        for c2 in [(20, 20), (10, 10), (30, 5), (5, 30)]:
            env.reset()
            for px, py in L1:
                env.step(GameAction.ACTION6, data={"x": px, "y": py})
            env.step(GameAction.ACTION6, data={"x": c1[0], "y": c1[1]})
            obs3 = env.step(GameAction.ACTION6, data={"x": c2[0], "y": c2[1]})
            if obs3.levels_completed >= 2:
                print(f"  WIN: {c1} -> {c2}")
                return

    print("\nno quick wins from targeted clicks")

    # Exhaustive 2-click (no L1 header; too slow)
    # Try all 1-click positions where foot or head EQUALS the static (49, 41) marker
    print("\n-- sweep: clicks that put MOVABLE foot at (49, 41) --")
    hits = []
    for cx in range(64):
        for cy in range(64):
            env.reset()
            for px, py in L1:
                env.step(GameAction.ACTION6, data={"x": px, "y": py})
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            feet = foot_positions(frame(obs2))
            if (49, 41) in feet and len(feet) >= 2:
                # both the goal and a new movable foot are at (49, 41) — collision
                if feet.count((49, 41)) >= 2 or any(f != (49, 41) and f in feet for f in feet):
                    hits.append((cx, cy))
                    if obs2.levels_completed >= 2:
                        print(f"  WIN via click({cx},{cy})")
                        return
    print(f"clicks that land movable foot at goal: {len(hits)}")
    if hits:
        print(f"  sample: {hits[:10]}")


if __name__ == "__main__":
    main()
