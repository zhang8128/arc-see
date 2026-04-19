"""R11L L2: dump frame after (45, 35), (26, 54) and find arm 2's head.

The click (26, 54) should place arm 2's head at (27, 55) (click + (1,1)).
Let's verify and see the full arm 2 structure.
"""
import copy
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
    g0 = np.array(env.step(GameAction.ACTION6, data={"x": 0, "y": 0}).frame[-1], dtype=np.int64)
    # Undo: reset and replay L1
    env.reset()
    for cx, cy in L1:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    snap = copy.deepcopy(env._game)

    # Apply the arm 2 placement
    env._game = copy.deepcopy(snap)
    env.step(GameAction.ACTION6, data={"x": 45, "y": 35})
    obs = env.step(GameAction.ACTION6, data={"x": 26, "y": 54})
    g = np.array(obs.frame[-1], dtype=np.int64)

    chars = "0123456789abcdef"
    print("--- L2 after (45, 35), (26, 54) ---")
    for y in range(64):
        row = []
        for x in range(64):
            v = int(g[y, x])
            row.append("." if v < 0 else (chars[v] if 0 <= v < 16 else "?"))
        print("".join(row))

    # Look for head sprites: small clusters of 0-outline with a center
    # Find all cells with 3+ 0-neighbors of color f (15) or c (12)
    print("\n-- possible head positions (f/c with 3+ 0 neighbors) --")
    for color in (15, 12):
        ys, xs = np.where(g == color)
        for y, x in zip(ys, xs):
            if y < 1 or y > 62 or x < 1 or x > 62:
                continue
            nb = [int(g[y - 1, x]), int(g[y + 1, x]),
                  int(g[y, x - 1]), int(g[y, x + 1])]
            if nb.count(0) >= 3:
                print(f"  head-like at ({x}, {y}) color={color}")


if __name__ == "__main__":
    main()
