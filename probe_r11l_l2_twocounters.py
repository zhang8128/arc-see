"""R11L L2: find the second counter (if any).

Compare col 0 and col 1 state across 5 clicks of (30, 30) vs (10, 10).
(30, 30) game-overs at click 4. (10, 10) does NOT. Something else must differ.
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

    def dump_col(g, col, label):
        return f"{label}: {''.join(str(int(g[r, col])) for r in range(g.shape[0]))}"

    # Both start from L2 init. Compare click-by-click.
    for click_name, click in [("(30, 30)", (30, 30)), ("(10, 10)", (10, 10))]:
        print(f"\n-- {click_name} x 5 --")
        env._game = copy.deepcopy(snap)
        init_g = np.array(env.step(GameAction.ACTION6, data={"x": click[0], "y": click[1]}).frame[-1], dtype=np.int64)
        # Actually start over to capture pre-click state
        env._game = copy.deepcopy(snap)
        for i in range(5):
            obs = env.step(GameAction.ACTION6, data={"x": click[0], "y": click[1]})
            g = np.array(obs.frame[-1], dtype=np.int64)
            print(f"  click{i}: state={obs.state.name}  lc={obs.levels_completed}")
            # Print column 0 (counter) and col 1
            c0 = "".join(f"{int(g[r, 0])}" for r in range(16))
            c1 = "".join(f"{int(g[r, 1])}" for r in range(16))
            print(f"    col0[0..15]: {c0}")
            print(f"    col1[0..15]: {c1}")


if __name__ == "__main__":
    main()
