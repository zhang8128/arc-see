"""R11L L2: verify the two-arm hypothesis.

Plan:
  1. Reset L2. Click one of the 4 hips to "activate" it.
  2. Click several different positions, track BOTH foot markers.
  3. Fit a formula for each arm's foot movement, based on which hip is active.
  4. Deduce which hip pairs with which arm.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def sixes(g):
    return [(int(x), int(y)) for y, x in np.argwhere(g == 6)]


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    # Initial L2 state
    env.reset()
    for cx, cy in L1:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    g0 = frame(obs)
    print(f"L2 initial sixes: {sixes(g0)}")

    hips = [(49, 9), (8, 21), (45, 35), (54, 48)]

    for hip in hips:
        print(f"\n-- activate hip {hip}, then sweep 5 clicks --")
        for test_click in [(10, 10), (30, 30), (50, 50), (20, 40), (40, 20)]:
            env.reset()
            for px, py in L1:
                env.step(GameAction.ACTION6, data={"x": px, "y": py})
            # Activate
            env.step(GameAction.ACTION6, data={"x": hip[0], "y": hip[1]})
            # Action click
            obs2 = env.step(GameAction.ACTION6, data={"x": test_click[0], "y": test_click[1]})
            g = frame(obs2)
            s = sixes(g)
            print(f"  hip{hip} + click{test_click}: sixes={s}")


if __name__ == "__main__":
    main()
