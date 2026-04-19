"""R11L L2: find all f-color (15) clusters. Maybe arm 1 has a goal diamond
in color f that I missed.
"""
import copy
import numpy as np
import arc_agi
from arcengine import GameAction


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
                for dy, dx in [(-1, 0), (1, 0), (0, -1), (0, 1),
                               (-1, -1), (-1, 1), (1, -1), (1, 1)]:  # include diagonal
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < H and 0 <= nx < W and g[ny, nx] == color and not visited[ny, nx]:
                        stack.append((ny, nx))
            out.append(cluster)
    return out


def clusters_4conn(g, color):
    """Same as clusters_of but 4-connected only."""
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


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    g = np.array(obs.frame[-1], dtype=np.int64)

    print("-- f-cells (color 15) --")
    print(f"total f-cells: {int(np.sum(g == 15))}")
    f_clusters_4 = clusters_4conn(g, 15)
    print(f"4-connected clusters: {len(f_clusters_4)}")
    for i, c in enumerate(f_clusters_4):
        ys = [p[0] for p in c]
        xs = [p[1] for p in c]
        center = (int(np.mean(xs)), int(np.mean(ys)))
        print(f"  cluster {i}: size={len(c)} center={center}")

    # Also 1-cell f dots forming diamonds?
    singleton_f = [c for c in f_clusters_4 if len(c) == 1]
    if len(singleton_f) >= 4:
        print(f"\nsingleton f cells ({len(singleton_f)}):")
        for c in singleton_f:
            y, x = c[0]
            print(f"  ({x}, {y})")

    # Also look at color 1 cells (arm body)
    print(f"\n-- color 1 cells --")
    print(f"total 1-cells: {int(np.sum(g == 1))}")
    c1 = clusters_4conn(g, 1)
    print(f"4-connected clusters: {len(c1)}")
    for i, c in enumerate(c1[:20]):
        ys = [p[0] for p in c]
        xs = [p[1] for p in c]
        center = (int(np.mean(xs)), int(np.mean(ys)))
        print(f"  cluster {i}: size={len(c)} center={center}")


if __name__ == "__main__":
    main()
