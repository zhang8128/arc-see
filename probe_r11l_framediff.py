"""R11L L2 frame analysis — understand what ACTUALLY changes on each click.

Instead of just tracking color-6 positions, this captures full frame diffs
to identify patterns we might be missing.
"""
import arc_agi
import numpy as np
from arcengine import GameAction
from collections import Counter

L1 = [(36, 13), (26, 61), (42, 30)]


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    def fresh_l2():
        """Get to L2 with correct double-reset."""
        env.reset()
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        # Return the L2 initial frame
        obs = env.step(GameAction.ACTION6, data={"x": 999, "y": 999})
        # Hmm that costs a click. Let me get the frame differently.
        return None  # Can't get frame without a click

    # Get L2 initial frame by making the env step to L2
    env.reset()
    env.reset()
    for px, py in L1:
        obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
    l2_init = np.array(obs.frame[-1], dtype=np.int64)

    print("=== L2 initial frame analysis ===")
    census = Counter()
    for r in range(64):
        for c in range(64):
            census[int(l2_init[r, c])] += 1
    print("Color census:")
    for color, count in sorted(census.items()):
        print(f"  color {color:2d}: {count} cells")

    # Now test a few clicks and see FULL frame diff
    clicks_to_test = [
        (10, 10),   # moves arm1
        (30, 30),   # no-op for arm1 (correct reset)
        (45, 35),   # arm2 hip
        (54, 48),   # arm2 hip
        (8, 21),    # arm1 hip
        (49, 9),    # arm1 hip
    ]

    for cx, cy in clicks_to_test:
        env.reset()
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        frame = np.array(obs.frame[-1], dtype=np.int64)

        diff_mask = frame != l2_init
        n_changed = int(diff_mask.sum())

        # Categorize changes by color transition
        transitions = Counter()
        for r in range(64):
            for c in range(64):
                if diff_mask[r, c]:
                    old = int(l2_init[r, c])
                    new = int(frame[r, c])
                    transitions[(old, new)] += 1

        print(f"\n=== Click ({cx},{cy}): {n_changed} cells changed ===")
        print(f"  lc={obs.levels_completed} state={obs.state.name}")
        for (old, new), cnt in transitions.most_common(10):
            print(f"  {old:2d} → {new:2d}: {cnt} cells")

    # Deep analysis: what does the COLUMN 0 counter look like?
    print("\n=== Column 0 analysis (turn counter) ===")
    env.reset()
    env.reset()
    for px, py in L1:
        obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
    init_col0 = np.array(obs.frame[-1], dtype=np.int64)[:, 0].copy()
    print(f"  L2 initial col 0: unique values = {sorted(set(int(v) for v in init_col0))}")
    non_default = [(r, int(init_col0[r])) for r in range(64) if init_col0[r] != 0]
    print(f"  Non-zero cells in col 0: {non_default[:20]}")

    for i, (cx, cy) in enumerate([(10, 10), (20, 20), (45, 35)]):
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        frame = np.array(obs.frame[-1], dtype=np.int64)
        col0 = frame[:, 0]
        changed = [(r, int(init_col0[r]), int(col0[r]))
                   for r in range(64) if col0[r] != init_col0[r]]
        print(f"  After click {i+1} ({cx},{cy}): col 0 changes = {changed[:10]}")

    # Check: what's the arm1 head position? (color 0 sprite with center)
    print("\n=== Head sprite analysis ===")
    env.reset()
    env.reset()
    for px, py in L1:
        obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
    frame = np.array(obs.frame[-1], dtype=np.int64)

    # Find color 0 cells (the head outline)
    zeros = np.argwhere(frame == 0)
    print(f"  Color 0 cells: {len(zeros)}")
    if len(zeros) > 0:
        # Cluster them
        from scipy.ndimage import label
        mask0 = (frame == 0)
        labeled, n_clusters = label(mask0)
        for cl in range(1, n_clusters + 1):
            cells = np.argwhere(labeled == cl)
            center = cells.mean(axis=0)
            print(f"  Cluster {cl}: {len(cells)} cells, "
                  f"center ({center[1]:.0f}, {center[0]:.0f}), "
                  f"bounds rows [{cells[:,0].min()}-{cells[:,0].max()}] "
                  f"cols [{cells[:,1].min()}-{cells[:,1].max()}]")

    # Find color 12 cells (the c-diamond and arm1 foot ring)
    print("\n=== Color 12 (c) cell positions ===")
    c12 = np.argwhere(frame == 12)
    print(f"  {len(c12)} cells of color 12")
    if len(c12) > 0:
        mask12 = (frame == 12)
        labeled12, n12 = label(mask12)
        for cl in range(1, n12 + 1):
            cells = np.argwhere(labeled12 == cl)
            center = cells.mean(axis=0)
            print(f"  Cluster {cl}: {len(cells)} cells, "
                  f"center ({center[1]:.0f}, {center[0]:.0f})")


if __name__ == "__main__":
    main()
