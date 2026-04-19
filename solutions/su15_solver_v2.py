"""SU15 solver v2 — beam search using sim v2 (with enemy logic)."""
import time, json, os
from solutions.su15_sim_v2 import (
    click as sim_click,
    is_won,
    state_key,
    initial_state_from_engine,
    SPRITE_SIZE,
    ENEMY_W,
    ENEMY_H,
    RADIUS,
    PLAY_Y_MIN,
    PLAY_Y_MAX,
    FRAME_W,
)

BASELINES = [18, 28, 50, 151, 18, 31, 50, 179, 41]


def clamp_click(x, y):
    return max(0, min(FRAME_W - 1, x)), max(PLAY_Y_MIN, min(PLAY_Y_MAX - 1, y))


def candidate_clicks(state, goal_rects, fspec, espec):
    fruits, enemies = state
    pts = set()
    DIRS = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]

    for i, (k, x, y) in enumerate(fruits):
        w = SPRITE_SIZE[k]
        cx, cy = x + w // 2, y + w // 2

        # Cardinal/diagonal max-step
        for dx, dy in DIRS:
            pts.add(clamp_click(cx + dx * (RADIUS - 1), cy + dy * (RADIUS - 1)))

        # Toward each goal
        for gx, gy, gw, gh in goal_rects:
            gcx, gcy = gx + gw // 2, gy + gh // 2
            ddx, ddy = gcx - cx, gcy - cy
            mag = max(abs(ddx), abs(ddy), 1)
            for step in (min(mag, RADIUS - 1), RADIUS - 1):
                if step > 0:
                    pts.add(clamp_click(cx + round(ddx * step / mag), cy + round(ddy * step / mag)))
            # Goal cells in close range
            if (gcx - cx) ** 2 + (gcy - cy) ** 2 <= (RADIUS + 1) ** 2:
                pts.add(clamp_click(gcx, gcy))

        # Same-kind merge target
        for j in range(i + 1, len(fruits)):
            ok, ox, oy = fruits[j]
            if ok != k:
                continue
            ow = SPRITE_SIZE[ok]
            ocx, ocy = ox + ow // 2, oy + ow // 2
            pts.add(clamp_click((cx + ocx) // 2, (cy + ocy) // 2))
            ddx, ddy = ocx - cx, ocy - cy
            mag = max(abs(ddx), abs(ddy), 1)
            step = min(mag, RADIUS - 1)
            if step > 0:
                pts.add(clamp_click(cx + round(ddx * step / mag), cy + round(ddy * step / mag)))

    # Enemy targeting clicks
    if espec or enemies:
        kind1_enemies = [(i, e) for i, e in enumerate(enemies) if e[0] == 1]
        for idx, (ek, ex, ey, _cd) in enumerate(enemies):
            ecx = ex + ENEMY_W // 2
            ecy = ey + ENEMY_H // 2
            if ek == 1:
                # Toward each goal
                for gx, gy, gw, gh in goal_rects:
                    gcx, gcy = gx + gw // 2, gy + gh // 2
                    ddx, ddy = gcx - ecx, gcy - ecy
                    mag = max(abs(ddx), abs(ddy), 1)
                    step = min(mag, RADIUS - 1)
                    if step > 0:
                        pts.add(clamp_click(ecx + round(ddx * step / mag), ecy + round(ddy * step / mag)))
                    if (gcx - ecx) ** 2 + (gcy - ecy) ** 2 <= (RADIUS + 1) ** 2:
                        pts.add(clamp_click(gcx, gcy))
                # Toward each other same-kind enemy (merge)
                for j_idx, (jek, jex, jey, _) in enumerate(enemies):
                    if j_idx <= idx or jek != ek:
                        continue
                    jcx = jex + ENEMY_W // 2
                    jcy = jey + ENEMY_H // 2
                    pts.add(clamp_click((ecx + jcx) // 2, (ecy + jcy) // 2))

        # For each high-kind fruit (>max_needed), generate clicks that put it in front
        # of a chasing enemy (so the enemy hits it)
        max_needed = max((rk for rk, _ in fspec), default=0)
        for k, x, y in fruits:
            if k <= max_needed:
                continue
            w = SPRITE_SIZE[k]
            cx_f = x + w // 2
            cy_f = y + w // 2
            for ek, ex, ey, cd in enemies:
                if cd > 0:
                    continue
                ecx = ex + ENEMY_W // 2
                ecy = ey + ENEMY_H // 2
                # Click that moves the high-kind fruit toward the enemy
                ddx, ddy = ecx - cx_f, ecy - cy_f
                mag = max(abs(ddx), abs(ddy), 1)
                step = min(mag, RADIUS - 1)
                if step > 0:
                    pts.add(clamp_click(cx_f + round(ddx * step / mag), cy_f + round(ddy * step / mag)))

    return pts


def heuristic(state, goal_rects, fspec, espec):
    fruits, enemies = state
    n = len(fruits)
    if n == 0 and not espec:
        return 10000

    in_goal_f = {}
    out_pos_by_kind = {}
    for k, x, y in fruits:
        w = SPRITE_SIZE[k]
        cx = x + w // 2
        cy = y + w // 2
        in_g = False
        for gx, gy, gw, gh in goal_rects:
            if gx <= cx < gx + gw and gy <= cy < gy + gh:
                in_g = True
                break
        if in_g:
            in_goal_f[k] = in_goal_f.get(k, 0) + 1
        else:
            out_pos_by_kind.setdefault(k, []).append((cx, cy))

    in_goal_e = {}
    out_enemies = []
    for ek, ex, ey, cd in enemies:
        ecx = ex + ENEMY_W // 2
        ecy = ey + ENEMY_H // 2
        in_g = False
        for gx, gy, gw, gh in goal_rects:
            if gx <= ecx < gx + gw and gy <= ecy < gy + gh:
                in_g = True
                break
        if in_g:
            in_goal_e[ek] = in_goal_e.get(ek, 0) + 1
        else:
            out_enemies.append((ek, ecx, ecy))

    # Fruit kind requirements
    max_kind = max((rk for rk, _ in fspec), default=0)
    needed = {}  # kind → count missing
    for rk, rc in fspec:
        have = in_goal_f.get(rk, 0)
        needed[rk] = needed.get(rk, 0) + max(0, rc - have)

    score = 0
    # For each missing requirement, try to satisfy via:
    # 1. Existing same-kind fruit out-of-goal (cheapest)
    # 2. Higher-kind fruit downgraded (1 hit per level diff)
    # 3. Lower-kind fruits merged up (2^N + N-1 cost)
    have_by_kind = dict((k, list(p)) for k, p in out_pos_by_kind.items())
    for rk in sorted(needed.keys(), reverse=True):
        cnt = needed[rk]
        # Try same kind first
        avail = have_by_kind.get(rk, [])
        use_same = min(cnt, len(avail))
        if use_same > 0:
            del avail[:use_same]
            cnt -= use_same
        # Try higher-kind via downgrade (each level costs ~3 enemy hits + movement)
        if cnt > 0:
            for higher_k in sorted([k for k in have_by_kind if k > rk]):
                higher_avail = have_by_kind[higher_k]
                while cnt > 0 and higher_avail:
                    higher_avail.pop()
                    score += (higher_k - rk) * 8  # ~3 clicks per downgrade level
                    cnt -= 1
                if cnt == 0:
                    break
        # Try lower-kind merge-up (2^N base fruits, N-1 merges)
        if cnt > 0:
            for lower_k in sorted([k for k in have_by_kind if k < rk], reverse=True):
                lower_avail = have_by_kind[lower_k]
                level_diff = rk - lower_k
                fruits_needed = 1 << level_diff  # 2^level_diff
                while cnt > 0 and len(lower_avail) >= fruits_needed:
                    del lower_avail[-fruits_needed:]
                    score += fruits_needed * 4 + (fruits_needed - 1) * 6  # rough cost
                    cnt -= 1
                if cnt == 0:
                    break
        if cnt > 0:
            score += cnt * 600  # truly infeasible

    score += n * 8

    for k, positions in out_pos_by_kind.items():
        if k > max_kind:
            score += len(positions) * 10
            continue
        if len(positions) >= 2:
            n_pos = len(positions)
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
                clicks = max(1, (d - 12) // 14 + 1)
                score += clicks * 6
                used.add(i)
                used.add(j)
            score += (n_pos - len(used)) * 30

    for k, positions in out_pos_by_kind.items():
        if k == max_kind:
            for cx, cy in positions:
                dist = 1e9
                for gx, gy, gw, gh in goal_rects:
                    dx = max(gx - cx, 0, cx - (gx + gw - 1))
                    dy = max(gy - cy, 0, cy - (gy + gh - 1))
                    d = abs(dx) + abs(dy)
                    if d < dist:
                        dist = d
                score += max(1, (dist - 1) // 7 + 1) * 5

    # Enemy spec: propagate down through enemy kind chain (1 → 2 → 3)
    if espec:
        e_needed = {}
        for ek, ec in espec:
            have = in_goal_e.get(ek, 0)
            e_needed[ek] = e_needed.get(ek, 0) + max(0, ec - have)

        e_have = {}
        for oek, _, _ in out_enemies:
            e_have[oek] = e_have.get(oek, 0) + 1

        for rk in sorted(e_needed.keys(), reverse=True):
            cnt = e_needed[rk]
            avail = e_have.get(rk, 0)
            use = min(cnt, avail)
            cnt -= use
            e_have[rk] = avail - use
            if cnt > 0:
                for lower_k in sorted([k for k in e_have if k < rk], reverse=True):
                    level_diff = rk - lower_k
                    need_per = 1 << level_diff
                    while cnt > 0 and e_have.get(lower_k, 0) >= need_per:
                        e_have[lower_k] -= need_per
                        score += need_per * 5 + level_diff * 8
                        cnt -= 1
                    if cnt == 0:
                        break
            if cnt > 0:
                score += cnt * 600
        # Also penalize unsatisfied enemy positioning vs goal
        for oek, ocx, ocy in out_enemies:
            dist_min = 1e9
            for gx, gy, gw, gh in goal_rects:
                dx = max(gx - ocx, 0, ocx - (gx + gw - 1))
                dy = max(gy - ocy, 0, ocy - (gy + gh - 1))
                d = abs(dx) + abs(dy)
                if d < dist_min:
                    dist_min = d
            score += dist_min // 6

    return int(score)


def bfs_solve_sim_v2(level_idx, prefix_solutions=None, max_states=20_000_000, max_time=600, verbose=True):
    """Plain BFS — no heuristic. Finds shortest sequence by depth."""
    from collections import deque
    state, goal_rects, fspec, espec = initial_state_from_engine(level_idx, prefix_solutions)
    if verbose:
        print(f"L{level_idx + 1}: BFS from {state}, baseline={BASELINES[level_idx]}", flush=True)
    queue = deque([(state, [])])
    seen = {state_key(state)}
    t0 = time.time()
    last_print = t0
    iters = 0
    while queue:
        st, path = queue.popleft()
        iters += 1
        if iters % 10000 == 0:
            now = time.time()
            if now - t0 > max_time:
                print(f"  TIMEOUT iter={iters} ({now-t0:.0f}s)", flush=True)
                return None
            if iters > max_states:
                print(f"  STATE CAP reached iter={iters}", flush=True)
                return None
            if now - last_print > 5.0:
                print(f"  iter={iters} q={len(queue)} d={len(path)} seen={len(seen)} t={now-t0:.0f}s", flush=True)
                last_print = now
        for (cx, cy) in candidate_clicks(st, goal_rects, fspec, espec):
            new_state, info = sim_click(st, cx, cy)
            if info == 'invalid' or info == 'no_op':
                continue
            key = state_key(new_state)
            if key in seen:
                continue
            if state_key(new_state) == state_key(st):
                continue
            if is_won(new_state, goal_rects, fspec, espec):
                result = path + [(cx, cy)]
                print(f"  FOUND! clicks={len(result)} iter={iters} (t={time.time()-t0:.1f}s)", flush=True)
                return result
            seen.add(key)
            queue.append((new_state, path + [(cx, cy)]))
    return None


def beam_solve_sim_v2(level_idx, prefix_solutions=None, beam_width=200, max_depth=300, max_time=300, verbose=True):
    """A* search with f = g + h*1.5 (slightly inadmissible for speed)."""
    import heapq
    state, goal_rects, fspec, espec = initial_state_from_engine(level_idx, prefix_solutions)
    n0 = len(state[0])
    if verbose:
        print(f"L{level_idx + 1}: {n0} fruits, {len(state[1])} enemies, fspec={fspec}, espec={espec}, baseline={BASELINES[level_idx]}", flush=True)

    h0 = heuristic(state, goal_rects, fspec, espec)
    counter = 0
    open_set = [(h0, counter, state, [])]
    counter += 1
    best_g = {state_key(state): 0}
    expansions = 0
    t0 = time.time()
    last_print = t0
    H_WEIGHT = 10  # very strong bias toward lower h (almost greedy)

    while open_set:
        now = time.time()
        if now - t0 > max_time:
            print(f"  TIMEOUT at expansions={expansions} ({now-t0:.0f}s)", flush=True)
            return None
        if now - last_print > 3.0:
            best_h_now = open_set[0][0] if open_set else None
            print(f"  exp={expansions} open={len(open_set)} best_f={best_h_now} closed={len(best_g)} t={now-t0:.0f}s", flush=True)
            last_print = now

        f, _, st, path = heapq.heappop(open_set)
        expansions += 1

        if expansions > max_depth * 1000:  # cap expansions
            print(f"  EXHAUSTED expansions cap", flush=True)
            return None

        key = state_key(st)
        g_cur = len(path)
        if best_g.get(key, 1e9) < g_cur:
            continue  # stale

        cands = candidate_clicks(st, goal_rects, fspec, espec)
        for (cx, cy) in cands:
            new_state, info = sim_click(st, cx, cy)
            if info == 'invalid' or info == 'no_op':
                continue
            if state_key(new_state) == key:
                continue
            if is_won(new_state, goal_rects, fspec, espec):
                result = path + [(cx, cy)]
                print(f"  FOUND! clicks={len(result)} expansions={expansions} (t={time.time()-t0:.2f}s)", flush=True)
                return result
            new_key = state_key(new_state)
            new_g = g_cur + 1
            if best_g.get(new_key, 1e9) <= new_g:
                continue
            best_g[new_key] = new_g
            h = heuristic(new_state, goal_rects, fspec, espec)
            f = new_g + H_WEIGHT * h
            heapq.heappush(open_set, (f, counter, new_state, path + [(cx, cy)]))
            counter += 1

    print(f"  EXHAUSTED open set", flush=True)
    return None


def verify_with_engine(level_idx, click_seq, prefix_solutions=None):
    """Replay full prefix + this level via engine; check natural level advance."""
    import importlib.util
    spec = importlib.util.spec_from_file_location('su15_engine', 'environment_files/su15/4c352900/su15.py')
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    from arcengine import GameAction, ActionInput
    g = mod.Su15()
    if prefix_solutions and level_idx > 0:
        for prev in range(level_idx):
            for (cx, cy) in prefix_solutions[str(prev)]:
                g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
        if g._current_level_index != level_idx:
            return False, f'progression failed: at {g._current_level_index}'
    else:
        g.set_level(level_idx)
    for (cx, cy) in click_seq:
        g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
        if g._current_level_index > level_idx:
            return True, 'won'
        if g._state.name == 'GAME_OVER':
            return False, 'game over'
    return False, 'no win'


if __name__ == "__main__":
    import sys
    lvl = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    path = 'solutions/su15_solutions.json'
    sols = {}
    if os.path.exists(path):
        with open(path) as f:
            sols = json.load(f)
    for prev in range(lvl):
        if str(prev) not in sols:
            print(f"ERROR: missing L{prev+1} solution")
            sys.exit(1)
    p = beam_solve_sim_v2(lvl, prefix_solutions=sols)
    if p:
        ok, why = verify_with_engine(lvl, p, sols)
        print(f"Verify L{lvl+1}: {ok} ({why})")
        if ok:
            sols[str(lvl)] = p
            with open(path, 'w') as f:
                json.dump(sols, f, indent=2)
            print(f"Saved L{lvl+1}")
