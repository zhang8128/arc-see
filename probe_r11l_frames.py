"""R11L: inspect multi-frame observations and full-board state change.

(1) Does obs.frame have multiple entries? What's different between frames?
(2) After a click, what cells in the 64x64 grid change that are NOT:
    - head sprite (within 4px of head)
    - foot sprite (within 4px of foot)
    - arm-line cells (color 1)
    - col 0 turn counter
(3) Are any FLOOR cells (color 5) or other cells in the mid-level permanently
    modified by arm passage?
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def all_frames(obs):
    """Return list of (h, w) grids from obs.frame."""
    return [np.array(f, dtype=np.int64) for f in obs.frame]


def frame_last(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def foot_pos(grid):
    sixes = np.argwhere(grid == 6)
    if len(sixes) != 1:
        return None
    y, x = sixes[0]
    return (int(x), int(y))


def head_pos(grid):
    ys, xs = np.where(grid == 15)
    for y, x in zip(ys, xs):
        if y < 1 or y > 62 or x < 1 or x > 62:
            continue
        nb = [int(grid[y - 1, x]), int(grid[y + 1, x]),
              int(grid[y, x - 1]), int(grid[y, x + 1])]
        if nb.count(0) >= 3:
            return (int(x), int(y))
    return None


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    # -- Multi-frame observation --
    obs = env.reset()
    frames = all_frames(obs)
    print(f"obs.frame has {len(frames)} entries")
    for i, f in enumerate(frames):
        print(f"  frame[{i}]: shape={f.shape}  unique={sorted(set(f.flatten().tolist()))}")
        # Is this frame different from frame[-1]?
        if i < len(frames) - 1:
            diff = int(np.sum(f != frames[-1]))
            print(f"    differs from frame[-1] in {diff} cells")

    obs2 = env.step(GameAction.ACTION6, data={"x": 40, "y": 40})
    frames2 = all_frames(obs2)
    print(f"\nafter click, obs.frame has {len(frames2)} entries")
    for i, f in enumerate(frames2):
        print(f"  frame[{i}]: shape={f.shape}  unique={sorted(set(f.flatten().tolist()))}")

    # -- Full board change scan --
    # From fresh state, click 5 different "interesting" positions and look for
    # cells that are far from both head and foot and not col 0 and not color 1.
    print("\n-- full board change scan --")
    env.reset()
    g0 = frame_last(env.reset())
    for i, (cx, cy) in enumerate([(40, 40), (20, 20), (50, 30), (25, 55), (15, 25)]):
        env.reset()
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame_last(obs2)
        h = head_pos(g)
        f = foot_pos(g)
        diffs = np.argwhere(g != g0)
        far_changes = []
        for y, x in diffs:
            y, x = int(y), int(x)
            if x == 0:  # turn counter
                continue
            if h is not None and abs(x - h[0]) <= 4 and abs(y - h[1]) <= 4:
                continue
            if f is not None and abs(x - f[0]) <= 4 and abs(y - f[1]) <= 4:
                continue
            # Also skip old head/foot footprint
            old_h, old_f = head_pos(g0), foot_pos(g0)
            if old_h is not None and abs(x - old_h[0]) <= 4 and abs(y - old_h[1]) <= 4:
                continue
            if old_f is not None and abs(x - old_f[0]) <= 4 and abs(y - old_f[1]) <= 4:
                continue
            # Skip arm-1 cells (both old and new)
            if g0[y, x] == 1 or g[y, x] == 1:
                continue
            far_changes.append((y, x, int(g0[y, x]), int(g[y, x])))
        print(f"  click({cx},{cy}): head={h}  foot={f}")
        print(f"    far changes ({len(far_changes)}): {far_changes[:15]}")

    # -- After many clicks, does the floor paint? --
    # Click 7 times at different positions and check if any floor cells changed
    # permanently (still different from initial after arm has moved away).
    print("\n-- 6-click sweep + final check for floor paint --")
    env.reset()
    g_init = frame_last(env.reset())
    sweep = [(10, 20), (50, 20), (50, 50), (10, 50), (30, 15), (30, 45)]
    env.reset()
    for cx, cy in sweep:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    # Now move arm far away from any specific cell and check what's left painted
    env.reset()
    for cx, cy in sweep:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    obs2 = env.step(GameAction.ACTION6, data={"x": 32, "y": 32})
    g_after = frame_last(obs2)
    # Compare to initial, excluding dynamic player elements and col 0
    h = head_pos(g_after)
    f = foot_pos(g_after)
    mask_ignore = np.zeros_like(g_init, dtype=bool)
    mask_ignore[:, 0] = True  # col 0
    if h:
        mask_ignore[max(0, h[1] - 6):h[1] + 7, max(0, h[0] - 6):h[0] + 7] = True
    if f:
        mask_ignore[max(0, f[1] - 6):f[1] + 7, max(0, f[0] - 6):f[0] + 7] = True
    # Also ignore arm-line cells in both frames
    mask_ignore |= (g_init == 1) | (g_after == 1)
    # And initial head/foot area
    old_h, old_f = head_pos(g_init), foot_pos(g_init)
    if old_h:
        mask_ignore[max(0, old_h[1] - 6):old_h[1] + 7, max(0, old_h[0] - 6):old_h[0] + 7] = True
    if old_f:
        mask_ignore[max(0, old_f[1] - 6):old_f[1] + 7, max(0, old_f[0] - 6):old_f[0] + 7] = True

    diff_cells = np.argwhere((g_init != g_after) & ~mask_ignore)
    print(f"  persistent non-player changes after 7-click sweep: {len(diff_cells)}")
    for y, x in diff_cells[:30]:
        print(f"    ({int(x)},{int(y)}): {int(g_init[y, x])} -> {int(g_after[y, x])}")

    print(f"  state after 7 clicks: {obs2.state.name}")
    print(f"  turn counter col (first 10 rows): {[int(g_after[i, 0]) for i in range(10)]}")


if __name__ == "__main__":
    main()
