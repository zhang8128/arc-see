"""R11L L2: visit each of the 12 c-dots with arm 2 foot.

After arming arm 2 with click (45, 35), arm 2 uses pivot (54, 48).
Formula: foot = ((54+cx)//2, (48+cy)//2). To visit (fx, fy), click
(2*fx - 54, 2*fy - 48).

Try visiting each c-dot individually (2 clicks: arm + cdot).
Also try visiting pairs, triples, or all 12 in sequence.
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

    c_dots = [
        (39, 48), (41, 48), (38, 49), (42, 49),
        (37, 50), (43, 50), (37, 52), (43, 52),
        (38, 53), (42, 53), (39, 54), (41, 54),
    ]
    arm_click = (45, 35)

    def to_click(fx, fy):
        return (2 * fx - 54, 2 * fy - 48)

    # Part 1: 2-click test for each c-dot
    print("-- 2-click visits (arm + cdot) --")
    for dot in c_dots:
        cx, cy = to_click(*dot)
        env._game = copy.deepcopy(snap)
        env.step(GameAction.ACTION6, data={"x": arm_click[0], "y": arm_click[1]})
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        lc = obs.levels_completed
        marker = " WIN" if lc >= 2 else ""
        print(f"  cdot {dot} via click({cx},{cy}): lc={lc}{marker}")

    # Part 2: visit all 12 cdots in a sequence
    print("\n-- visit all 12 cdots after arming arm 2 --")
    env._game = copy.deepcopy(snap)
    env.step(GameAction.ACTION6, data={"x": arm_click[0], "y": arm_click[1]})
    for dot in c_dots:
        cx, cy = to_click(*dot)
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        if obs.levels_completed >= 2:
            print(f"  WIN after visiting {dot}")
            return
    print(f"  after all 12: lc={obs.levels_completed}")

    # Part 3: visit cdots in diamond order (clockwise starting from top)
    ordered = [
        (39, 48), (41, 48),  # top
        (42, 49), (43, 50), (43, 52), (42, 53),  # right
        (41, 54), (39, 54),  # bottom
        (38, 53), (37, 52), (37, 50), (38, 49),  # left
    ]
    print("\n-- cdots in diamond order --")
    env._game = copy.deepcopy(snap)
    env.step(GameAction.ACTION6, data={"x": arm_click[0], "y": arm_click[1]})
    for dot in ordered:
        cx, cy = to_click(*dot)
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        if obs.levels_completed >= 2:
            print(f"  WIN after visiting {dot}")
            return
    print(f"  after all 12 in order: lc={obs.levels_completed}")

    # Part 4: what about center (40, 51)?
    print("\n-- (40, 51) then cdots --")
    env._game = copy.deepcopy(snap)
    env.step(GameAction.ACTION6, data={"x": arm_click[0], "y": arm_click[1]})
    env.step(GameAction.ACTION6, data={"x": 26, "y": 54})  # arm 2 → (40, 51)
    for dot in c_dots:
        cx, cy = to_click(*dot)
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        if obs.levels_completed >= 2:
            print(f"  WIN after {dot}")
            return
    print(f"  final lc={obs.levels_completed}")


if __name__ == "__main__":
    main()
