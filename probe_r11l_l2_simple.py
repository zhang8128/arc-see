"""R11L: simplest L2 attempt — visit each color-3 cluster center in all orders.

L2 has 3 color-3 clusters. Try all 6 permutations as 3-click sequences.
If none work, try 4-click (visit each cluster + one extra).
"""
import numpy as np
import itertools
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def find_color3_clusters(g):
    H, W = g.shape
    visited = np.zeros_like(g, dtype=bool)
    clusters = []
    for y in range(H):
        for x in range(W):
            if g[y, x] != 3 or visited[y, x]:
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
                    if 0 <= ny < H and 0 <= nx < W and g[ny, nx] == 3 and not visited[ny, nx]:
                        stack.append((ny, nx))
            clusters.append(cluster)
    return clusters


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    L1 = [(36, 13), (26, 61), (42, 30)]
    env.reset()
    for cx, cy in L1:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    g = frame(env.step(GameAction.ACTION6, data={"x": 0, "y": 0}))
    # Oops: that extra click consumed a turn. Reset and play L1 again.
    env.reset()
    for cx, cy in L1:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    g = frame(obs)

    clusters = find_color3_clusters(g)
    print(f"L2 color-3 clusters: {len(clusters)}")
    centers = []
    for i, c in enumerate(clusters):
        ys = [p[0] for p in c]
        xs = [p[1] for p in c]
        cy, cx = int(np.mean(ys)), int(np.mean(xs))
        centers.append((cx, cy))
        print(f"  cluster {i}: {len(c)} cells, center=({cx},{cy})")

    # To place head on cluster center, click (cx-1, cy-1)
    clicks = [(cx - 1, cy - 1) for cx, cy in centers]
    print(f"\nclicks to place head on each: {clicks}")

    # Try all permutations of 3 clicks
    print("\n-- 3-click permutations --")
    for perm in itertools.permutations(clicks):
        env.reset()
        for cx, cy in L1:
            env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        for cx, cy in perm:
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        print(f"  {perm}: lc={obs2.levels_completed}")

    # If no wins yet, try adding an extra click at various positions after the 3
    print("\n-- 3 + 1 extra click --")
    for perm in itertools.permutations(clicks):
        for extra in [(36, 13), (26, 61), (42, 30), (32, 32), (10, 10), (50, 50)]:
            env.reset()
            for cx, cy in L1:
                env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            for cx, cy in perm:
                env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            obs2 = env.step(GameAction.ACTION6, data={"x": extra[0], "y": extra[1]})
            if obs2.levels_completed >= 2:
                print(f"  WIN: perm={perm} + extra={extra}")


if __name__ == "__main__":
    main()
