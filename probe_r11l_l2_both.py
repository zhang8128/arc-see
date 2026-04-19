"""R11L L2: arm 1 somewhere THEN arm 2 to (40, 51) goal.

We know (45, 35), (26, 54) places arm 2 foot exactly at (40, 51). If the win
requires both arms at specific positions, then prefixing with an arm 1
movement should produce a WIN for the right arm-1 target.
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
    ARM2_GOAL_SEQ = [(45, 35), (26, 54)]  # places arm 2 foot at (40, 51)

    # Sweep arm 1 first clicks at 2-pixel stride
    print("-- sweep arm1 click before arm2 goal --")
    wins = []
    distinct_arm1 = set()
    arm1_samples = {}
    for cx1 in range(0, 64, 2):
        for cy1 in range(0, 64, 2):
            env.reset()
            for px, py in L1:
                env.step(GameAction.ACTION6, data={"x": px, "y": py})
            # Arm 1 move via a single click
            env.step(GameAction.ACTION6, data={"x": cx1, "y": cy1})
            # Arm 2 placement
            env.step(GameAction.ACTION6, data={"x": 45, "y": 35})
            obs_final = env.step(GameAction.ACTION6, data={"x": 26, "y": 54})
            if obs_final.levels_completed >= 2:
                wins.append((cx1, cy1))
                print(f"  WIN: arm1 click ({cx1}, {cy1}) + arm2 goal")
                if len(wins) >= 5:
                    return

    print(f"total wins: {len(wins)}")

    # Also try: arm 2 goal FIRST, then arm 1 click (different order)
    print("\n-- arm2 goal FIRST, then arm 1 click --")
    for cx1 in range(0, 64, 2):
        for cy1 in range(0, 64, 2):
            env.reset()
            for px, py in L1:
                env.step(GameAction.ACTION6, data={"x": px, "y": py})
            # Arm 2 placement
            env.step(GameAction.ACTION6, data={"x": 45, "y": 35})
            env.step(GameAction.ACTION6, data={"x": 26, "y": 54})
            # Arm 1 move
            obs_final = env.step(GameAction.ACTION6, data={"x": cx1, "y": cy1})
            if obs_final.levels_completed >= 2:
                print(f"  WIN: arm2 goal + arm1 click ({cx1}, {cy1})")
                return

    print("no wins in either order")


if __name__ == "__main__":
    main()
