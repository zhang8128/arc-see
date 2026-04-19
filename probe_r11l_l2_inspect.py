"""R11L L2: dump the frame after a single click to see exactly what moves.

Previous probes' head detection returned weird clamped values. Just print the
diff and the frame visually. Focus on: what colors are where in the initial
vs post-click state.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def dump(g, title=""):
    print(f"--- {title} ---")
    chars = "0123456789abcdef"
    H, W = g.shape
    for y in range(H):
        row = []
        for x in range(W):
            v = int(g[y, x])
            row.append("." if v < 0 else (chars[v] if 0 <= v < 16 else "?"))
        print("".join(row))
    print()


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    g0 = frame(obs)
    dump(g0, "L2 initial")

    # Click (48, 40): under L1 formula this would put head at (49, 41)
    env.reset()
    for cx, cy in L1:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    obs2 = env.step(GameAction.ACTION6, data={"x": 48, "y": 40})
    g1 = frame(obs2)
    dump(g1, "after click(48, 40)")

    # Diff, ignoring col 0 counter
    diffs = np.argwhere((g0 != g1) & (np.arange(g0.shape[1])[None, :] != 0))
    print(f"\ndiff cells (not col 0): {len(diffs)}")
    # Group by old->new value
    from collections import Counter
    changes = Counter()
    for y, x in diffs:
        changes[(int(g0[y, x]), int(g1[y, x]))] += 1
    print(f"value transitions: {dict(changes.most_common())}")


if __name__ == "__main__":
    main()
