"""R11L L2: try the L1 win pattern ON L2.

Maybe each level is shaped similarly and L1's (36,13) → (26,61) → (42,30)
works on L2 too. Also try scaled/shifted variants.
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

    # Test 1: same L1 sequence
    print("-- L1 sequence replayed in L2 --")
    env._game = copy.deepcopy(snap)
    for cx, cy in L1:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    print(f"  lc={obs.levels_completed}")

    # Test 2: L1 reversed order
    env._game = copy.deepcopy(snap)
    for cx, cy in reversed(L1):
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    print(f"  reversed: lc={obs.levels_completed}")

    # Test 3: 2 L1 rounds
    env._game = copy.deepcopy(snap)
    for cx, cy in L1 + L1:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    print(f"  2 L1 rounds: lc={obs.levels_completed}")

    # Test 4: L1 + alternate perm (should test visiting diamonds repeatedly)
    alts = [
        L1,
        [(42, 30), (26, 61), (36, 13)],
        # L1 but with adjustments
        [(36, 13), (26, 58), (42, 30)],
        [(36, 13), (27, 59), (42, 30)],
        # L1 goal visits with L2 hip middles
        [(36, 13), (49, 9), (42, 30)],
        [(36, 13), (8, 21), (42, 30)],
        [(36, 13), (45, 35), (42, 30)],
        [(36, 13), (54, 48), (42, 30)],
    ]
    print("\n-- L1 pattern variants --")
    for seq in alts:
        env._game = copy.deepcopy(snap)
        lc = 0
        for cx, cy in seq:
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            lc = max(lc, obs.levels_completed)
        marker = " *** WIN ***" if lc >= 2 else ""
        print(f"  {seq}: lc={lc}{marker}")


if __name__ == "__main__":
    main()
