"""R11L: BFS again — this time checking obs.levels_completed, not state.name.

The level-completion signal for R11L may live in levels_completed, which only
increments on a level win. state might stay NOT_FINISHED until all 6 levels
are done.
"""
import numpy as np
from collections import deque
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

    obs = env.reset()
    f0 = foot_pos(frame(obs))
    print(f"initial foot: {f0}  levels_completed: {obs.levels_completed}")
    if f0 is None:
        raise RuntimeError("no foot")

    # First: single-click sweep checking levels_completed increment
    print("\n-- single-click sweep for levels_completed --")
    wins = []
    for cy in range(64):
        for cx in range(64):
            env.reset()
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            if obs2.levels_completed > 0:
                wins.append((cx, cy))
    print(f"single-click WINs by levels_completed: {len(wins)}")
    if wins:
        print(f"sample: {wins[:10]}")
        return  # Stop here — we found it

    # Build rejection set + reachable foot positions
    print("\n-- building rejection map from initial --")
    rejected: set[tuple[int, int]] = set()
    for cy in range(64):
        for cx in range(64):
            env.reset()
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            if foot_pos(frame(obs2)) == f0:
                rejected.add((cx, cy))
    print(f"rejected: {len(rejected)}")

    # BFS on foot positions; at each step record the click that led there.
    # Replay each path checking levels_completed.
    seen: dict[tuple[int, int], list[tuple[int, int]]] = {f0: []}
    q = deque([(f0, [])])
    max_depth = 7
    while q:
        foot, path = q.popleft()
        if len(path) >= max_depth:
            continue
        for cx in range(64):
            for cy in range(64):
                if (cx, cy) in rejected:
                    continue
                fx = (26 + cx) // 2
                fy = (58 + cy) // 2
                if max(abs(fx - foot[0]), abs(fy - foot[1])) > 8:
                    continue
                if (fx, fy) in seen:
                    continue
                seen[(fx, fy)] = path + [(cx, cy)]
                q.append(((fx, fy), path + [(cx, cy)]))
    print(f"\nBFS explored {len(seen)} foot cells")

    # Replay each path, check levels_completed
    print("replaying paths checking levels_completed...")
    found = None
    for foot, path in seen.items():
        if not path:
            continue
        env.reset()
        lc = 0
        for cx, cy in path:
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            lc = obs2.levels_completed
            if lc > 0:
                break
        if lc > 0:
            found = (foot, path)
            print(f"  WIN at foot={foot} via {len(path)} clicks: {path}")
            break
    if not found:
        print("  no path triggered levels_completed increment")


if __name__ == "__main__":
    main()
