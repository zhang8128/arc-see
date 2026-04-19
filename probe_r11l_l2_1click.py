"""R11L L2: clarify what each single click does from fresh L2.

Test matrix: 4 hips x 3 simple targets = 12 single-step and 2-step sequences.
Track arm 1 and arm 2 positions precisely.
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
    env.reset()
    for cx, cy in L1:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    g0 = frame(obs)
    init_sixes = sixes(g0)
    print(f"L2 init sixes: {init_sixes}")

    def play_l2(steps):
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        last = None
        for cx, cy in steps:
            last = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        return last

    # Part A: single click (no hip first). Which arm moves?
    print("\n-- SINGLE clicks from L2 init --")
    for (cx, cy) in [(10, 10), (30, 30), (50, 30), (20, 50), (40, 40), (8, 21),
                     (49, 9), (45, 35), (54, 48)]:
        obs2 = play_l2([(cx, cy)])
        s = sixes(frame(obs2))
        moved = set(s) - set(init_sixes)
        removed = set(init_sixes) - set(s)
        print(f"  click({cx:2d},{cy:2d}): sixes={s}")
        print(f"    new={sorted(moved)}  gone={sorted(removed)}")

    # Part B: hip + target
    print("\n-- HIP + TARGET pairs --")
    hips = [(49, 9), (8, 21), (45, 35), (54, 48)]
    for hip in hips:
        for (cx, cy) in [(30, 30), (10, 10), (50, 50)]:
            obs2 = play_l2([hip, (cx, cy)])
            s = sixes(frame(obs2))
            moved = set(s) - set(init_sixes)
            removed = set(init_sixes) - set(s)
            print(f"  hip({hip[0]:2d},{hip[1]:2d})→target({cx:2d},{cy:2d}): sixes={s}  new={sorted(moved)}")


if __name__ == "__main__":
    main()
