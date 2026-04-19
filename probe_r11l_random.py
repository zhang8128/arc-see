"""R11L: random-search 1000 game rollouts up to 10 clicks each, tracking:
  - state changes (any transition out of NOT_FINISHED)
  - levels_completed changes (any increment)
  - available_actions changes (new actions unlocked)
  - full_reset changes

If anything ever changes beyond what we've seen, print the trigger.
"""
import random
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def foot_pos(grid):
    sixes = np.argwhere(grid == 6)
    if len(sixes) != 1:
        return None
    y, x = sixes[0]
    return (int(x), int(y))


def sig(obs):
    """Summary signature of interesting obs fields."""
    return (
        obs.state.name,
        obs.levels_completed,
        tuple(obs.available_actions),
        obs.full_reset,
    )


def main():
    random.seed(42)
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    # Baseline signature
    obs = env.reset()
    base_sig = sig(obs)
    print(f"baseline sig: {base_sig}")
    print(f"baseline foot: {foot_pos(frame(obs))}")

    N_ROLLOUTS = 500
    STEPS = 10
    unique_sigs = {base_sig}
    best_progress = None  # (rollout_idx, step_idx, sig, path)

    for r in range(N_ROLLOUTS):
        env.reset()
        path = []
        for s in range(STEPS):
            cx = random.randint(0, 63)
            cy = random.randint(0, 63)
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            path.append((cx, cy))
            sg = sig(obs2)
            if sg != base_sig:
                if sg not in unique_sigs:
                    unique_sigs.add(sg)
                    print(f"new sig at rollout {r}, step {s}: {sg}")
                    print(f"  path: {path}")
                if best_progress is None or obs2.levels_completed > best_progress[2][1]:
                    best_progress = (r, s, sg, list(path))
            if obs2.levels_completed > 0 or obs2.state.name == "WIN":
                print(f"\n*** PROGRESS at rollout {r} step {s}: {sg} ***")
                print(f"path: {path}")
                return

    print(f"\nunique sigs seen: {len(unique_sigs)}")
    for s in unique_sigs:
        print(f"  {s}")
    if best_progress:
        print(f"\nbest: rollout={best_progress[0]} step={best_progress[1]} sig={best_progress[2]}")
        print(f"  path: {best_progress[3]}")


if __name__ == "__main__":
    main()
