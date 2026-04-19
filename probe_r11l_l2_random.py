"""R11L: random search to find an L2 win sequence after completing L1.

Approach:
  1. Play the L1 win: (36, 13), (26, 61), (42, 30).
  2. From the post-L1 state, random-search 10-click sequences and track
     levels_completed >= 2 (L2 cleared).
  3. Log any winning sequence.
"""
import random
import numpy as np
import arc_agi
from arcengine import GameAction


def main():
    random.seed(1)
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1_SOLUTION = [(36, 13), (26, 61), (42, 30)]

    N_ROLLOUTS = 2000
    STEPS = 12
    best = None
    wins_seen = []

    for r in range(N_ROLLOUTS):
        env.reset()
        for cx, cy in L1_SOLUTION:
            env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        # Now in L2. Random play.
        path = []
        for s in range(STEPS):
            cx = random.randint(0, 63)
            cy = random.randint(0, 63)
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            path.append((cx, cy))
            if obs2.levels_completed >= 2:
                print(f"L2 WIN at rollout {r}, step {s}: path={path}")
                wins_seen.append(list(path))
                break
        if len(wins_seen) >= 3:
            break

    print(f"\ntotal L2 wins found: {len(wins_seen)}")
    for w in wins_seen:
        print(f"  {w}")


if __name__ == "__main__":
    main()
