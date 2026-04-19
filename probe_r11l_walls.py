"""R11L: (1) dump frame after one click to eyeball model, (2) map walls via
rejection set, (3) try a few multi-click sequences to see if score/state changes
in non-obvious ways.
"""
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


def dump_grid(g, title=""):
    print(f"--- {title} ---")
    chars = "0123456789abcdef"
    for y in range(64):
        print("".join("." if g[y, x] < 0 else chars[int(g[y, x])] for x in range(64)))
    print()


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)
    g0 = frame(env.reset())
    print(f"initial: head={head_pos(g0)}  foot={foot_pos(g0)}")

    # Dump the frame after click (40, 40). Under the model:
    # head should go to ~(40, 40), foot to midpoint((26,58),(40,40))=(33, 49).
    env.reset()
    obs2 = env.step(GameAction.ACTION6, data={"x": 40, "y": 40})
    g = frame(obs2)
    print(f"after click(40, 40): head={head_pos(g)}  foot={foot_pos(g)}")
    dump_grid(g, "click(40, 40)")

    # Rejection map. Track which clicks leave both head AND foot unchanged.
    env.reset()
    g0 = frame(env.reset())
    h0 = head_pos(g0)
    f0 = foot_pos(g0)
    rejected = []
    reject_set: set[tuple[int, int]] = set()
    for cy in range(64):
        for cx in range(64):
            env.reset()
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            g = frame(obs2)
            h = head_pos(g)
            f = foot_pos(g)
            if (h == h0 or h is None) and (f == f0 or f is None):
                rejected.append((cx, cy))
                reject_set.add((cx, cy))
    print(f"\nrejected clicks: {len(rejected)}")

    # Print the 64x64 rejection map: '#' rejected, '.' accepted
    print("Rejection map (# = rejected, . = accepted):")
    for cy in range(64):
        row = "".join("#" if (cx, cy) in reject_set else "." for cx in range(64))
        print(f"  {cy:2d}: {row}")

    # Multi-click sequence test: click each corner, and see if anything nontrivial
    # progresses (score in any cell besides 0,0, win state, level change).
    print("\n-- multi-click sequence: 4 corner clicks --")
    env.reset()
    g_prev = frame(env.reset())
    for i, (cx, cy) in enumerate([(5, 5), (58, 5), (5, 58), (58, 58), (32, 32)]):
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(obs2)
        # Find any cells that changed besides the expected head/foot regions
        diff = np.argwhere(g != g_prev)
        print(f"  click{i} ({cx},{cy}): {len(diff)} cells changed  state={obs2.state.name}")
        print(f"    head={head_pos(g)}  foot={foot_pos(g)}  (0,0)={int(g[0,0])}")
        # What non-0,0 cells that don't belong to the head/foot neighbourhoods changed?
        h = head_pos(g)
        f = foot_pos(g)
        interesting = []
        for y, x in diff:
            if (y, x) == (0, 0):
                continue
            # Skip cells near head or foot (10x10 window)
            near_h = h and abs(x - h[0]) < 8 and abs(y - h[1]) < 8
            near_f = f and abs(x - f[0]) < 8 and abs(y - f[1]) < 8
            if not (near_h or near_f):
                interesting.append((int(y), int(x), int(g_prev[y, x]), int(g[y, x])))
        if interesting:
            print(f"    interesting (not near head/foot): {interesting[:10]}")
        g_prev = g


if __name__ == "__main__":
    main()
