"""R11L: L2 random search with longer rollouts (25 clicks) and more trials.

Previous 2000×12 failed. Try 5000×25.
"""
import random
import arc_agi
from arcengine import GameAction


def main():
    random.seed(3)
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    N = 5000
    STEPS = 25

    for r in range(N):
        env.reset()
        for cx, cy in L1:
            env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        # Now in L2
        path = []
        for s in range(STEPS):
            cx = random.randint(0, 63)
            cy = random.randint(0, 63)
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            path.append((cx, cy))
            if obs2.levels_completed >= 2:
                print(f"L2 WIN rollout={r} step={s} lc={obs2.levels_completed}")
                print(f"  path: {path}")
                return path
        if r % 500 == 0 and r > 0:
            print(f"rollout {r}: no win yet")
    print(f"\nno L2 win in {N} rollouts × {STEPS} steps")


if __name__ == "__main__":
    main()
