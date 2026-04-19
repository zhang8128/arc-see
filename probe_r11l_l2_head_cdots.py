"""R11L L2: visit each c-dot with ARM 2's HEAD (not foot).

arm 2 head = click + (1, 1) (I think; verify with actual frame inspection).
Earlier probe put arm 2 FOOT on c-dots via click (2*fx-54, 2*fy-48). Now try
putting arm 2 HEAD on c-dots via click (fx-1, fy-1).

12 c-dots: (39,48), (41,48), (38,49), (42,49), (37,50), (43,50), (37,52),
(43,52), (38,53), (42,53), (39,54), (41,54)
"""
import copy
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
    arm = (45, 35)

    print("-- 2-click: arm + head at each cdot --")
    for dot in c_dots:
        cx, cy = dot[0] - 1, dot[1] - 1
        env._game = copy.deepcopy(snap)
        env.step(GameAction.ACTION6, data={"x": arm[0], "y": arm[1]})
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        marker = " WIN" if obs.levels_completed >= 2 else ""
        print(f"  head→{dot} via click({cx},{cy}): lc={obs.levels_completed}{marker}")

    print("\n-- sequence: arm then visit all c-dots with head --")
    env._game = copy.deepcopy(snap)
    env.step(GameAction.ACTION6, data={"x": arm[0], "y": arm[1]})
    for dot in c_dots:
        cx, cy = dot[0] - 1, dot[1] - 1
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        if obs.levels_completed >= 2:
            print(f"  WIN at dot {dot}")
            return
    print(f"  final lc={obs.levels_completed}")

    # Visit in clockwise diamond order
    ordered = [
        (39, 48), (41, 48),
        (42, 49), (43, 50),
        (43, 52), (42, 53),
        (41, 54), (39, 54),
        (38, 53), (37, 52),
        (37, 50), (38, 49),
    ]
    print("\n-- head visits in clockwise order --")
    env._game = copy.deepcopy(snap)
    env.step(GameAction.ACTION6, data={"x": arm[0], "y": arm[1]})
    for dot in ordered:
        cx, cy = dot[0] - 1, dot[1] - 1
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        if obs.levels_completed >= 2:
            print(f"  WIN at dot {dot}")
            return
    print(f"  final lc={obs.levels_completed}")

    # Also: head visits plus foot placement at center
    print("\n-- clockwise + final foot at (40, 51) --")
    env._game = copy.deepcopy(snap)
    env.step(GameAction.ACTION6, data={"x": arm[0], "y": arm[1]})
    for dot in ordered:
        cx, cy = dot[0] - 1, dot[1] - 1
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        if obs.levels_completed >= 2:
            print(f"  WIN at dot {dot}")
            return
    # Final: center
    obs = env.step(GameAction.ACTION6, data={"x": 26, "y": 54})
    print(f"  after center: lc={obs.levels_completed}")


if __name__ == "__main__":
    main()
