"""R11L L2: try combos that put arm 1 in the isolated cluster AND arm 2 on
the c-diamond.

Arm 1 isolated cluster reachable via clicks at (42-51, 57-63).
Arm 2 c-diamond reachable via (45, 35) + (26, 54).
"""
import copy
import itertools
import numpy as np
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

    # Enumerate the "arm 1 to isolated" clicks (those that moved arm 1 to rows 29-31)
    arm1_iso = [(cx, cy) for cx in range(42, 52) for cy in range(57, 64)]
    # Arm 2 goal sequence
    arm2_seq = [(45, 35), (26, 54)]

    wins = []
    for arm1_click in arm1_iso:
        # Try several orderings
        seqs = [
            [arm1_click] + arm2_seq,
            arm2_seq + [arm1_click],
            [arm1_click, arm2_seq[0], arm2_seq[1]],
            [arm2_seq[0], arm1_click, arm2_seq[1]],
            [arm2_seq[0], arm2_seq[1], arm1_click],
        ]
        for seq in seqs:
            env._game = copy.deepcopy(snap)
            for cx, cy in seq:
                obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            if obs.levels_completed >= 2:
                wins.append(seq)
                print(f"  L2 WIN: {seq}")
                if len(wins) >= 5:
                    return
    print(f"\ntotal wins: {len(wins)}")

    if not wins:
        # Maybe we need 4 clicks: arm 1 to isolated, arm 1 to another spot,
        # arm 2 sequence. Or: use both arm 1 hips.
        print("\ntrying 4-click: arm1_iso + arm1_hip + arm2_seq")
        for arm1_click in arm1_iso[:5]:
            for hip in [(49, 9), (8, 21)]:
                env._game = copy.deepcopy(snap)
                env.step(GameAction.ACTION6, data={"x": arm1_click[0], "y": arm1_click[1]})
                env.step(GameAction.ACTION6, data={"x": hip[0], "y": hip[1]})
                env.step(GameAction.ACTION6, data={"x": 45, "y": 35})
                obs = env.step(GameAction.ACTION6, data={"x": 26, "y": 54})
                if obs.levels_completed >= 2:
                    print(f"  WIN: {arm1_click}, {hip}, (45,35), (26,54)")
                    return


if __name__ == "__main__":
    main()
