"""R11L L2: map 'free' clicks (that don't increment the counter).

For each 8-pixel stride click, measure counter delta from 0 to 1.
"""
import copy
import numpy as np
import arc_agi
from arcengine import GameAction


def counter_marks(g):
    return sum(1 for r in range(g.shape[0]) if int(g[r, 0]) == 5)


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    snap = copy.deepcopy(env._game)

    # For each click, measure counter delta
    free_clicks = set()
    paid_clicks = set()
    for cy in range(64):
        for cx in range(64):
            env._game = copy.deepcopy(snap)
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            g = np.array(obs.frame[-1], dtype=np.int64)
            c = counter_marks(g)
            if c == 0:
                free_clicks.add((cx, cy))
            else:
                paid_clicks.add((cx, cy))

    print(f"free clicks (counter=0 after): {len(free_clicks)}")
    print(f"paid clicks (counter>0 after): {len(paid_clicks)}")

    # Visualize free-click regions
    print("\nFree-click map (F = free):")
    for cy in range(0, 64, 2):
        row = "".join("F" if (cx, cy) in free_clicks else "." for cx in range(0, 64, 2))
        print(f"  y={cy:2d}: {row}")


if __name__ == "__main__":
    main()
