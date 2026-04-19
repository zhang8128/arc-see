"""R11L L2: large random search biased toward meaningful click positions.

Previous random search (pure uniform) failed. Try biasing clicks toward:
  - 4 hip centers
  - positions that produce distinct arm states
  - random positions (for coverage)

10K rollouts × 15 clicks each.
"""
import random
import numpy as np
import arc_agi
from arcengine import GameAction


def main():
    random.seed(7)
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]

    hips = [(49, 9), (8, 21), (45, 35), (54, 48)]
    # Additional "interesting" points: coordinates of the color-c cluster diamonds
    # and any 1-cell c dots at (39-43, 48-54) form a diamond pattern
    c_diamond_center = (40, 51)
    # Plus common points
    common = [(20, 20), (30, 30), (40, 40), (50, 50), (20, 40), (40, 20),
              (10, 30), (30, 10), (50, 30), (30, 50), (25, 25), (35, 35),
              (45, 45), (15, 15), (55, 55), (25, 45), (45, 25), (35, 15),
              (15, 35), (55, 15), (15, 55)]
    candidates = hips + [c_diamond_center] + common

    N = 8000
    STEPS = 15

    for r in range(N):
        env.reset()
        for cx, cy in L1:
            env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        path = []
        for s in range(STEPS):
            # 60% biased to candidates, 40% random
            if random.random() < 0.6:
                cx, cy = random.choice(candidates)
            else:
                cx = random.randint(0, 63)
                cy = random.randint(0, 63)
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            path.append((cx, cy))
            if obs2.levels_completed >= 2:
                print(f"L2 WIN rollout={r} step={s} path={path}")
                return
        if r % 1000 == 0 and r > 0:
            print(f"rollout {r}: no L2 win yet")
    print(f"\nno L2 win in {N} × {STEPS}")


if __name__ == "__main__":
    main()
