"""R11L L2: massive targeted random search at 1px precision.

Instead of grid sweep, use random samples biased toward likely patterns.
Each trial tests 3 or 4 random clicks with one always being a hip.
500K trials should finish in ~30 min.
"""
import random
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

    def rand_pos():
        return (random.randint(0, 63), random.randint(0, 63))

    t0 = time.time()
    wins = []
    N = 500000

    for i in range(N):
        # Choose pattern type randomly
        ptype = random.choice([
            "AhB",      # standard: A, hip, B
            "AhBc",     # 4-click: A, hip, B, extra
            "cAhB",     # 4-click: extra first, A, hip, B
            "h1h2A",    # two hips + A
            "Ah1h2",    # A + two hips
            "ABh",      # A, B, hip (non-standard order)
            "hAB",      # hip, A, B
            "ABCD",     # pure random 4-click
            "ABC",      # pure random 3-click
        ])

        hip = random.choice(ALL_HIPS)
        hip2 = random.choice([h for h in ALL_HIPS if h != hip])

        if ptype == "AhB":
            seq = [rand_pos(), hip, rand_pos()]
        elif ptype == "AhBc":
            seq = [rand_pos(), hip, rand_pos(), rand_pos()]
        elif ptype == "cAhB":
            seq = [rand_pos(), rand_pos(), hip, rand_pos()]
        elif ptype == "h1h2A":
            seq = [hip, hip2, rand_pos()]
        elif ptype == "Ah1h2":
            seq = [rand_pos(), hip, hip2]
        elif ptype == "ABh":
            seq = [rand_pos(), rand_pos(), hip]
        elif ptype == "hAB":
            seq = [hip, rand_pos(), rand_pos()]
        elif ptype == "ABCD":
            seq = [rand_pos(), rand_pos(), rand_pos(), rand_pos()]
        elif ptype == "ABC":
            seq = [rand_pos(), rand_pos(), rand_pos()]

        obs = play(seq)
        if obs.levels_completed >= 2:
            wins.append((ptype, seq))
            print(f"WIN #{len(wins)}: {ptype} {seq}")
            if len(wins) >= 10:
                break

        if (i + 1) % 50000 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            print(f"[{i+1}/{N}] {elapsed:.0f}s, {rate:.0f}/s, {len(wins)} wins")

    print(f"\nTotal: {len(wins)} wins in {N} trials ({time.time()-t0:.0f}s)")


if __name__ == "__main__":
    main()
