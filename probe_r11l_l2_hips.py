"""R11L L2: test clicks on and near each of the 4 color-3 clusters.

For each cluster center, click there and dump what moved. Looking for:
  - which click produces which head/foot position
  - whether any triggers level advance
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    g0 = frame(obs)

    # Color-3 cluster centers from the earlier probe
    hip_candidates = [
        (49, 9),   # upper right
        (8, 21),   # upper left
        (45, 35),  # middle right
        (54, 48),  # lower right
    ]

    # Also the L2 head position
    head_l2 = (17, 6)

    # And the static 6 marker
    static_marker = (49, 41)

    test_clicks = hip_candidates + [
        (head_l2[0] - 1, head_l2[1] - 1),  # click to place head AT head_l2 (1,1 offset)
        (static_marker[0] - 1, static_marker[1] - 1),
        # Also try clicks at the 4 hip cluster centers minus (1,1)
        (48, 8), (7, 20), (44, 34), (53, 47),
    ]

    for cx, cy in test_clicks:
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(obs2)
        # Diff (excluding col 0)
        diffs = np.argwhere((g != g0) & (np.arange(g.shape[1])[None, :] != 0))
        print(f"\nclick({cx},{cy}): {len(diffs)} cells changed (non-col-0), lc={obs2.levels_completed}")
        # Which sprites changed? Sample the diff cells
        if len(diffs) == 0:
            print("  NO-OP")
            continue
        # List old->new transitions
        from collections import Counter
        trans = Counter()
        for y, x in diffs:
            trans[(int(g0[y, x]), int(g[y, x]))] += 1
        print(f"  transitions: {dict(trans)}")
        # Find new 6-cells and new c-rings
        new_sixes = [(int(x), int(y)) for y, x in np.argwhere(g == 6)]
        print(f"  new 6 positions: {new_sixes}")


if __name__ == "__main__":
    main()
