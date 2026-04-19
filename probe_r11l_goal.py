"""R11L: test the 'land foot on 3-diamond' hypothesis via the public arc_agi API.

Initial player head ~ (6, 36), foot center ~ (17, 47). Foot offset = (+11, +11).
Goal candidate: 3-diamond with f center at ~(29, 60).
To land foot at (29, 60), click head at (18, 49).
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def print_grid(g, tag):
    print(f"--- {tag} ---")
    chars = "0123456789abcdef"
    for y in range(64):
        row = []
        for x in range(64):
            v = int(g[y, x])
            row.append("." if v < 0 else (chars[v] if v < 16 else "?"))
        print("".join(row))
    print()


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    obs = env.reset()
    g0 = frame(obs)

    # Confirm the 3-diamond at ~(29, 60) by finding 3s and lower f-cells.
    threes = np.argwhere(g0 == 3)
    print(f"cells with value 3: {len(threes)}  (sample: {threes[:10].tolist()})")
    fs = np.argwhere(g0 == 15)
    fs_lower = [tuple(p.tolist()) for p in fs if p[0] > 30]
    print(f"f-cells with y>30 (lower half): {fs_lower}")

    # Try targeting the 3-diamond center via a few click positions.
    for click_xy in [
        (18, 49),  # head click so foot (+11,+11) lands at (29, 60)
        (29, 60),  # direct click on diamond center
        (17, 47),  # foot center — baseline, not expected to progress
    ]:
        env.reset()
        obs2 = env.step(GameAction.ACTION6, data={"x": click_xy[0], "y": click_xy[1]})
        g = frame(obs2)
        state = obs2.state
        changed = int(np.sum(g0 != g))
        still_has_3 = bool(np.any(g == 3))
        still_has_6 = bool(np.any(g == 6))
        new_fs = np.argwhere(g == 15)
        new_fs_lower = [tuple(p.tolist()) for p in new_fs if p[0] > 30]
        print(f"\nclick{click_xy}: {changed} cells changed  state={state}")
        print(f"  still has 3s: {still_has_3}  still has 6: {still_has_6}")
        print(f"  f-cells y>30 after: {new_fs_lower}")

    # Dump the frame after click(18,49) so we can see where player ended up
    env.reset()
    obs2 = env.step(GameAction.ACTION6, data={"x": 18, "y": 49})
    print_grid(frame(obs2), "after click(18,49)")


if __name__ == "__main__":
    main()
