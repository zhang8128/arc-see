"""R11L L2: test L1-style pattern for ARM 1 (with arm1 hips as middle click).

If the hip-swap mechanic works for arm 1 too, clicks (A, arm1_hip, B) should
move arm 1 foot via midpoint(other_arm1_hip, B).

For hip (49, 9), pivot = (8, 21). foot = midpoint((8, 21), B).
For hip (8, 21), pivot = (49, 9). foot = midpoint((49, 9), B).

Test various B and see if arm 1 foot matches this formula.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def sixes(g):
    return sorted([(int(x), int(y)) for y, x in np.argwhere(g == 6)])


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

    # Verify arm 1 formula after (A, arm1_hip, B)
    print("-- A → (49, 9) → B, expected foot = midpoint((8, 21), B) --")
    for B in [(10, 10), (30, 30), (40, 40), (20, 40), (50, 20), (15, 35)]:
        obs = play([(10, 5), (49, 9), B])
        g = np.array(obs.frame[-1], dtype=np.int64)
        expected = ((8 + B[0]) // 2, (21 + B[1]) // 2)
        print(f"  B={B}: sixes={sixes(g)}  expected_arm1={expected}  lc={obs.levels_completed}")

    print("\n-- A → (8, 21) → B, expected foot = midpoint((49, 9), B) --")
    for B in [(10, 10), (30, 30), (40, 40), (20, 40), (50, 20)]:
        obs = play([(10, 5), (8, 21), B])
        g = np.array(obs.frame[-1], dtype=np.int64)
        expected = ((49 + B[0]) // 2, (9 + B[1]) // 2)
        print(f"  B={B}: sixes={sixes(g)}  expected_arm1={expected}  lc={obs.levels_completed}")

    # Now the key question: if arm 1 works the same way, we have 4 hips and 2 arms.
    # Maybe the win is: visit 2 goal diamonds per arm, with the hip as middle each time.
    # 6 clicks total: (A1, arm1-hip, B1, A2, arm2-hip, B2)

    # Or maybe simpler: one full arm 1 pattern + one full arm 2 pattern = 6 clicks
    print("\n-- full L1-style pattern for BOTH arms --")
    import itertools
    arm1_hips = [(49, 9), (8, 21)]
    arm2_hips = [(45, 35), (54, 48)]

    # Sample A and B positions near the known goals and interesting places
    As = [(10, 10), (36, 13), (16, 5), (20, 20)]
    Bs = [(26, 54), (40, 40), (42, 30), (40, 51)]

    tried = 0
    for h1 in arm1_hips:
        for h2 in arm2_hips:
            for a1 in As:
                for b1 in Bs:
                    for a2 in As:
                        for b2 in Bs:
                            seq = [a1, h1, b1, a2, h2, b2]
                            obs = play(seq)
                            tried += 1
                            if obs.levels_completed >= 2:
                                print(f"  WIN: {seq}")
                                return
    print(f"  no wins in {tried} trials")


if __name__ == "__main__":
    main()
