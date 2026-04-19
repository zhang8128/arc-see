"""R11L: Targeted win-trigger tests.

H1: Click the hip itself — collapses both legs to hip, might win.
H2: Click the f-center of the diamond (27, 59).
H3: Click each cloud cluster at the top (decor = collectibles).
H4: Sweep arm through a sequence.

Also: re-run rejection scan after moving arm, to separate static walls
from the dynamic head-footprint.
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


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    # H1 & H2: direct clicks at the hip and diamond center
    print("-- direct hip/diamond clicks --")
    for cx, cy in [(26, 58), (27, 59), (25, 59), (28, 58), (27, 58)]:
        env.reset()
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(obs2)
        print(f"  click({cx},{cy}): head={head_pos(g)}  foot={foot_pos(g)}  state={obs2.state.name}")

    # Find cloud cluster centers at the top of the initial frame
    g0 = frame(env.reset())
    print("\n-- finding clouds in rows 0..6 --")
    # Any '5' cells in rows 0..6 with neighbour '5's form clusters.
    cloud_cells = [(int(x), int(y)) for y in range(7) for x in range(64) if g0[y, x] == 5]
    # Simple connected-component labeling
    visited = set()
    clusters = []
    for start in cloud_cells:
        if start in visited:
            continue
        stack = [start]
        cluster = []
        while stack:
            p = stack.pop()
            if p in visited:
                continue
            visited.add(p)
            cluster.append(p)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                n = (p[0] + dx, p[1] + dy)
                if 0 <= n[0] < 64 and 0 <= n[1] < 64 and n not in visited:
                    if g0[n[1], n[0]] == 5:
                        stack.append(n)
        clusters.append(cluster)
    print(f"found {len(clusters)} cloud clusters in rows 0..6")
    centers = []
    for i, cluster in enumerate(clusters):
        cx = sum(p[0] for p in cluster) // len(cluster)
        cy = sum(p[1] for p in cluster) // len(cluster)
        centers.append((cx, cy))
        print(f"  cluster {i}: {len(cluster)} cells  center≈({cx},{cy})")

    # H3: click each cloud center
    print("\n-- clicking each cloud center --")
    for cx, cy in centers:
        env.reset()
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g = frame(obs2)
        # Did the CLOUD disappear from the initial position?
        cloud_gone = not np.array_equal(g[:7, :], g0[:7, :])
        print(f"  click({cx},{cy}): head={head_pos(g)}  foot={foot_pos(g)}  state={obs2.state.name}  cloud_changed={cloud_gone}")

    # H4: Try sequences — click each cloud in one session
    print("\n-- sequence: click all cloud centers --")
    env.reset()
    for i, (cx, cy) in enumerate(centers):
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        if obs2.state.name == "WIN":
            print(f"  WIN at click {i}: ({cx},{cy})")
            break
        g = frame(obs2)
        print(f"  click{i} ({cx},{cy}): head={head_pos(g)}  state={obs2.state.name}")
    else:
        print("  no WIN from cloud sequence")

    # Re-check: after moving head away, is (5..9, 34..38) still rejected?
    # If yes → static wall. If no → dynamic head footprint.
    print("\n-- static vs dynamic walls at (5..9, 34..38) --")
    static_walls = []
    dynamic_walls = []
    for cy in range(34, 39):
        for cx in range(5, 10):
            env.reset()
            # Move head far away first
            env.step(GameAction.ACTION6, data={"x": 40, "y": 20})
            # Then try to click into the old head footprint
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            g2 = frame(obs2)
            h2 = head_pos(g2)
            if h2 is not None and abs(h2[0] - cx) <= 1 and abs(h2[1] - cy) <= 1:
                dynamic_walls.append((cx, cy))
            else:
                static_walls.append((cx, cy))
    print(f"  after moving head to (40,20), cells in (5..9, 34..38):")
    print(f"    now accepted (head went there): {dynamic_walls}")
    print(f"    still rejected: {static_walls}")


if __name__ == "__main__":
    main()
