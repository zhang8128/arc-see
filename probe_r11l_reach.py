"""R11L: one-click foot reachability map.

From the fresh L1 state, click at every (x, y) on a grid and record where the
foot marker (color 6) ends up. This shows:
  - Which click positions are rejected (foot doesn't move).
  - The reachable foot positions in ONE click.
  - Whether (27, 60) — the 3-diamond center — is reachable in one click.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def foot_pos(grid):
    """Return (x, y) of the lone cell with value 6, or None."""
    sixes = np.argwhere(grid == 6)
    if len(sixes) == 0:
        return None
    if len(sixes) > 1:
        return ("MULTI", [tuple(p.tolist()) for p in sixes])
    y, x = sixes[0]
    return (int(x), int(y))


def head_pos(grid):
    """Head f-center: the (x, y) of the 'f' surrounded by '0's (000 / 0f0 / 000).

    Quick hack: find f cells that have 0 neighbors on at least 3 of 4 sides.
    """
    ys, xs = np.where(grid == 15)
    for y, x in zip(ys, xs):
        if y < 1 or y > 62 or x < 1 or x > 62:
            continue
        neighbors = [grid[y - 1, x], grid[y + 1, x], grid[y, x - 1], grid[y, x + 1]]
        if neighbors.count(0) >= 3:
            return (int(x), int(y))
    return None


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    obs = env.reset()
    g0 = frame(obs)
    print(f"initial foot: {foot_pos(g0)}")
    print(f"initial head: {head_pos(g0)}")

    # Goal candidate
    print(f"3-diamond center (hypothesis): (27, 60)")

    # Scan clicks on a coarse grid. For each, record (foot_x, foot_y) or NOOP.
    STEP = 4
    reach: dict[tuple[int, int], tuple[int, int]] = {}
    wins: list[tuple[int, int]] = []
    noop_count = 0
    for cy in range(0, 64, STEP):
        for cx in range(0, 64, STEP):
            env.reset()
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            g = frame(obs2)
            if obs2.state.name == "WIN":
                wins.append((cx, cy))
            fp = foot_pos(g)
            if fp is None or isinstance(fp[0], str):
                continue
            if fp == foot_pos(g0):
                noop_count += 1
                continue
            reach[(cx, cy)] = fp

    print(f"\nclicks tried: {(64//STEP)**2}  moved: {len(reach)}  no-op: {noop_count}")
    print(f"WINs: {wins}")

    # Show the reachable foot positions
    foot_targets = set(reach.values())
    print(f"\ndistinct foot positions reachable in 1 click: {len(foot_targets)}")
    if foot_targets:
        fxs = [p[0] for p in foot_targets]
        fys = [p[1] for p in foot_targets]
        print(f"  x range: {min(fxs)}..{max(fxs)}  y range: {min(fys)}..{max(fys)}")

    # Can we reach the goal (27, 60) directly?
    goal = (27, 60)
    direct = [click for click, fp in reach.items() if fp == goal]
    if direct:
        print(f"\n*** DIRECT: click{direct} lands foot on goal ***")
    else:
        # Nearest foot position to goal
        if foot_targets:
            nearest = min(
                foot_targets,
                key=lambda p: (p[0] - goal[0]) ** 2 + (p[1] - goal[1]) ** 2,
            )
            dist2 = (nearest[0] - goal[0]) ** 2 + (nearest[1] - goal[1]) ** 2
            print(f"\nnearest reachable foot: {nearest}  (dist^2={dist2})")
            clicks_for_nearest = [c for c, fp in reach.items() if fp == nearest]
            print(f"  achievable via clicks: {clicks_for_nearest[:5]}")

    # Simple visualisation: print a 16x16 grid (each cell = 4x4 block) where
    # the character is the last-digit of the foot y coordinate, or '.' for no-op.
    print("\nClick grid → foot y last digit (or '.' for noop):")
    for cy in range(0, 64, STEP):
        row = ""
        for cx in range(0, 64, STEP):
            fp = reach.get((cx, cy))
            if fp is None:
                row += "."
            else:
                row += str(fp[1] % 10)
        print(f"  y={cy:2d}: {row}")


if __name__ == "__main__":
    main()
