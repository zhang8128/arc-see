"""R11L: fit separate formulas for head and foot, independently.

For every click where head (resp foot) moved, fit click → new head position
(resp new foot position). Check the two formulas are distinct, and whether
they reveal a kinematic tie between the two legs.
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


def fit(pairs, label):
    """pairs: list of ((cx, cy), (tx, ty)). Print linear fit of click → target."""
    if not pairs:
        print(f"{label}: no data")
        return None
    X = np.array([c for c, _ in pairs], dtype=np.float64)
    Y = np.array([t for _, t in pairs], dtype=np.float64)
    A = np.hstack([X, np.ones((len(X), 1))])
    sol_x, *_ = np.linalg.lstsq(A, Y[:, 0], rcond=None)
    sol_y, *_ = np.linalg.lstsq(A, Y[:, 1], rcond=None)
    pred_x = A @ sol_x
    pred_y = A @ sol_y
    max_rx = float(np.max(np.abs(pred_x - Y[:, 0])))
    max_ry = float(np.max(np.abs(pred_y - Y[:, 1])))
    print(f"{label}:")
    print(f"  t_x ≈ {sol_x[0]:+.3f}*cx {sol_x[1]:+.3f}*cy {sol_x[2]:+.3f}   max_res {max_rx:.3f}")
    print(f"  t_y ≈ {sol_y[0]:+.3f}*cx {sol_y[1]:+.3f}*cy {sol_y[2]:+.3f}   max_res {max_ry:.3f}")
    return sol_x, sol_y


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    g0 = frame(env.reset())
    h0 = head_pos(g0)
    f0 = foot_pos(g0)
    print(f"initial: head={h0}  foot={f0}")

    head_pairs = []  # (click, new_head) where head moved
    foot_pairs = []  # (click, new_foot) where foot moved
    rejected: list[tuple[int, int]] = []
    for cy in range(64):
        for cx in range(64):
            env.reset()
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            g = frame(obs2)
            h = head_pos(g)
            f = foot_pos(g)
            if h is not None and h != h0:
                head_pairs.append(((cx, cy), h))
            if f is not None and f != f0:
                foot_pairs.append(((cx, cy), f))
            if (h == h0 or h is None) and (f == f0 or f is None):
                rejected.append((cx, cy))

    print(f"head moved: {len(head_pairs)}  foot moved: {len(foot_pairs)}  rejected: {len(rejected)}")

    fit(head_pairs, "head formula")
    fit(foot_pairs, "foot formula")

    # For a sample of "both move" clicks, print both positions
    print("\n-- 10 sample both-move clicks --")
    shown = 0
    head_set = {c for c, _ in head_pairs}
    foot_set = {c for c, _ in foot_pairs}
    both_clicks = sorted(head_set & foot_set)
    for cx, cy in both_clicks[::350][:10]:
        env.reset()
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(obs2)
        print(f"  click({cx:2d},{cy:2d}): head={head_pos(g)}  foot={foot_pos(g)}")
        shown += 1

    # Distance invariants:
    # For each both-move click, compute dist(head, hip), dist(foot, hip),
    # dist(head, foot). Is anything constant?
    print("\n-- invariants across all clicks that moved anything --")
    hip = (26, 58)
    d_hh_list, d_hf_list, d_ff_list, d_hhf_list = [], [], [], []
    for cx, cy in both_clicks:
        env.reset()
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(obs2)
        h = head_pos(g)
        f = foot_pos(g)
        if h is None or f is None:
            continue
        d_hh = ((h[0] - hip[0]) ** 2 + (h[1] - hip[1]) ** 2) ** 0.5
        d_ff = ((f[0] - hip[0]) ** 2 + (f[1] - hip[1]) ** 2) ** 0.5
        d_hf = ((h[0] - f[0]) ** 2 + (h[1] - f[1]) ** 2) ** 0.5
        d_hh_list.append(d_hh)
        d_ff_list.append(d_ff)
        d_hf_list.append(d_hf)
        d_hhf_list.append(d_hh + d_ff)
    if d_hh_list:
        print(f"  dist(head, hip):  min={min(d_hh_list):.2f} max={max(d_hh_list):.2f}")
        print(f"  dist(foot, hip):  min={min(d_ff_list):.2f} max={max(d_ff_list):.2f}")
        print(f"  dist(head, foot): min={min(d_hf_list):.2f} max={max(d_hf_list):.2f}")
        print(f"  dist(h,hip)+dist(f,hip): min={min(d_hhf_list):.2f} max={max(d_hhf_list):.2f}")


if __name__ == "__main__":
    main()
