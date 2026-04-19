"""R11L L2: carefully inspect L2 initial state and post-arm-2-placement
state using FRESH RESET.

Look for:
- all sprite shapes (crosses, diamonds, rings)
- any cells I haven't accounted for
- differences in '1' cell clusters (arm bodies)
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def dump_grid_range(g, title, y0=0, y1=64, x0=0, x1=64):
    print(f"--- {title} ---")
    chars = "0123456789abcdef"
    for y in range(y0, y1):
        row = []
        for x in range(x0, x1):
            v = int(g[y, x])
            row.append("." if v < 0 else (chars[v] if 0 <= v < 16 else "?"))
        print(f"  y={y:2d}: " + "".join(row))
    print()


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)
    L1 = [(36, 13), (26, 61), (42, 30)]

    def play(seq):
        env.reset()
        obs = None
        for px, py in L1:
            obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
        for cx, cy in seq:
            obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        return obs

    # L2 initial (from just after L1 win)
    env.reset()
    obs = None
    for px, py in L1:
        obs = env.step(GameAction.ACTION6, data={"x": px, "y": py})
    g_init = np.array(obs.frame[-1], dtype=np.int64)

    # After (A, arm2_hip, B) placing arm 2 foot at (40, 51)
    obs2 = play([(10, 10), (45, 35), (26, 54)])
    g_placed = np.array(obs2.frame[-1], dtype=np.int64)

    print(f"L2 init arm2 foot (should be (49, 41)):")
    sixes_init = sorted([(int(x), int(y)) for y, x in np.argwhere(g_init == 6)])
    print(f"  {sixes_init}")
    sixes_placed = sorted([(int(x), int(y)) for y, x in np.argwhere(g_placed == 6)])
    print(f"after placement:")
    print(f"  {sixes_placed}")

    # Dump the area around (40, 51) in both frames
    dump_grid_range(g_init, "L2 init — area (35..55, 40..60)", 40, 60, 35, 55)
    dump_grid_range(g_placed, "after placement — area (35..55, 40..60)", 40, 60, 35, 55)

    # Diff only the non-player areas
    print("\n-- diff cells outside arm 1 foot and arm 2 foot areas --")
    # Approximate player regions
    diffs = []
    for y in range(64):
        for x in range(64):
            if g_init[y, x] != g_placed[y, x]:
                # Skip col 0 (counter)
                if x == 0:
                    continue
                # Skip areas near arm 1 foot
                if 19 <= x <= 32 and 10 <= y <= 16:
                    continue
                # Skip area near arm 2 foot (both positions)
                if 44 <= x <= 54 and 36 <= y <= 46:
                    continue
                if 35 <= x <= 45 and 46 <= y <= 56:
                    continue
                diffs.append((y, x, int(g_init[y, x]), int(g_placed[y, x])))
    print(f"distant diffs: {len(diffs)}")
    for d in diffs[:30]:
        print(f"  {d}")


if __name__ == "__main__":
    main()
