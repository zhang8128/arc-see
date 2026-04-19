"""R11L L2: 3-click search at 4px resolution (finer than previous 8px).

Previous 8px search: 4 hips × 64 A × 64 B = 16K → 0 wins.
This: 2 arm2 hips × 256 A × 256 B = 131K trials → ~65 min.

If no wins: the answer requires 4 clicks or pixel-precise coordinates.
"""
import arc_agi
from arcengine import GameAction
import time

L1 = [(36, 13), (26, 61), (42, 30)]
ARM2_HIPS = [(45, 35), (54, 48)]


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    def play(seq):
        env.reset()
        obs = None
        for px, py in L1:
            obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
        for cx, cy in seq:
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        return obs

    grid = list(range(0, 64, 4))  # 16 values → 256 positions
    total = 2 * len(grid)**2 * len(grid)**2
    print(f"Search: 2 hips × {len(grid)**2} A × {len(grid)**2} B = {total}")

    t0 = time.time()
    done = 0
    wins = []

    for hip in ARM2_HIPS:
        for a_x in grid:
            for a_y in grid:
                for b_x in grid:
                    for b_y in grid:
                        obs = play([(a_x, a_y), hip, (b_x, b_y)])
                        done += 1
                        if obs.levels_completed >= 2:
                            wins.append(((a_x, a_y), hip, (b_x, b_y)))
                            print(f"  WIN #{len(wins)}: ({a_x},{a_y}) → {hip} → ({b_x},{b_y})")
                            if len(wins) >= 10:
                                print(f"\nDone in {time.time()-t0:.0f}s ({done} trials)")
                                return
                if done % 5000 == 0:
                    elapsed = time.time() - t0
                    rate = done / elapsed if elapsed > 0 else 0
                    eta = (total - done) / rate if rate > 0 else 0
                    print(f"  [{done}/{total}] {elapsed:.0f}s elapsed, ~{eta:.0f}s remaining")

    print(f"\nTotal wins: {len(wins)} in {time.time()-t0:.0f}s ({done} trials)")


if __name__ == "__main__":
    main()
