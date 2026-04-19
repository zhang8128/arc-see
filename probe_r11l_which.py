"""R11L: which leg (head or foot) moves on each click?

Scan all clicks, track BOTH head and foot positions before and after, and
categorize each click: head_move, foot_move, both_move, neither_move.

Also search for a click (possibly after 1-7 clicks) that triggers WIN.
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
    """f center with 3+ 0-neighbors among {N,S,E,W}."""
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

    g0 = frame(env.reset())
    h0 = head_pos(g0)
    f0 = foot_pos(g0)
    print(f"initial: head={h0}  foot={f0}")
    print(f"hip (pivot) = (26, 58)  [derived from linear fit]")

    # Scan all 4096 clicks
    categories = {"head_only": [], "foot_only": [], "both": [], "neither": []}
    wins = []
    for cy in range(64):
        for cx in range(64):
            env.reset()
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            if obs2.state.name == "WIN":
                wins.append((cx, cy))
            g = frame(obs2)
            h = head_pos(g)
            f = foot_pos(g)
            hm = h != h0
            fm = f != f0
            if hm and fm:
                categories["both"].append(((cx, cy), h, f))
            elif hm:
                categories["head_only"].append(((cx, cy), h))
            elif fm:
                categories["foot_only"].append(((cx, cy), f))
            else:
                categories["neither"].append((cx, cy))

    for k, v in categories.items():
        print(f"{k}: {len(v)}")
    print(f"WINs in single clicks: {wins}")

    # Compute target for each click and see if head_only vs foot_only correlates
    # with target position relative to the hip (26, 58).
    def target(cx, cy):
        return ((cx + 26) // 2, (cy + 58) // 2)  # integer midpoint

    # Quadrant of target relative to hip
    def quad(cx, cy):
        tx, ty = target(cx, cy)
        dx = tx - 26
        dy = ty - 58
        return (int(np.sign(dx)), int(np.sign(dy)))

    head_quads: dict[tuple[int, int], int] = {}
    foot_quads: dict[tuple[int, int], int] = {}
    for (cx, cy), _ in categories["head_only"]:
        q = quad(cx, cy)
        head_quads[q] = head_quads.get(q, 0) + 1
    for (cx, cy), _ in categories["foot_only"]:
        q = quad(cx, cy)
        foot_quads[q] = foot_quads.get(q, 0) + 1

    print("\nTarget quadrant (dx, dy) from hip:")
    print(f"  head-move quadrants: {sorted(head_quads.items())}")
    print(f"  foot-move quadrants: {sorted(foot_quads.items())}")

    # Also, per target: is it consistent which leg moves?
    by_target_head: dict[tuple[int, int], int] = {}
    by_target_foot: dict[tuple[int, int], int] = {}
    for (cx, cy), h in categories["head_only"]:
        by_target_head[h] = by_target_head.get(h, 0) + 1
    for (cx, cy), f in categories["foot_only"]:
        by_target_foot[f] = by_target_foot.get(f, 0) + 1

    # Are there any targets that sometimes move head and sometimes move foot?
    both_sources = set(by_target_head.keys()) & set(by_target_foot.keys())
    print(f"\ntargets hit by both head_only AND foot_only clicks: {len(both_sources)}")
    if both_sources:
        for t in list(both_sources)[:5]:
            print(f"  {t}: head={by_target_head[t]}  foot={by_target_foot[t]}")


if __name__ == "__main__":
    main()
