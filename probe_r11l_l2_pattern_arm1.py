"""R11L L2: try the L1-style 'A → hip → B' pattern BUT with arm 1 visiting
positions in the isolated cluster AND the hole through the hip transitions.

The L1 pattern was 3 clicks: diamond A, hip center, diamond B. For L2, maybe
arm 1 does similar with its 2 hips between 2 goal positions.
"""
import copy
import itertools
import arc_agi
from arcengine import GameAction


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    snap = copy.deepcopy(env._game)

    # arm 1 hips: (49, 9) and (8, 21)
    # arm 2 hips: (45, 35) and (54, 48)
    arm1_hips = [(49, 9), (8, 21)]
    arm2_hips = [(45, 35), (54, 48)]

    # Targets: include the c-diamond placement click
    arm1_iso_click = (45, 60)  # reaches arm 1 foot (34, 30)
    arm2_cdiamond_click = (26, 54)  # reaches arm 2 foot (40, 51)

    # Various sequences inspired by L1 pattern
    candidates = [
        # Double A → hip → B, once per arm
        [(45, 60), (49, 9), (26, 54)],       # arm1 iso → arm1 hip → arm2 place
        [(45, 60), (8, 21), (45, 35), (26, 54)],
        [(45, 60), (45, 35), (26, 54)],
        [(45, 60), (54, 48), (26, 54)],
        # arm 2 first
        [(26, 54), (45, 35), (45, 60)],
        [(45, 35), (26, 54), (45, 60)],
        # With both hip pairs
        [(45, 60), (49, 9), (26, 54), (45, 35)],
        [(45, 60), (8, 21), (26, 54), (54, 48)],
        # Longer sequences
        [(48, 8), (45, 60), (7, 20), (45, 35), (26, 54)],
        [(45, 35), (26, 54), (48, 8), (45, 60), (7, 20)],
        # Head visits all 4 hip centers with arm2 intermediates
        [(48, 8), (44, 34), (26, 54), (7, 20), (53, 47)],
        # Straight cycles
        [(48, 8), (7, 20), (44, 34), (53, 47), (26, 54)],
        [(44, 34), (48, 8), (53, 47), (7, 20), (26, 54)],
    ]

    for seq in candidates:
        env._game = copy.deepcopy(snap)
        lc = 0
        for cx, cy in seq:
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            lc = max(lc, obs.levels_completed)
        marker = " *** WIN ***" if lc >= 2 else ""
        print(f"{seq}: lc={lc}{marker}")


if __name__ == "__main__":
    main()
