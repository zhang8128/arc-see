"""SU15 solver — beam search using the pure-Python simulator. Fast enough
to solve L1-L3 (no enemies). L4+ also requires enemy simulation."""
import time
import importlib.util
from collections import deque

from solutions.su15_sim import (
    click as sim_click,
    is_won,
    initial_state_from_engine,
    SPRITE_SIZE,
    RADIUS,
    PLAY_Y_MIN,
    PLAY_Y_MAX,
    FRAME_W,
)

BASELINES = [18, 28, 50, 151, 18, 31, 50, 179, 41]


def clamp_click(x, y):
    return max(0, min(FRAME_W - 1, x)), max(PLAY_Y_MIN, min(PLAY_Y_MAX - 1, y))


def fruit_center(f):
    k, x, y = f
    w = SPRITE_SIZE[k]
    return x + w // 2, y + w // 2


def candidate_clicks(fruits, goal_rect, gspec):
    pts = set()
    DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]
    gx, gy, gw, gh = goal_rect
    gcx, gcy = gx + gw // 2, gy + gh // 2

    centers = [fruit_center(f) for f in fruits]
    kinds = [f[0] for f in fruits]

    for i, (fx, fy) in enumerate(centers):
        # Cardinal/diagonal max-step movement
        for dx, dy in DIRS:
            for step in (RADIUS - 1, RADIUS - 2, 5, 3):
                pts.add(clamp_click(fx + dx * step, fy + dy * step))

        # Toward goal center — exact and max
        ddx, ddy = gcx - fx, gcy - fy
        mag = max(abs(ddx), abs(ddy), 1)
        for step in (min(mag, RADIUS - 1), RADIUS - 1):
            if step > 0:
                pts.add(clamp_click(fx + round(ddx * step / mag), fy + round(ddy * step / mag)))

        # Goal area cells in range
        for ggy in range(gy, gy + gh):
            for ggx in range(gx, gx + gw):
                if (ggx - fx) ** 2 + (ggy - fy) ** 2 <= (RADIUS + 1) ** 2:
                    pts.add(clamp_click(ggx, ggy))

        # Toward each same-kind fruit (potential merge)
        for j, (ofx, ofy) in enumerate(centers):
            if i == j or kinds[i] != kinds[j]:
                continue
            mid_x, mid_y = (fx + ofx) // 2, (fy + ofy) // 2
            pts.add(clamp_click(mid_x, mid_y))
            ddx, ddy = ofx - fx, ofy - fy
            mag = max(abs(ddx), abs(ddy), 1)
            step = min(mag, RADIUS - 1)
            if step > 0:
                pts.add(clamp_click(fx + round(ddx * step / mag), fy + round(ddy * step / mag)))

    return pts


def heuristic(fruits, goal_rect, gspec):
    """Primary: cost to complete the goal via optimal merge+delivery.
    Strong signal on same-kind pair proximity so search chains merges."""
    n = len(fruits)
    if n == 0:
        return 10000
    gx, gy, gw, gh = goal_rect

    in_goal = {}
    out_pos_by_kind = {}
    for f in fruits:
        cx, cy = fruit_center(f)
        if gx <= cx < gx + gw and gy <= cy < gy + gh:
            in_goal[f[0]] = in_goal.get(f[0], 0) + 1
        else:
            out_pos_by_kind.setdefault(f[0], []).append((cx, cy))

    # Total "need" per kind — propagate down: a missing kind-3 needs 2 kind-2
    # which needs 4 kind-1 which needs 8 kind-0.
    # We compute needed[k] at each kind level, deducting what's already in goal.
    max_kind = max((rk for rk, _ in gspec), default=0)
    needed = [0] * (max_kind + 2)
    for rk, rc in gspec:
        have = in_goal.get(rk, 0)
        needed[rk] += max(0, rc - have)

    score = 0
    # Propagate shortage down the chain: each missing kind-(k+1) can be produced
    # from 2 kind-k. Count fruits we already have of each kind.
    have_by_kind = {k: len(positions) for k, positions in out_pos_by_kind.items()}
    for k in range(max_kind, 0, -1):
        req = needed[k]
        available = have_by_kind.get(k, 0)
        used = min(req, available)
        req -= used
        # Each "missing" unit at level k needs 2 at level k-1
        needed[k - 1] += req * 2
        # Each direct delivery costs ~delivery_clicks; each merge costs ~merge_clicks.
        # Rough cost: ~(movement + merge + delivery) per missing unit.
        score += req * 40  # merge+movement estimate per level

    # Bottom kind (0): unmet demand means infeasible
    if needed[0] > have_by_kind.get(0, 0):
        score += (needed[0] - have_by_kind.get(0, 0)) * 500

    # Total fruit count — strongly push toward fewer fruits (merging)
    score += n * 15

    # Delivery distance for any "mergeable-up" fruits: sum min distance to nearest same-kind partner
    for k, positions in out_pos_by_kind.items():
        if k > max_kind:
            score += len(positions) * 10  # over-merged
            continue
        if len(positions) >= 2:
            n_pos = len(positions)
            # Sum of "pair up" costs: greedily pair nearest
            pairs = []
            for i in range(n_pos):
                for j in range(i + 1, n_pos):
                    d = abs(positions[i][0] - positions[j][0]) + abs(positions[i][1] - positions[j][1])
                    pairs.append((d, i, j))
            pairs.sort()
            used = set()
            for d, i, j in pairs:
                if i in used or j in used:
                    continue
                # Clicks to merge a pair ≈ (d - 16) / 14 + 1 (movement + merge click)
                clicks = max(1, (d - 12) // 14 + 1)
                score += clicks * 6
                used.add(i)
                used.add(j)
            # Unpaired fruits of lower kind are less useful
            score += (n_pos - len(used)) * 30

    # For the highest-kind fruits (kind == max_kind), add delivery distance
    for k, positions in out_pos_by_kind.items():
        if k == max_kind:
            for cx, cy in positions:
                dx = max(gx - cx, 0, cx - (gx + gw - 1))
                dy = max(gy - cy, 0, cy - (gy + gh - 1))
                dist = abs(dx) + abs(dy)
                score += max(1, (dist - 1) // 7 + 1) * 5  # delivery clicks estimate

    return score


def beam_solve_sim(level_idx, beam_width=500, max_depth=300, max_time=300, verbose=True):
    fruits, goal_rect, gspec = initial_state_from_engine(level_idx)
    if verbose:
        print(f"L{level_idx + 1}: {len(fruits)} fruits, goal={goal_rect}, spec={gspec}, baseline={BASELINES[level_idx]}", flush=True)

    h0 = heuristic(fruits, goal_rect, gspec)
    beam = [(fruits, [], h0)]
    seen = {fruits: 0}
    t0 = time.time()
    last_print = t0

    for depth in range(max_depth):
        now = time.time()
        if now - t0 > max_time:
            print(f"  TIMEOUT at depth {depth} ({now-t0:.0f}s)", flush=True)
            return None
        if now - last_print > 3.0:
            print(f"  d={depth} beam={len(beam)} best_h={beam[0][2] if beam else None} seen={len(seen)} t={now-t0:.0f}s", flush=True)
            last_print = now

        next_beam = []
        for (state, path, _) in beam:
            cands = candidate_clicks(state, goal_rect, gspec)
            for (cx, cy) in cands:
                new_state, info = sim_click(state, cx, cy)
                if info == 'invalid' or info == 'no_op':
                    continue
                if new_state == state:
                    continue
                if is_won(new_state, goal_rect, gspec):
                    result = path + [(cx, cy)]
                    print(f"  FOUND! depth={depth + 1} clicks={len(result)} (t={time.time()-t0:.2f}s)", flush=True)
                    return result
                if not new_state:
                    # All fruits gone but not won — losing state
                    continue
                key = tuple(sorted(new_state))
                new_depth = len(path) + 1
                if key in seen and seen[key] <= new_depth:
                    continue
                seen[key] = new_depth
                h = heuristic(new_state, goal_rect, gspec)
                next_beam.append((new_state, path + [(cx, cy)], h))

        if not next_beam:
            print(f"  STUCK at depth {depth}", flush=True)
            return None

        next_beam.sort(key=lambda t: t[2])
        beam = next_beam[:beam_width]

    print(f"  EXHAUSTED max_depth={max_depth}", flush=True)
    return None


def verify_with_engine(level_idx, click_seq):
    """Replay clicks through the engine to confirm the solution actually wins."""
    spec = importlib.util.spec_from_file_location('su15_engine', 'environment_files/su15/4c352900/su15.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    from arcengine import GameAction, ActionInput
    g = mod.Su15(); g.set_level(level_idx)
    for (cx, cy) in click_seq:
        g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
        if g._current_level_index > level_idx or g._state.name == "WIN":
            return True
        if g._state.name == "GAME_OVER":
            return False
    return False


def main():
    import json
    all_solutions = {}
    for lvl in range(9):
        path = beam_solve_sim(lvl)
        if path is None:
            print(f"L{lvl + 1} FAILED — stop", flush=True)
            continue
        # Verify
        ok = verify_with_engine(lvl, path)
        print(f"  Engine verification: {'OK' if ok else 'FAILED'}", flush=True)
        if not ok:
            print(f"L{lvl + 1} sim solved but engine rejected", flush=True)
            continue
        all_solutions[lvl] = path
        print(flush=True)

    # Save solutions to file
    with open('solutions/su15_solutions.json', 'w') as f:
        json.dump({str(k): v for k, v in all_solutions.items()}, f, indent=2)
    print(f"Saved to solutions/su15_solutions.json")

    print("=" * 60)
    total = sum(len(p) for p in all_solutions.values())
    base = sum(BASELINES[k] for k in all_solutions.keys())
    print(f"Solved {len(all_solutions)}/9 — total={total}, baseline={base}, savings={base - total}")
    return all_solutions


if __name__ == "__main__":
    main()
