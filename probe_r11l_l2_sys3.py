"""R11L L2: systematic 3-click enumeration.

For each (hip, target1, target2) combo, test if it wins L2. 4 hips × 256
coarse targets × 256 coarse targets = 262K combos. Use deepcopy for speed.
Actually that's too much. Use 8-pixel stride: 4 * 64 * 64 = 16K combos.
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

    hips = [(49, 9), (8, 21), (45, 35), (54, 48)]
    targets = [(x, y) for x in range(0, 64, 8) for y in range(0, 64, 8)]
    print(f"targets: {len(targets)}, hips: {len(hips)}")
    print(f"total 3-click combos: {len(hips) * len(targets) * len(targets)}")

    wins = []
    count = 0
    for hip in hips:
        for t1 in targets:
            for t2 in targets:
                env._game = copy.deepcopy(snap)
                env.step(GameAction.ACTION6, data={"x": hip[0], "y": hip[1]})
                env.step(GameAction.ACTION6, data={"x": t1[0], "y": t1[1]})
                obs = env.step(GameAction.ACTION6, data={"x": t2[0], "y": t2[1]})
                count += 1
                if obs.levels_completed >= 2:
                    wins.append((hip, t1, t2))
                    print(f"  WIN: {hip} → {t1} → {t2}")
                    if len(wins) >= 5:
                        return
    print(f"\ntried {count} combos, wins: {len(wins)}")

    # Also try 2-click: (hip, target)
    print("\n-- 2-click --")
    for hip in hips:
        for t in targets:
            env._game = copy.deepcopy(snap)
            env.step(GameAction.ACTION6, data={"x": hip[0], "y": hip[1]})
            obs = env.step(GameAction.ACTION6, data={"x": t[0], "y": t[1]})
            if obs.levels_completed >= 2:
                print(f"  WIN 2-click: {hip} → {t}")
                return

    print("no 2-click wins either")


if __name__ == "__main__":
    main()
