"""R11L: detailed L2 exploration — find new head/foot sprites and test the
arm mechanic on L2.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def clusters_of(g, color):
    H, W = g.shape
    visited = np.zeros_like(g, dtype=bool)
    out = []
    for y in range(H):
        for x in range(W):
            if g[y, x] != color or visited[y, x]:
                continue
            stack = [(y, x)]
            cluster = []
            while stack:
                cy, cx = stack.pop()
                if visited[cy, cx]:
                    continue
                visited[cy, cx] = True
                cluster.append((cy, cx))
                for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and g[ny, nx] == color and not visited[ny, nx]:
                        stack.append((ny, nx))
            out.append(cluster)
    return out


def center(cluster):
    ys = [p[0] for p in cluster]
    xs = [p[1] for p in cluster]
    return (int(np.mean(xs)), int(np.mean(ys)))


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    print(f"after L1: lc={obs.levels_completed}  available={list(obs.available_actions)}")
    g = frame(obs)
    H, W = g.shape

    # Find sixes (foot centers)
    sixes = np.argwhere(g == 6)
    print(f"color-6 cells: {sixes.tolist()}")
    # Find f-ring (color 15) with 0 neighbors (old head style)
    print(f"\ncolor-f (15) count: {int(np.sum(g == 15))}")
    # Find c-ring (color 12) cells
    print(f"color-c (12) count: {int(np.sum(g == 12))}")
    # Color 3 clusters with centers
    c3 = clusters_of(g, 3)
    print(f"\ncolor-3 clusters: {len(c3)}")
    for i, c in enumerate(c3):
        print(f"  {i}: size={len(c)}, center={center(c)}")

    # Color 12 (c) clusters
    c12 = clusters_of(g, 12)
    print(f"\ncolor-c (12) clusters: {len(c12)}")
    for i, c in enumerate(c12):
        print(f"  {i}: size={len(c)}, center={center(c)}")

    # Color 10 (a) clusters — probably the new walkable terrain
    c10 = clusters_of(g, 10)
    print(f"\ncolor-a (10) clusters: {len(c10)}")
    for i, c in enumerate(c10[:5]):
        print(f"  {i}: size={len(c)}, center={center(c)}")

    # Test the arm mechanic on L2: click a few positions, check if a head/foot moves
    print("\n-- testing the arm mechanic on L2 --")
    # Use the deepcopy pattern via env internals if possible
    # Simpler: play L1 fresh each time
    for (cx, cy) in [(30, 30), (20, 20), (50, 50), (40, 40)]:
        env.reset()
        for px, py in L1:
            env.step(GameAction.ACTION6, data={"x": px, "y": py})
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        g2 = frame(obs2)
        # Count colors; diff against L2 initial
        diff = int(np.sum(g != g2))
        print(f"  click({cx},{cy}) in L2: diff={diff} cells, lc={obs2.levels_completed}")


if __name__ == "__main__":
    main()
