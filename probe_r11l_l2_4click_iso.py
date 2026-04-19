"""R11L L2: 4-click search with arm 1 locked at (33, 30).

Click 1 = (43, 61) puts arm 1 at (33, 30) — the isolated cluster target.
Clicks 2-4 = (A, hip, B) sweeps arm 2 at 4px resolution.

Also searches: arm 1 at (33, 30) via click 1, then OTHER patterns for clicks 2-4
(not just A-hip-B — also hip-first, hip-last, two-hips).
"""
import arc_agi
from arcengine import GameAction
import time

L1 = [(36, 13), (26, 61), (42, 30)]
ARM1_CLICK = (43, 61)  # puts arm 1 at (33, 30)
ARM2_HIPS = [(45, 35), (54, 48)]
ALL_HIPS = [(49, 9), (8, 21), (45, 35), (54, 48)]


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

    grid4 = list(range(0, 64, 4))
    grid8 = list(range(0, 64, 8))
    t0 = time.time()

    # Phase 1: (43,61) then (A, arm2_hip, B) at 4px
    print(f"=== Phase 1: (43,61) + (A, hip, B) at 4px ===")
    total = 2 * len(grid4)**2 * len(grid4)**2
    print(f"Trials: {total}")
    done = 0
    wins = []

    for hip in ARM2_HIPS:
        for a_x in grid4:
            for a_y in grid4:
                for b_x in grid4:
                    for b_y in grid4:
                        obs = play([ARM1_CLICK, (a_x, a_y), hip, (b_x, b_y)])
                        done += 1
                        if obs.levels_completed >= 2:
                            wins.append(((a_x, a_y), hip, (b_x, b_y)))
                            print(f"  WIN: (43,61)→({a_x},{a_y})→{hip}→({b_x},{b_y})")
                            if len(wins) >= 10:
                                print(f"Done: {time.time()-t0:.0f}s")
                                return
                if done % 5000 == 0:
                    elapsed = time.time() - t0
                    rate = done / elapsed if elapsed > 0 else 0
                    eta = (total - done) / rate if rate > 0 else 0
                    print(f"  [{done}/{total}] {elapsed:.0f}s, ~{eta:.0f}s remaining")
    print(f"Phase 1 wins: {len(wins)} ({time.time()-t0:.0f}s)")

    # Phase 2: (43,61) + hip FIRST patterns at 8px
    if not wins:
        print(f"\n=== Phase 2: (43,61) + unusual 3-click patterns ===")
        # (43,61), hip, A, B
        for hip in ALL_HIPS:
            for a_x in grid8:
                for a_y in grid8:
                    for b_x in grid8:
                        for b_y in grid8:
                            obs = play([ARM1_CLICK, hip, (a_x, a_y), (b_x, b_y)])
                            if obs.levels_completed >= 2:
                                print(f"  WIN: (43,61)→{hip}→({a_x},{a_y})→({b_x},{b_y})")
                                wins.append(("hip-first", hip, (a_x, a_y), (b_x, b_y)))
                            # Also: (43,61), A, B, hip
                            obs2 = play([ARM1_CLICK, (a_x, a_y), (b_x, b_y), hip])
                            if obs2.levels_completed >= 2:
                                print(f"  WIN: (43,61)→({a_x},{a_y})→({b_x},{b_y})→{hip}")
                                wins.append(("hip-last", (a_x, a_y), (b_x, b_y), hip))
        print(f"Phase 2 wins: {len(wins)} ({time.time()-t0:.0f}s)")

    print(f"\nTOTAL: {len(wins)} wins in {time.time()-t0:.0f}s")


if __name__ == "__main__":
    main()
