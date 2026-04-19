"""R11L L2: find the clicks that reach the isolated foot region at y=29-31.

Also sweep multi-click sequences to see if the isolated region expands.
Maybe the hole+isolated pattern is the goal structure.
"""
import copy
import numpy as np
import arc_agi
from arcengine import GameAction


def sixes(g):
    return sorted([(int(x), int(y)) for y, x in np.argwhere(g == 6)])


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    snap = copy.deepcopy(env._game)

    # Find clicks that put arm 1 foot in the isolated cluster y=29-31
    isolated = {(x, y) for x in range(33, 37) for y in range(29, 32)}
    clicks_to_isolated: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for cy in range(64):
        for cx in range(64):
            env._game = copy.deepcopy(snap)
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            g = np.array(obs.frame[-1], dtype=np.int64)
            s = sixes(g)
            arm1 = None
            for p in s:
                if p != (49, 41):
                    arm1 = p
                    break
            if arm1 in isolated:
                clicks_to_isolated.setdefault(arm1, []).append((cx, cy))

    print(f"clicks that reach the isolated region:")
    for pos, clicks in sorted(clicks_to_isolated.items()):
        print(f"  foot at {pos}: {len(clicks)} clicks, e.g. {clicks[:5]}")

    # Find clicks that put arm 1 foot INSIDE the "hole" at y=20-22, x=25-36
    hole = {(x, y) for x in range(25, 37) for y in range(20, 23)}
    clicks_to_hole: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for cy in range(64):
        for cx in range(64):
            env._game = copy.deepcopy(snap)
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            g = np.array(obs.frame[-1], dtype=np.int64)
            s = sixes(g)
            arm1 = None
            for p in s:
                if p != (49, 41):
                    arm1 = p
                    break
            if arm1 in hole:
                clicks_to_hole.setdefault(arm1, []).append((cx, cy))
    print(f"\nclicks that reach the 'hole' area:")
    for pos, clicks in sorted(clicks_to_hole.items()):
        print(f"  foot at {pos}: {len(clicks)} clicks, e.g. {clicks[:5]}")


if __name__ == "__main__":
    main()
