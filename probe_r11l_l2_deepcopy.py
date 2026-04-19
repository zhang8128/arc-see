"""R11L L2: use deepcopy to skip L1 replay, enabling much longer search.

Save an env state that's already in L2. Deepcopy it for each trial and run
longer random searches.
"""
import copy
import random
import arc_agi
from arcengine import GameAction


def main():
    random.seed(11)
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]

    # Get to L2
    env.reset()
    for cx, cy in L1:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    # Snapshot the internal game state
    try:
        snap = copy.deepcopy(env._game)
        print(f"snapshot succeeded: {type(snap).__name__}")
    except Exception as e:
        print(f"deepcopy failed: {e}")
        return

    # Verify: restore and step
    env._game = copy.deepcopy(snap)
    obs = env.step(GameAction.ACTION6, data={"x": 30, "y": 30})
    print(f"test step after restore: lc={obs.levels_completed}")

    # Now run a much longer search
    N = 15000
    STEPS = 20
    hips = [(49, 9), (8, 21), (45, 35), (54, 48)]
    # Bias clicks toward hips (50%), toward (26, 54) (10%), random (40%)
    for r in range(N):
        env._game = copy.deepcopy(snap)
        path = []
        for s in range(STEPS):
            rx = random.random()
            if rx < 0.5:
                cx, cy = random.choice(hips)
            elif rx < 0.6:
                cx, cy = (26, 54)
            else:
                cx = random.randint(0, 63)
                cy = random.randint(0, 63)
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            path.append((cx, cy))
            if obs.levels_completed >= 2:
                print(f"L2 WIN rollout={r} step={s} path={path}")
                return
        if r % 3000 == 0 and r > 0:
            print(f"rollout {r}: no L2 win yet")
    print(f"\nno L2 win in {N} rollouts")


if __name__ == "__main__":
    main()
