"""R11L L2: try unusual click patterns that don't follow (A, hip, B).

Patterns tested:
- 1-click wins at 1px resolution (exhaustive)
- 2-click wins at 2px resolution
- 3-click with hip FIRST: (hip, A, B)
- 3-click with hip LAST: (A, B, hip)
- 3-click with two hips: (hip1, hip2, A)
- 3-click with same hip twice: (hip, hip, A)
- 2-click targeting specific arm 1 hips: (arm1_hip, B)
"""
import arc_agi
from arcengine import GameAction
import time

L1 = [(36, 13), (26, 61), (42, 30)]
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

    t0 = time.time()

    # Test 1: exhaustive 1-click at 1px
    print("=== 1-click exhaustive (64x64=4096) ===")
    wins1 = 0
    for x in range(64):
        for y in range(64):
            obs = play([(x, y)])
            if obs.levels_completed >= 2:
                print(f"  WIN: ({x},{y})")
                wins1 += 1
    print(f"  1-click wins: {wins1} ({time.time()-t0:.0f}s)")

    # Test 2: 2-click at 2px
    print("\n=== 2-click (2px grid, 32^4=1M) ===")
    grid2 = list(range(0, 64, 2))
    wins2 = 0
    done = 0
    for x1 in grid2:
        for y1 in grid2:
            for x2 in grid2:
                for y2 in grid2:
                    obs = play([(x1, y1), (x2, y2)])
                    done += 1
                    if obs.levels_completed >= 2:
                        print(f"  WIN: ({x1},{y1}), ({x2},{y2})")
                        wins2 += 1
                        if wins2 >= 5:
                            print(f"  stopping early ({time.time()-t0:.0f}s)")
                            return
        if done % 10000 == 0:
            elapsed = time.time() - t0
            total = len(grid2)**4
            rate = done / elapsed if elapsed > 0 else 0
            eta = (total - done) / rate if rate > 0 else 0
            print(f"  [{done}/{total}] {elapsed:.0f}s, ~{eta:.0f}s remaining")
    print(f"  2-click wins: {wins2} ({time.time()-t0:.0f}s)")

    # Test 3: 3-click with hip FIRST (hip, A, B) at 8px
    print("\n=== 3-click hip-first (hip, A, B) 8px ===")
    grid8 = list(range(0, 64, 8))
    wins3 = 0
    for hip in ALL_HIPS:
        for a_x in grid8:
            for a_y in grid8:
                for b_x in grid8:
                    for b_y in grid8:
                        obs = play([hip, (a_x, a_y), (b_x, b_y)])
                        if obs.levels_completed >= 2:
                            print(f"  WIN: {hip} → ({a_x},{a_y}) → ({b_x},{b_y})")
                            wins3 += 1
                            if wins3 >= 5:
                                return
    print(f"  hip-first wins: {wins3} ({time.time()-t0:.0f}s)")

    # Test 4: 3-click with hip LAST (A, B, hip) at 8px
    print("\n=== 3-click hip-last (A, B, hip) 8px ===")
    wins4 = 0
    for hip in ALL_HIPS:
        for a_x in grid8:
            for a_y in grid8:
                for b_x in grid8:
                    for b_y in grid8:
                        obs = play([(a_x, a_y), (b_x, b_y), hip])
                        if obs.levels_completed >= 2:
                            print(f"  WIN: ({a_x},{a_y}) → ({b_x},{b_y}) → {hip}")
                            wins4 += 1
                            if wins4 >= 5:
                                return
    print(f"  hip-last wins: {wins4} ({time.time()-t0:.0f}s)")

    # Test 5: 3-click with two different hips (hip1, hip2, A) at 8px
    print("\n=== 3-click two-hips (hip1, hip2, A) 8px ===")
    wins5 = 0
    from itertools import permutations
    for h1, h2 in permutations(ALL_HIPS, 2):
        for a_x in grid8:
            for a_y in grid8:
                obs = play([h1, h2, (a_x, a_y)])
                if obs.levels_completed >= 2:
                    print(f"  WIN: {h1} → {h2} → ({a_x},{a_y})")
                    wins5 += 1
                obs = play([(a_x, a_y), h1, h2])
                if obs.levels_completed >= 2:
                    print(f"  WIN: ({a_x},{a_y}) → {h1} → {h2}")
                    wins5 += 1
    print(f"  two-hips wins: {wins5} ({time.time()-t0:.0f}s)")

    print(f"\n=== TOTAL TIME: {time.time()-t0:.0f}s ===")


if __name__ == "__main__":
    main()
