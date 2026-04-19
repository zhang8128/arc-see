"""R11L: apply the L1 'A → hip → B' pattern to L2.

L2 hip center from probe_r11l_levels: (39, 28). But L2 has 48 color-3 cells,
probably multiple diamonds. First, enumerate color-3 clusters. Then try
3-click sequences with each cluster as the middle click.
"""
import numpy as np
import arc_agi
from arcengine import GameAction


def frame(obs):
    return np.array(obs.frame[-1], dtype=np.int64)


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    # Play L1 → L2
    env.reset()
    for cx, cy in [(36, 13), (26, 61), (42, 30)]:
        obs = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
    print(f"after L1: lc={obs.levels_completed}")

    g = frame(obs)
    # Find color-3 clusters via flood fill
    H, W = g.shape
    visited = np.zeros_like(g, dtype=bool)
    clusters = []
    for y in range(H):
        for x in range(W):
            if g[y, x] != 3 or visited[y, x]:
                continue
            # BFS
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
    print(f"color-3 clusters in L2: {len(clusters)}")
    cluster_centers = []
    for i, c in enumerate(clusters):
        ys = [p[0] for p in c]
        xs = [p[1] for p in c]
        cy, cx = int(np.mean(ys)), int(np.mean(xs))
        cluster_centers.append((cx, cy))
        print(f"  cluster {i}: {len(c)} cells, center=({cx}, {cy})")

    # For each cluster, find a click that places the head on its center
    # Under head = click + (1,1), to place head at (cx, cy) click (cx-1, cy-1).
    # But clamping may happen near edges. Try the click and check head.
    # Actually we don't need the head to be exactly on the center — we need
    # a click whose head lands in the cluster. Sweep click positions near each
    # cluster center.

    # Simpler: just sweep all 64x64 clicks for a 2-click path A → hip_candidate → B.
    # With 3 clusters as hip candidates, that's 3 * 4096 * 4096 = too much.
    # Prune: middle click is specifically ONE of the cluster-centering clicks.
    # First click and third click sweep a coarse grid.

    # One middle-click per cluster: the cluster center (head target = center-1)
    # with head = click+(1,1), to place head at cluster center we click (cx-1, cy-1)
    hip_middle_clicks = [(cx - 1, cy - 1) for cx, cy in cluster_centers]
    print(f"\nmiddle click candidates: {hip_middle_clicks}")

    # First/third click: 4-pixel grid
    outer_clicks = [(x, y) for x in range(0, 64, 4) for y in range(0, 64, 4)]
    print(f"outer click candidates: {len(outer_clicks)} each side")
    total = len(hip_middle_clicks) * len(outer_clicks) * len(outer_clicks)
    print(f"total 3-click combos: {total}")

    wins = []
    tried = 0
    L1_SOL = [(36, 13), (26, 61), (42, 30)]
    for mid in hip_middle_clicks:
        for a in outer_clicks:
            for b in outer_clicks:
                env.reset()
                for cx, cy in L1_SOL:
                    env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
                env.step(GameAction.ACTION6, data={"x": a[0], "y": a[1]})
                env.step(GameAction.ACTION6, data={"x": mid[0], "y": mid[1]})
                obs3 = env.step(GameAction.ACTION6, data={"x": b[0], "y": b[1]})
                tried += 1
                if obs3.levels_completed >= 2:
                    wins.append((a, mid, b))
                    print(f"  L2 WIN ({len(wins)}): {a} -> {mid} -> {b}")
                    if len(wins) >= 5:
                        return
    print(f"\ntried {tried} combos, found {len(wins)} L2 wins")


if __name__ == "__main__":
    main()
