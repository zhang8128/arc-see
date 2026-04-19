"""R11L: precise mapping click → (foot_x, foot_y), and search for (27, 59).

Goal: find a click that lands the foot exactly on the diamond f-center (27, 59).
Also derive the linear click→foot formula by fitting both axes.
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


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    obs0 = env.reset()
    g0 = frame(obs0)
    f0 = foot_pos(g0)
    print(f"initial foot: {f0}")

    # Scan every single pixel click position and record foot position if it moved
    # Too slow at 64x64 = 4096? Each is one env.reset + one step. ~10ms each = 40s.
    # Use STEP=1 for a full map.
    reach: dict[tuple[int, int], tuple[int, int]] = {}
    wins = []
    for cy in range(0, 64):
        for cx in range(0, 64):
            env.reset()
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            if obs2.state.name == "WIN":
                wins.append((cx, cy))
            fp = foot_pos(frame(obs2))
            if fp is not None and fp != f0:
                reach[(cx, cy)] = fp

    print(f"clicks that moved foot: {len(reach)} / 4096")
    print(f"WINs: {wins}")

    # Distinct foot landings
    targets = set(reach.values())
    print(f"distinct foot landings: {len(targets)}")

    if not reach:
        print("No clicks moved the foot — nothing to analyse.")
        return

    # Find click(s) that land foot at exactly (27, 59) — the diamond center
    goal = (27, 59)
    hits = [click for click, fp in reach.items() if fp == goal]
    print(f"\nclicks that land foot at goal (27, 59): {hits[:20]}")

    # If no direct hit, report nearest
    if not hits:
        nearest_fp = min(
            targets, key=lambda p: abs(p[0] - goal[0]) + abs(p[1] - goal[1])
        )
        d = abs(nearest_fp[0] - goal[0]) + abs(nearest_fp[1] - goal[1])
        clicks_for_nearest = [c for c, fp in reach.items() if fp == nearest_fp]
        print(f"nearest foot: {nearest_fp}  L1-dist={d}")
        print(f"clicks: {clicks_for_nearest[:5]}")

    # Fit linear mapping click → foot to see the rule
    clicks_arr = np.array(list(reach.keys()), dtype=np.float64)
    foots_arr = np.array(list(reach.values()), dtype=np.float64)
    # Augment with bias column
    A = np.hstack([clicks_arr, np.ones((len(clicks_arr), 1))])
    # Solve A @ [ax, bx, cx] = foot_x ; same for y
    sol_x, *_ = np.linalg.lstsq(A, foots_arr[:, 0], rcond=None)
    sol_y, *_ = np.linalg.lstsq(A, foots_arr[:, 1], rcond=None)
    print(f"\nLinear fit:")
    print(f"  foot_x ≈ {sol_x[0]:+.3f} * click_x {sol_x[1]:+.3f} * click_y {sol_x[2]:+.3f}")
    print(f"  foot_y ≈ {sol_y[0]:+.3f} * click_x {sol_y[1]:+.3f} * click_y {sol_y[2]:+.3f}")
    # Residuals
    pred_x = A @ sol_x
    pred_y = A @ sol_y
    max_res_x = float(np.max(np.abs(pred_x - foots_arr[:, 0])))
    max_res_y = float(np.max(np.abs(pred_y - foots_arr[:, 1])))
    print(f"  max residual x: {max_res_x:.3f}  y: {max_res_y:.3f}")


if __name__ == "__main__":
    main()
