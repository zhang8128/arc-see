"""R11L: BFS over foot positions with 1-mark-per-stride cost.

Uses env.reset() + replay each candidate path. Slow but correct.
State key: (head, foot, counter). Goal: WIN state.

Strategy: at each step, enumerate clicks that would move the foot by
|Δ| ≤ 8 in each axis (stride budget). That gives ≤ 17×17 = 289 candidates
per step. Depth 7 = 289^7 = 1.8e17 too big. But with dedup on (foot) since
head can be recomputed from the last click, state is 4K.

Actually let's just BFS on (foot, counter), generating all single-click
successors, and look for WIN.
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


def count_marks(g):
    h = g.shape[0]
    return sum(1 for r in range(h) if int(g[r, 0]) == 5)


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    # Step 1: compute the set of foot positions reachable from the initial
    # state in ONE click that cost ≤1 mark. Foot delta max ≤ 8.
    obs = env.reset()
    g0 = frame(obs)
    f0 = foot_pos(g0)
    if f0 is None:
        raise RuntimeError("could not locate foot sprite in initial frame")
    print(f"initial foot: {f0}")

    # Enumerate clicks that move foot by max-axis ≤ 8 cells.
    # foot = midpoint(hip, click). delta_foot ≈ 0.5 * delta_click.
    # So delta_click ≤ 16 in each axis corresponds to delta_foot ≤ 8.
    # From an initial state, click must also be in the accepted region.
    # Enumerate all candidate clicks near the initial foot position range.
    candidates = []
    for cx in range(0, 64):
        for cy in range(0, 64):
            # Foot target = ((26+cx)//2, (58+cy)//2)
            fx = (26 + cx) // 2
            fy = (58 + cy) // 2
            dx = abs(fx - f0[0])
            dy = abs(fy - f0[1])
            if max(dx, dy) <= 8 and (dx + dy) > 0:
                candidates.append((cx, cy))
    print(f"candidates from initial: {len(candidates)}")

    # Walk each candidate from fresh state, check for WIN
    wins = []
    foot_targets = set()
    for cx, cy in candidates:
        env.reset()
        obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
        if obs2.state.name == "WIN":
            wins.append(((cx, cy),))
            print(f"  WIN in 1 click at ({cx},{cy})!")
        g = frame(obs2)
        f = foot_pos(g)
        if f is not None:
            foot_targets.add(f)
    print(f"reachable foot positions in 1 click (cost 1): {len(foot_targets)}")
    print(f"single-click WINs: {len(wins)}")

    # BFS over foot positions. Key: foot. Edge: 1-click move with |Δ|≤8.
    # But we need a CONNECTIVITY MAP, not just from initial state.
    # Precompute: for each (foot_src), which foot_dst reachable in 1 click of
    # cost 1. We can compute this analytically: foot_dst = midpoint(hip, click).
    # So for each foot_src, any click with fx=(26+cx)//2 within 8 of foot_src_x
    # is valid and moves foot to fx, fy. BUT: we also need the click to be
    # ACCEPTED (not rejected by the rejection map).
    #
    # Load the rejection set: scan fresh initial state.
    print("\nbuilding rejection set...")
    rejected: set[tuple[int, int]] = set()
    for cy in range(64):
        for cx in range(64):
            env.reset()
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            g = frame(obs2)
            f = foot_pos(g)
            # Foot unchanged AND col0 incremented means rejected-but-charged
            # Foot unchanged AND head unchanged == rejected
            if f == f0:
                rejected.add((cx, cy))
    print(f"rejected clicks (from initial state): {len(rejected)}")

    # Now: enumerate ALL foot positions reachable. For each foot_src, the
    # set of valid successor foot_dst via 1 cost-1 click.
    # Foot can only be in positions reachable via some click. Since
    # foot_x = (26 + cx) // 2, foot_x ∈ [13..44]. Similarly foot_y ∈ [29..60].
    # But not all combinations are reachable — only accepted clicks.

    # Hold on: we ASSUME the rejection set is state-independent. That's
    # probably wrong because the head blocks its own footprint. But as a
    # first approximation let's see what we get.
    all_foot_positions = set()
    for cx in range(64):
        for cy in range(64):
            if (cx, cy) in rejected:
                continue
            fx = (26 + cx) // 2
            fy = (58 + cy) // 2
            all_foot_positions.add((fx, fy))
    print(f"all reachable foot cells (approx): {len(all_foot_positions)}")

    # BFS from initial foot. State: (foot, depth). Edge: 1-stride move.
    # Cost 1 per edge. Try up to depth 7.
    seen = {f0: []}
    q = deque([(f0, [])])
    max_depth = 7
    win_path = None
    while q and win_path is None:
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

    print(f"\nBFS explored {len(seen)} distinct foot positions at depth ≤ {max_depth}")
    # Now we have click paths to reach each foot position. Try each path
    # and check if any yields WIN.
    print("replaying paths to check for WIN state...")
    wins2 = []
    checked = 0
    for foot, path in list(seen.items())[:2000]:
        if not path:
            continue
        env.reset()
        state = "NOT_FINISHED"
        for cx, cy in path:
            obs2 = env.step(GameAction.ACTION6, data={"x": cx, "y": cy})
            state = obs2.state.name
            if state != "NOT_FINISHED":
                break
        checked += 1
        if state == "WIN":
            wins2.append((foot, path))
            print(f"  WIN at foot={foot} via {len(path)} clicks: {path}")
            break
    print(f"checked {checked} paths, WINs: {len(wins2)}")


if __name__ == "__main__":
    main()
