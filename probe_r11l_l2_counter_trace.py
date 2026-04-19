"""R11L L2: trace counter marks over a 10-click sequence for various clicks.
Determine exactly when and why counter stops incrementing.
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
    snap = copy.deepcopy(env._game)

    tests = [(10, 10), (30, 30), (40, 20), (0, 0), (50, 50)]
    for click in tests:
        print(f"-- click {click} x 10 --")
        env._game = copy.deepcopy(snap)
        for i in range(10):
            obs = env.step(GameAction.ACTION6, data={"x": click[0], "y": click[1]})
            g = np.array(obs.frame[-1], dtype=np.int64)
            counter = sum(1 for r in range(g.shape[0]) if int(g[r, 0]) == 5)
            print(f"  click{i}: counter={counter} state={obs.state.name}")
            if obs.state.name == "GAME_OVER":
                break


if __name__ == "__main__":
    main()
