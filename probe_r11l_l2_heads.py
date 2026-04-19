"""R11L L2: find the head sprites, test the click mechanic per arm.

L2 has 2 foot-6-centers: (24, 12) and (49, 41). If L2 is a 2-arm puzzle each
arm has its own head. Find them. Then diff click effects to see which head/
foot the click affects.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def foot_positions(g):
    """Return list of 6-cell positions (arm count = len(list))."""
    sixes = np.argwhere(g == 6)
    return [(int(x), int(y)) for y, x in sixes]


def find_head_candidates(g):
    """Look for f-center or c-center surrounded by 0-outline (head pattern)."""
    # f=15, c=12
    out = []
    for color in (15, 12):
        ys, xs = np.where(g == color)
        for y, x in zip(ys, xs):
            if y < 1 or y > 62 or x < 1 or x > 62:
                continue
            nb = [int(g[y - 1, x]), int(g[y + 1, x]),
                  int(g[y, x - 1]), int(g[y, x + 1])]
            if nb.count(0) >= 3:
                out.append((int(x), int(y), color))
    return out


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    # Advance to L2
    env.reset()
    for cx, cy in [(36, 13), (26, 61), (42, 30)]:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    g0 = frame(obs)

    feet = foot_positions(g0)
    print(f"L2 feet: {feet}")
    heads = find_head_candidates(g0)
    print(f"L2 head candidates: {heads}")

    # Try a click and see which foot/head moves
    print("\n-- click tests --")
    for (cx, cy) in [(30, 30), (10, 10), (40, 40), (50, 30), (20, 50)]:
        env.reset()
        for px, py in [(36, 13), (26, 61), (42, 30)]:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(obs2)
        new_feet = foot_positions(g)
        new_heads = find_head_candidates(g)
        feet_changed = [nf for nf in new_feet if nf not in feet]
        feet_unchanged = [f for f in feet if f in new_feet]
        heads_changed = [h for h in new_heads if h not in heads]
        heads_unchanged = [h for h in heads if h in new_heads]
        print(f"  click({cx},{cy}):")
        print(f"    feet changed: {feet_changed}  unchanged: {feet_unchanged}")
        print(f"    heads changed: {heads_changed}  unchanged: {heads_unchanged}")
        print(f"    lc={obs2.levels_completed}")


if __name__ == "__main__":
    main()
