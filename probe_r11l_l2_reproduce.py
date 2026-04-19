"""R11L L2: reproduce the click (30, 30) behavior comparing reset vs deepcopy."""
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

    # Method A: fresh reset each time
    print("-- Method A: reset + L1 + click --")
    for click in [(30, 30), (10, 10), (45, 35), (26, 54)]:
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        obs = env.step(GameAction.ACTION6, data={"x": click[0], "y": click[1]})
        g = np.array(obs.frame[-1], dtype=np.int64)
        print(f"  click {click}: sixes={sixes(g)}  state={obs.state.name}")

    # Method B: deepcopy from snap
    print("\n-- Method B: deepcopy snap + click --")
    env.reset()
    for px, py in L1:
        env.step(GameAction.ACTION6, data={"x": px, "y": py})
    snap = copy.deepcopy(env._game)

    for click in [(30, 30), (10, 10), (45, 35), (26, 54)]:
        env._game = copy.deepcopy(snap)
        obs = env.step(GameAction.ACTION6, data={"x": click[0], "y": click[1]})
        g = np.array(obs.frame[-1], dtype=np.int64)
        print(f"  click {click}: sixes={sixes(g)}  state={obs.state.name}")


if __name__ == "__main__":
    main()
