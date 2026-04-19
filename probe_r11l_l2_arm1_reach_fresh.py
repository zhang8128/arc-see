"""R11L L2: map arm 1's reachable positions with FRESH RESET.

The deepcopy approach was buggy. Redo the map correctly.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def arm1_foot(g):
    sixes = [(int(x), int(y)) for y, x in np.argwhere(g == 6)]
    for p in sixes:
        if p != (49, 41):
            return p
    return None


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)
    L1 = [(36, 13), (26, 61), (42, 30)]

    positions: dict[tuple[int, int], tuple[int, int]] = {}

    for cy in range(64):
        for cx in range(64):
            env.reset()
            for px, py in L1:
                env.step(GameAction.ACTION6, data={"x": px, "y": py})
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            g = np.array(obs.frame[-1], dtype=np.int64)
            f = arm1_foot(g)
            if f:
                positions[(cx, cy)] = f

    print(f"total mapped: {len(positions)}")
    # Count distinct foot positions
    distinct = set(positions.values())
    print(f"distinct arm1 positions: {len(distinct)}")

    from collections import Counter
    counts = Counter(positions.values())
    print(f"top 10 arm1 positions:")
    for pos, c in counts.most_common(10):
        print(f"  {pos}: {c} clicks")

    if not distinct:
        print("no arm1 positions found — aborting plot")
        return
    # Plot the reachable region
    xs = [p[0] for p in distinct]
    ys = [p[1] for p in distinct]
    print(f"bbox: x {min(xs)}..{max(xs)}  y {min(ys)}..{max(ys)}")

    # 2x stride print
    pos_set = distinct
    for y in range(0, 48, 1):
        row = ""
        for x in range(0, 64, 1):
            row += "#" if (x, y) in pos_set else "."
        print(f"  y={y:2d}: {row}")


if __name__ == "__main__":
    main()
