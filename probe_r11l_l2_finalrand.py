"""R11L L2: final large random search with deepcopy for speed.

30K rollouts × 30 steps. Mostly random with light bias toward hips and
interesting targets identified so far.
"""
import copy
import random
import arc_agi
from arcengine import GameAction


def main():
    random.seed(17)
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    snap = copy.deepcopy(env._game)

    hips = [(49, 9), (8, 21), (45, 35), (54, 48)]
    interesting = hips + [(48, 8), (7, 20), (44, 34), (53, 47),
                          (26, 54), (42, 57), (45, 60),
                          (36, 13), (16, 5), (35, 19),
                          (48, 40), (37, 50)]

    N = 30000
    STEPS = 30
    best_seen_lc = 1
    for r in range(N):
        env._game = copy.deepcopy(snap)
        path = []
        for s in range(STEPS):
            rx = random.random()
            if rx < 0.3:
                cx, cy = random.choice(interesting)
            else:
                cx = random.randint(0, 63)
                cy = random.randint(0, 63)
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            path.append((cx, cy))
            if obs.levels_completed > best_seen_lc:
                best_seen_lc = obs.levels_completed
                print(f"NEW BEST lc={obs.levels_completed} rollout={r} step={s}")
                if obs.levels_completed >= 2:
                    print(f"L2 WIN path={path}")
                    return
        if r % 5000 == 0 and r > 0:
            print(f"rollout {r}: best lc={best_seen_lc}")
    print(f"\nno L2 win in {N} × {STEPS}. best lc={best_seen_lc}")


if __name__ == "__main__":
    main()
