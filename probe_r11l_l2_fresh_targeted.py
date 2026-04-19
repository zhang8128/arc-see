"""R11L L2: targeted 3-click sequences with fresh reset.

Now that I know the mechanic is (A → arm2_hip → B), test variations:
- Each L1-style pattern with various A and B around the c-diamond goal.
- Goal-placement variations.
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

    # Target: arm 2 foot at (40, 51) via (A, (45, 35), (26, 54))
    # Sweep A
    print("-- A → (45, 35) → (26, 54) with various A --")
    for a_x in range(0, 64, 4):
        for a_y in range(0, 64, 4):
            obs = play([(a_x, a_y), (45, 35), (26, 54)])
            if obs.levels_completed >= 2:
                print(f"  WIN: A=({a_x},{a_y})")
                return
            g = np.array(obs.frame[-1], dtype=np.int64)
            s = sixes(g)
            if s != [(24, 12), (40, 51)] and s != [(22, 13), (40, 51)] and s != [(31, 14), (40, 51)]:
                print(f"  unusual: A=({a_x},{a_y}) → sixes={s}")
    print("  no wins in this sweep")

    # Also try (A, (54, 48), B) with various A and B
    print("\n-- A → (54, 48) → B --")
    wins = 0
    for a_x in range(0, 64, 8):
        for a_y in range(0, 64, 8):
            for b_x in range(0, 64, 8):
                for b_y in range(0, 64, 8):
                    obs = play([(a_x, a_y), (54, 48), (b_x, b_y)])
                    if obs.levels_completed >= 2:
                        print(f"  WIN: ({a_x},{a_y}) → (54,48) → ({b_x},{b_y})")
                        wins += 1
                        if wins >= 5:
                            return
    print(f"  wins: {wins}")


if __name__ == "__main__":
    main()
