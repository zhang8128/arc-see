"""R11L L2: rejection map + arm motion analysis.

Plays L1 to enter L2, then scans all 4096 clicks to build:
  1. rejection map (which clicks do nothing)
  2. for each accepted click, the exact diff count vs L2 initial
  3. the distinct "movable foot" positions reached

The rejection map should reveal L2's walkable geometry and any hidden goal
diamonds (like L1's upper and middle diamonds were hidden in the rejection
map shape).
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def movable_foot(g, static=(49, 41)):
    """Return the non-static foot position."""
    sixes = np.argwhere(g == 6)
    for y, x in sixes:
        if (int(x), int(y)) != static:
            return (int(x), int(y))
    return None


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    g_l2_init = frame(obs)
    f0 = movable_foot(g_l2_init)
    print(f"L2 initial movable foot: {f0}")

    # Scan all 4096 clicks
    rejected: set[tuple[int, int]] = set()
    reach: dict[tuple[int, int], tuple[int, int]] = {}
    for cy in range(64):
        for cx in range(64):
            env.reset()
            for px, py in L1:
                env.step(GameAction.ACTION6, data={"x": px, "y": py})
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            g = frame(obs2)
            f = movable_foot(g)
            # Compute diff count (excluding col 0 counter)
            diff = int(np.sum(g[:, 1:] != g_l2_init[:, 1:]))
            if diff == 0:
                rejected.add((cx, cy))
            elif f is not None:
                reach[(cx, cy)] = f

    print(f"\nL2 rejected clicks: {len(rejected)}")
    print(f"L2 accepted clicks that moved foot: {len(reach)}")

    targets = set(reach.values())
    print(f"distinct foot landings: {len(targets)}")
    if targets:
        xs = [p[0] for p in targets]
        ys = [p[1] for p in targets]
        print(f"  foot x range: {min(xs)}..{max(xs)}  y range: {min(ys)}..{max(ys)}")

    # Print rejection map at 2-pixel stride
    print("\n-- L2 rejection map (# = rejected) --")
    for cy in range(0, 64, 2):
        row = "".join("#" if (cx, cy) in rejected else "." for cx in range(0, 64, 2))
        print(f"  y={cy:2d}: {row}")

    # Look for ISOLATED accepted-regions (hidden goal diamonds)
    # An accepted-region is a connected set of accepted clicks.
    # If there are multiple disconnected accepted-regions, each is a potential
    # "goal diamond".
    accepted_set = {(cx, cy) for cx in range(64) for cy in range(64)
                    if (cx, cy) not in rejected}
    print(f"\ntotal accepted clicks: {len(accepted_set)}")
    # Flood-fill components
    seen_accepted = set()
    components = []
    for start in accepted_set:
        if start in seen_accepted:
            continue
        stack = [start]
        comp = []
        while stack:
            p = stack.pop()
            if p in seen_accepted:
                continue
            seen_accepted.add(p)
            comp.append(p)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                n = (p[0] + dx, p[1] + dy)
                if n in accepted_set and n not in seen_accepted:
                    stack.append(n)
        components.append(comp)
    print(f"accepted-click components: {len(components)}")
    for i, comp in enumerate(components):
        xs = [p[0] for p in comp]
        ys = [p[1] for p in comp]
        center = (int(np.mean(xs)), int(np.mean(ys)))
        print(f"  comp {i}: {len(comp)} cells, bbox x:{min(xs)}..{max(xs)} y:{min(ys)}..{max(ys)}, center={center}")


if __name__ == "__main__":
    main()
