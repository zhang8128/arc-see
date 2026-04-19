"""R11L L2: clean 3-click search with fresh reset each time.

L1-pattern: (A, hip, B) where hip is one of the 4 hip centers and A, B sweep.
Fresh reset each trial (no deepcopy).

Expected runtime: ~7 minutes (16K combos × 5 steps × 5ms).
"""
import arc_agi
from arcengine import GameAction


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)
    L1 = [(36, 13), (26, 61), (42, 30)]

    def play(seq):
        env.reset()
        obs = None
        for px, py in L1:
            obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
        for cx, cy in seq:
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        return obs

    hips = [(49, 9), (8, 21), (45, 35), (54, 48)]
    grid = list(range(0, 64, 8))  # 8 values per axis = 64 positions total

    print(f"search space: 4 hips × {len(grid)**2} × {len(grid)**2} = {4 * (len(grid)**2)**2}")

    wins = []
    for hip in hips:
        for a_x in grid:
            for a_y in grid:
                for b_x in grid:
                    for b_y in grid:
                        obs = play([(a_x, a_y), hip, (b_x, b_y)])
                        if obs.levels_completed >= 2:
                            wins.append((a_x, a_y, hip, b_x, b_y))
                            print(f"  WIN: ({a_x},{a_y}) → {hip} → ({b_x},{b_y})")
                            if len(wins) >= 5:
                                return
    print(f"\ntotal wins found: {len(wins)}")


if __name__ == "__main__":
    main()
