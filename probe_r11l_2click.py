"""R11L: search for a 2-click L1 solution.

Hypothesis: the win is 'click to place head on hip' then 'click anywhere to
advance'. Test all 2-click combos where either click places head on the hip
f-center area.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    # Enumerate candidate "first clicks" (hip-placement clicks).
    # The previous winning click was (26, 61) which clamped head to (27, 59).
    # Try a broad range of hip-area clicks.
    hip_clicks = []
    for cx in range(20, 35):
        for cy in range(55, 64):
            hip_clicks.append((cx, cy))

    # Second clicks: sample a reasonable grid
    second_clicks = []
    for cx in range(4, 60, 4):
        for cy in range(12, 60, 4):
            second_clicks.append((cx, cy))

    print(f"trying {len(hip_clicks)} × {len(second_clicks)} = {len(hip_clicks) * len(second_clicks)} combos")

    wins_2 = []
    for c1 in hip_clicks:
        for c2 in second_clicks:
            env.reset()
            env.step(GameAction.ACTION6, data={"x": c1[0], "y": c1[1]})
            obs2 = env.step(GameAction.ACTION6, data={"x": c2[0], "y": c2[1]})
            if obs2.levels_completed > 0:
                wins_2.append((c1, c2))
                if len(wins_2) <= 5:
                    print(f"  2-click WIN: {c1}, {c2}")

    print(f"\ntotal 2-click wins: {len(wins_2)}")

    if not wins_2:
        # Try 1-click (previously tested but maybe with wrong signal)
        print("\n-- single-click sweep with levels_completed check (sanity) --")
        wins_1 = []
        for cx in range(64):
            for cy in range(64):
                env.reset()
                obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
                if obs2.levels_completed > 0:
                    wins_1.append((cx, cy))
        print(f"  single-click wins: {len(wins_1)}")


if __name__ == "__main__":
    main()
