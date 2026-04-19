"""R11L L2: print ALL 6-cells after each click in a sequence."""
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

    for seq_name, seq in [
        ("(30, 30) x 5", [(30, 30)] * 5),
        ("(10, 10) x 5", [(10, 10)] * 5),
        ("(45, 35), (26, 54), (45, 35), (26, 54)", [(45, 35), (26, 54), (45, 35), (26, 54)]),
    ]:
        print(f"\n-- {seq_name} --")
        env._game = copy.deepcopy(snap)
        for i, (cx, cy) in enumerate(seq):
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            g = np.array(obs.frame[-1], dtype=np.int64)
            sixes = sorted([(int(x), int(y)) for y, x in np.argwhere(g == 6)])
            print(f"  click{i} {(cx, cy)}: sixes={sixes}  state={obs.state.name}")


if __name__ == "__main__":
    main()
