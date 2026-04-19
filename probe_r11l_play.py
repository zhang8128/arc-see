"""R11L: play via arc_agi public API. No engine attribute spelunking.

Goal: reset L1, print the frame, try each action once, print after each.
Dump ONLY what would be visible through the lenses (the 64x64 frame).
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def print_grid(grid, title=""):
    print(f"--- {title} ---")
    H, W = grid.shape
    # Compact color mapping. Use hex chars so each cell is one column.
    chars = "0123456789abcdef"
    for y in range(H):
        row = []
        for x in range(W):
            v = int(grid[y, x])
            if v < 0:
                row.append(".")
            elif v < 16:
                row.append(chars[v])
            else:
                row.append("?")
        print("".join(row))
    print()


def frame_of(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def unique_colors(grid):
    vals, counts = np.unique(grid, return_counts=True)
    return list(zip(vals.tolist(), counts.tolist()))


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)
    assert env is not None, "env is None"

    obs = env.reset()
    grid = frame_of(obs)
    print(f"Initial frame shape: {grid.shape}")
    print(f"Unique colors (value, count): {unique_colors(grid)}")
    print_grid(grid, "L1 initial")

    # Try each action once. Actions 1-7. Click (action 6) requires x,y.
    # Per the handoff, R11L's discrete actions (1-5, 7) don't do anything;
    # only click (6) has effect. Confirm that.
    for aid in [1, 2, 3, 4, 5, 7]:
        obs = env.reset()
        action = getattr(GameAction, f"ACTION{aid}")
        obs2 = env.step(action)
        g2 = frame_of(obs2)
        changed = int(np.sum(g2 != grid))
        print(f"ACTION{aid}: {changed} cells changed, state={obs2.state}")

    # Try click at a few points, see what moves
    print("\n-- clicks --")
    for (cx, cy) in [(10, 10), (30, 30), (50, 50), (6, 36), (17, 47), (29, 60)]:
        obs = env.reset()
        before = frame_of(obs)
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        after = frame_of(obs2)
        changed = int(np.sum(before != after))
        print(f"click({cx},{cy}): {changed} cells changed, state={obs2.state}")


if __name__ == "__main__":
    main()
