"""R11L L2: test if the c-dot diamond at (40, 51) is a goal for arm 2.

From the L2 frame, I see 12 1-cell c markers forming a diamond around (40, 51):
  (39,48),(41,48),(38,49),(42,49),(37,50),(43,50),(37,52),(43,52),
  (38,53),(42,53),(39,54),(41,54)

This mirrors a hip diamond in color 'c' — probably a GOAL for arm 2.

To place arm 2 foot at (40, 51) with arm 2's formula (after clicking hip (45, 35)):
  foot = (0.5*cx + 27, 0.5*cy + 24)
  → cx = 26, cy = 54
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def sixes(g):
    return sorted([(int(x), int(y)) for y, x in np.argwhere(g == 6)])


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]

    # Base test: click (45, 35) to arm arm 2, then click (26, 54) to place
    # arm 2 foot at (40, 51).
    attempts = [
        [(45, 35), (26, 54)],
        [(54, 48), (36, 68)],  # via other hip (OOB, will fail)
        [(45, 35), (26, 54), (45, 35)],  # armed again
        [(45, 35), (26, 54), (42, 30)],
        [(45, 35), (26, 54), (8, 21)],
        [(45, 35), (26, 54), (49, 9)],
        # Try arming arm 2, placing foot at goal, then arm 1 somewhere
        [(45, 35), (26, 54), (36, 13)],  # arm 1 to where head started on L2?
        [(45, 35), (26, 54), (17, 6)],
        [(45, 35), (26, 54), (16, 5)],
        # Or: arm 1 first, then arm 2
        [(16, 5), (45, 35), (26, 54)],
        [(36, 13), (45, 35), (26, 54)],
        # Plain arm 2 goal visit
        [(26, 54)],
    ]

    for seq in attempts:
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        final = None
        for cx, cy in seq:
            final = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(final)
        s = sixes(g)
        print(f"seq {seq}: sixes={s}  lc={final.levels_completed}")


if __name__ == "__main__":
    main()
