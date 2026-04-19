"""R11L: characterize the turn counter precisely.

Goal: find what makes counter skip (cost 2 marks vs 1), and see if that hidden
rule hints at a win condition.

Test strategy:
  1. Click at systematically varying (head_delta) positions from a known start.
  2. Record counter value after EACH click (full col 0).
  3. Find what click properties correlate with counter skip.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def col0(g):
    h = g.shape[0]
    return [int(g[i, 0]) for i in range(h)]


def count_marks(g):
    return sum(1 for v in col0(g) if v == 5)


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

    # Replay the exact sequence that showed the skip: (15, 20), (18, 25),
    # (21, 30), (24, 35), (27, 40), (30, 45), (33, 50), (36, 20), ...
    seq = [(15, 20), (18, 25), (21, 30), (24, 35), (27, 40),
           (30, 45), (33, 50), (36, 20), (39, 25), (42, 30)]
    env.reset()
    g0 = frame(env.reset())
    prev_head = head_pos(g0)
    prev_foot = foot_pos(g0)
    prev_count = 0
    prev_col0 = col0(g0)
    env.reset()
    print(f"Start: head={prev_head}  foot={prev_foot}  counter={prev_count}")
    print(f"Initial col0 (first 10): {prev_col0[:10]}")

    for i, (cx, cy) in enumerate(seq):
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(obs2)
        h = head_pos(g)
        f = foot_pos(g)
        cnt = count_marks(g)
        c0 = col0(g)
        delta_cnt = cnt - prev_count
        # Identify which rows in col0 are newly 5
        new_marks = [r for r in range(len(c0)) if c0[r] == 5 and prev_col0[r] != 5]
        removed_marks = [r for r in range(len(c0)) if c0[r] != 5 and prev_col0[r] == 5]
        head_delta = (
            None if h is None or prev_head is None
            else (h[0] - prev_head[0], h[1] - prev_head[1])
        )
        foot_delta = (
            None if f is None or prev_foot is None
            else (f[0] - prev_foot[0], f[1] - prev_foot[1])
        )
        print(f"click{i:2d} ({cx:2d},{cy:2d}): h={h} f={f} cnt={cnt}(Δ{delta_cnt:+d})")
        print(f"  head_delta={head_delta}  foot_delta={foot_delta}")
        print(f"  new col0 marks at rows: {new_marks}  removed: {removed_marks}")
        prev_head, prev_foot, prev_count, prev_col0 = h, f, cnt, c0

    # Also: dump the entire col 0 after all these clicks
    print(f"\nfinal col0: {prev_col0}")


if __name__ == "__main__":
    main()
