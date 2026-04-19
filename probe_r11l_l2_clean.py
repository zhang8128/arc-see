"""R11L L2: re-verify ALL basic click behaviors using fresh reset (Method A).

The deepcopy pattern introduced subtle state inconsistencies. Use reset each
time and re-derive:
  - what each click does to arm 1 foot (24, 12) and arm 2 foot (49, 41)
  - which clicks are no-ops, which move arms, which game-over
  - the actual game-over trigger
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def sixes(g):
    return sorted([(int(x), int(y)) for y, x in np.argwhere(g == 6)])


def play(env, L1, extras):
    env.reset()
    obs = None
    for px, py in L1:
        obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
    for cx, cy in extras:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    return obs


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)
    L1 = [(36, 13), (26, 61), (42, 30)]

    # Single-click sweep of representative positions
    print("-- single clicks (fresh reset each) --")
    for click in [(30, 30), (10, 10), (45, 35), (26, 54), (54, 48),
                  (8, 21), (49, 9), (40, 51), (20, 20), (50, 50),
                  (0, 0), (40, 20), (30, 60), (60, 30)]:
        obs = play(env, L1, [click])
        g = np.array(obs.frame[-1], dtype=np.int64)
        print(f"  click {click}: sixes={sixes(g)}  state={obs.state.name}")

    # Classic L1-style pattern with each hip as middle
    print("\n-- L1 pattern with each L2 hip --")
    for hip in [(49, 9), (8, 21), (45, 35), (54, 48)]:
        obs = play(env, L1, [(10, 10), hip, (40, 40)])
        g = np.array(obs.frame[-1], dtype=np.int64)
        print(f"  (10,10)→{hip}→(40,40): sixes={sixes(g)}  lc={obs.levels_completed}")

    # Test: can we win L2 with 1 or 2 clicks now (fresh reset, 8px grid)?
    print("\n-- 2-click search for L2 win (8px grid) --")
    wins = 0
    grid = list(range(0, 64, 8))
    for cx1 in grid:
        for cy1 in grid:
            for cx2 in grid:
                for cy2 in grid:
                    obs = play(env, L1, [(cx1, cy1), (cx2, cy2)])
                    if obs.levels_completed >= 2:
                        print(f"  WIN: ({cx1},{cy1}), ({cx2},{cy2})")
                        wins += 1
                        if wins >= 5:
                            return
    print(f"  total 2-click wins: {wins}")


if __name__ == "__main__":
    main()
