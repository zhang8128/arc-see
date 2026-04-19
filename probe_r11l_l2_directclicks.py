"""R11L L2: click DIRECTLY on each c-dot position as raw coordinates.

Previous probes used the midpoint formula to place arm 2 foot on c-dots.
But maybe the win is triggered by clicking at the RAW c-dot coordinates.
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
        (40, 51),  # center
    ]

    # Individual raw clicks
    print("-- raw clicks on each c-dot --")
    for dot in c_dots:
        env._game = copy.deepcopy(snap)
        obs = env.step(GameAction.ACTION6, data={"x": dot[0], "y": dot[1]})
        marker = " WIN" if obs.levels_completed >= 2 else ""
        print(f"  click{dot}: lc={obs.levels_completed}{marker}")

    # Sequences of raw c-dot clicks (12 dots + center = 13 clicks)
    print("\n-- sequence of all 13 raw c-dot clicks (incl. center) --")
    env._game = copy.deepcopy(snap)
    for dot in c_dots:
        obs = env.step(GameAction.ACTION6, data={"x": dot[0], "y": dot[1]})
        if obs.levels_completed >= 2:
            print(f"  WIN at dot {dot}")
            return
    print(f"  final lc={obs.levels_completed}")

    # With arm 2 armed first
    print("\n-- (45, 35) + raw c-dot clicks --")
    env._game = copy.deepcopy(snap)
    env.step(GameAction.ACTION6, data={"x": 45, "y": 35})
    for dot in c_dots:
        obs = env.step(GameAction.ACTION6, data={"x": dot[0], "y": dot[1]})
        if obs.levels_completed >= 2:
            print(f"  WIN at dot {dot}")
            return
    print(f"  final lc={obs.levels_completed}")

    # Try: click the static marker (49, 41)
    print("\n-- single click (49, 41) --")
    env._game = copy.deepcopy(snap)
    obs = env.step(GameAction.ACTION6, data={"x": 49, "y": 41})
    print(f"  lc={obs.levels_completed}")

    # Click both foot positions in sequence
    print("\n-- foot clicks: (24, 12) and (49, 41) --")
    env._game = copy.deepcopy(snap)
    env.step(GameAction.ACTION6, data={"x": 24, "y": 12})
    obs = env.step(GameAction.ACTION6, data={"x": 49, "y": 41})
    print(f"  lc={obs.levels_completed}")
    env._game = copy.deepcopy(snap)
    env.step(GameAction.ACTION6, data={"x": 49, "y": 41})
    obs = env.step(GameAction.ACTION6, data={"x": 24, "y": 12})
    print(f"  reversed: lc={obs.levels_completed}")


if __name__ == "__main__":
    main()
