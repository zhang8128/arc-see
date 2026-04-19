"""R11L L2: test the 'swap arms' hypothesis.

Need to find clicks that:
  - move arm 1 foot to (49, 41) [arm 2's start]
  - move arm 2 foot to (24, 12) [arm 1's start]

First, sweep all clicks after activating each arm's hip, find clicks that
bring the foot near (49, 41) for arm 1 and near (24, 12) for arm 2.
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

    def setup_l2():
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})

    # Arm 1: activate hip (8, 21), find clicks that move arm-1 foot near (49, 41)
    print("-- Arm 1 foot reachable positions (after hip (8, 21)) --")
    best_arm1 = None
    best_arm1_dist = float('inf')
    for cx in range(0, 64, 2):
        for cy in range(0, 64, 2):
            setup_l2()
            env.step(GameAction.ACTION6, data={"x": 8, "y": 21})
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            s = sixes(frame(obs2))
            # Find arm 1 foot (the one NOT at (49, 41), unless it's at (49, 41) now)
            arm1 = None
            for p in s:
                if p != (49, 41):
                    arm1 = p
                    break
            if arm1 is None and (49, 41) in s:
                # both feet at (49, 41)?
                arm1 = (49, 41)
            if arm1:
                d = abs(arm1[0] - 49) + abs(arm1[1] - 41)
                if d < best_arm1_dist:
                    best_arm1_dist = d
                    best_arm1 = (cx, cy, arm1)

    if best_arm1:
        print(f"closest arm 1 foot to (49, 41): click({best_arm1[0]},{best_arm1[1]}) → foot{best_arm1[2]} (dist {best_arm1_dist})")
    else:
        print("no arm 1 movement detected")

    # Arm 2: activate hip (45, 35), find clicks that move arm-2 foot near (24, 12)
    print("\n-- Arm 2 foot reachable positions (after hip (45, 35)) --")
    best_arm2 = None
    best_arm2_dist = float('inf')
    for cx in range(0, 64, 2):
        for cy in range(0, 64, 2):
            setup_l2()
            env.step(GameAction.ACTION6, data={"x": 45, "y": 35})
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            s = sixes(frame(obs2))
            arm2 = None
            for p in s:
                if p != (24, 12):
                    arm2 = p
                    break
            if arm2:
                d = abs(arm2[0] - 24) + abs(arm2[1] - 12)
                if d < best_arm2_dist:
                    best_arm2_dist = d
                    best_arm2 = (cx, cy, arm2)

    if best_arm2:
        print(f"closest arm 2 foot to (24, 12): click({best_arm2[0]},{best_arm2[1]}) → foot{best_arm2[2]} (dist {best_arm2_dist})")
    else:
        print("no arm 2 movement detected")


if __name__ == "__main__":
    main()
