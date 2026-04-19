"""R11L L2: arm 2 head visits arm 1 hip positions (and vice versa).

Try sequences where arm 2 is armed and then head-visits the arm 1 hips
or head. Maybe the win is cross-visit.
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

    # All 4 hip centers as head targets
    arm1_hips = [(49, 9), (8, 21)]
    arm2_hips = [(45, 35), (54, 48)]
    all_hips = arm1_hips + arm2_hips

    def head_click(pos):
        return (pos[0] - 1, pos[1] - 1)

    # 1. Single hip arming then head-visit to a hip of the OTHER arm
    print("-- arm2 armed, head visits arm1 hips --")
    for arm2_arm in arm2_hips:
        for target in arm1_hips:
            seq = [arm2_arm, head_click(target)]
            env._game = copy.deepcopy(snap)
            for cx, cy in seq:
                obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            print(f"  {seq}: lc={obs.levels_completed}")

    # 2. 3-click: arm1-hip → arm2-arm → target
    print("\n-- arm1 hip → arm2 arm → target --")
    for target in [(27, 55), (26, 54), (40, 51), (40, 50), (20, 30),
                   (30, 30), (36, 13), (42, 30), (17, 6)]:
        for a1 in arm1_hips:
            for a2 in arm2_hips:
                seq = [head_click(a1), a2, target]
                env._game = copy.deepcopy(snap)
                for cx, cy in seq:
                    obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
                if obs.levels_completed >= 2:
                    print(f"  WIN: {seq}")
                    return

    # 3. The full L1-pattern with head-visits at hip centers with alternating arm arming
    print("\n-- L1-style: 4 hip head-visits (A → hip → B → hip2) --")
    for perm in itertools.permutations(all_hips, 4):
        seq = [head_click(p) for p in perm]
        env._game = copy.deepcopy(snap)
        for cx, cy in seq:
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        if obs.levels_completed >= 2:
            print(f"  WIN: {seq}")
            return
    print("  no wins")

    # 4. 5-click sequences interleaving arm 2 arm and head visits
    print("\n-- arm2 arm + arm1 hip head-visits --")
    for a2 in arm2_hips:
        for perm in itertools.permutations(arm1_hips + arm2_hips, 3):
            seq = [a2] + [head_click(p) for p in perm]
            env._game = copy.deepcopy(snap)
            for cx, cy in seq:
                obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            if obs.levels_completed >= 2:
                print(f"  WIN: {seq}")
                return
    print("  no wins in final pass")


if __name__ == "__main__":
    main()
