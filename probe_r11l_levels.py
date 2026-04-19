"""R11L: (1) test order-independence of the L1 diamond-visit solution,
(2) play through L2..L6 with a discovery loop — find the goal diamonds by
sweeping first-click positions and testing the same 3-click pattern.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    # Part 1: order independence of L1
    targets = [(36, 13), (26, 61), (42, 30)]
    print("-- L1 order independence --")
    import itertools
    for perm in itertools.permutations(targets):
        env.reset()
        last_lc = 0
        for i, (cx, cy) in enumerate(perm):
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            last_lc = obs2.levels_completed
        print(f"  {perm}: levels_completed={last_lc}")

    # Part 2: play L1 → advance → examine L2's frame
    print("\n-- advance to L2 --")
    env.reset()
    env.step(GameAction.ACTION6, data={"x": 36, "y": 13})
    env.step(GameAction.ACTION6, data={"x": 26, "y": 61})
    obs_l2 = env.step(GameAction.ACTION6, data={"x": 42, "y": 30})
    print(f"after L1 win: levels_completed={obs_l2.levels_completed}  state={obs_l2.state.name}")
    print(f"frame shape: {np.array(obs_l2.frame[-1]).shape}")
    # Dump L2 frame
    g_l2 = frame(obs_l2)
    vals = sorted(set(g_l2.flatten().tolist()))
    print(f"L2 unique values: {vals}")
    # Count color 3 cells (hip candidates) and their positions
    threes = np.argwhere(g_l2 == 3)
    print(f"L2 hip (color 3) cells: {len(threes)}")
    if len(threes) > 0:
        ys_3 = threes[:, 0]
        xs_3 = threes[:, 1]
        print(f"  center: ({int(xs_3.mean())}, {int(ys_3.mean())})")

    # Print L2 frame
    chars = "0123456789abcdef"
    print("\n--- L2 frame ---")
    for y in range(g_l2.shape[0]):
        row = "".join("." if g_l2[y, x] < 0 else chars[int(g_l2[y, x])] for x in range(g_l2.shape[1]))
        print(row)


if __name__ == "__main__":
    main()
