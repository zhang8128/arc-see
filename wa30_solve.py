"""WA30 solver — decomposition + cooperative greedy with helpers."""
import sys
sys.path.insert(0, "environment_files/wa30/ee6fef47")
import copy
from collections import deque
from itertools import permutations
from wa30 import Wa30
from arcengine import ActionInput, GameAction

STEP = 4
DIRS = [(0, -STEP), (0, STEP), (-STEP, 0), (STEP, 0)]
ACT_FOR_DIR = {(0, -STEP): 1, (0, STEP): 2, (-STEP, 0): 3, (STEP, 0): 4}


def engine_step(g, action_id):
    g._set_action(ActionInput(id=action_id))
    g.step()
    if g._next_level:
        g._really_set_next_level()
    return g._state.name


def extract_level(g):
    level = g.current_level
    collidable = set()
    for s in level.get_sprites():
        if s.is_collidable and not any(t in s.tags for t in ("geezpjgiyd", "kdweefinfi", "ysysltqlke", "wbmdvjhthc")):
            collidable.add((s.x, s.y))
    for i in range(0, 64, STEP):
        collidable.add((-STEP, i)); collidable.add((64, i))
        collidable.add((i, -STEP)); collidable.add((i, 64))
    special = set((s.x, s.y) for s in level.get_sprites_by_tag("bnzklblgdk"))
    walls = collidable | special  # Player blocked by both
    # Pieces only blocked by collidable, NOT by bnzklblgdk (per game rules)

    piece_targets = set()
    for tx, ty in g.wyzquhjerd:
        if tx % STEP == 0 and ty % STEP == 0:
            piece_targets.add((tx, ty))

    player = level.get_sprites_by_tag("wbmdvjhthc")[0]
    return {
        "walls": frozenset(walls),
        "piece_walls": frozenset(collidable),
        "absolute_walls": frozenset(special),  # bnzklblgdk: absolute block for player even when carrying
        "targets": piece_targets,
        "player": (player.x, player.y),
        "pieces": [(p.x, p.y) for p in level.get_sprites_by_tag("geezpjgiyd")],
        "n_helpers": len(level.get_sprites_by_tag("kdweefinfi")),
        "n_enemies": len(level.get_sprites_by_tag("ysysltqlke")),
        "step_limit": g.kuncbnslnm.current_steps,
    }


def bfs_walk(start, goal_set, blocked):
    if start in goal_set:
        return [start]
    visited = {start}
    queue = deque([(start, [start])])
    while queue:
        pos, path = queue.popleft()
        for d in DIRS:
            nb = (pos[0] + d[0], pos[1] + d[1])
            if nb in goal_set:
                return path + [nb]
            if nb not in visited and nb not in blocked:
                visited.add(nb)
                queue.append((nb, path + [nb]))
    return None


def bfs_carry(player_start, carry_offset, goal_set,
              player_blocked, piece_blocked=None, player_absolute=None):
    """BFS for carrying.
    player_blocked: player can enter if == piece_pos (collidable + sprites)
    player_absolute: player CANNOT enter even if piece is there (bnzklblgdk)
    piece_blocked: piece can enter if == player_pos (collidable + sprites)
    """
    if piece_blocked is None:
        piece_blocked = player_blocked
    if player_absolute is None:
        player_absolute = frozenset()
    piece_pos = (player_start[0] + carry_offset[0], player_start[1] + carry_offset[1])
    if piece_pos in goal_set:
        return [player_start]
    visited = {player_start}
    queue = deque([(player_start, [player_start])])
    while queue:
        pos, path = queue.popleft()
        cur_piece = (pos[0] + carry_offset[0], pos[1] + carry_offset[1])
        for d in DIRS:
            np_ = (pos[0] + d[0], pos[1] + d[1])
            np_piece = (np_[0] + carry_offset[0], np_[1] + carry_offset[1])
            if np_ not in visited:
                if np_ in player_absolute:
                    continue
                np_ok = (np_ not in player_blocked) or (np_ == cur_piece)
                piece_ok = (np_piece not in piece_blocked) or (np_piece == pos)
                if np_ok and piece_ok:
                    visited.add(np_)
                    new_path = path + [np_]
                    if np_piece in goal_set:
                        return new_path
                    queue.append((np_, new_path))
    return None


def path_to_actions(positions):
    return [ACT_FOR_DIR[(positions[i][0] - positions[i-1][0],
                         positions[i][1] - positions[i-1][1])]
            for i in range(1, len(positions))]


def plan_delivery(player_pos, piece_pos, target_pos, blocked):
    best = None
    best_cost = float('inf')
    for d in DIRS:
        approach = (piece_pos[0] - d[0], piece_pos[1] - d[1])
        if approach in blocked or approach == piece_pos:
            continue
        walk = bfs_walk(player_pos, {approach}, blocked | {piece_pos})
        if walk is None:
            continue
        walk_acts = path_to_actions(walk)
        face_act = ACT_FOR_DIR[d]
        pre_grab = walk_acts + ([face_act] if not walk_acts or walk_acts[-1] != face_act else [])
        grab_acts = pre_grab + [5]
        carry = bfs_carry(approach, d, {target_pos}, blocked)
        if carry is None:
            continue
        carry_acts = path_to_actions(carry)
        all_acts = grab_acts + carry_acts + [5]
        if len(all_acts) < best_cost:
            best = (all_acts, carry[-1], len(all_acts))
            best_cost = len(all_acts)
    return best


def solve_simple(cfg):
    walls = cfg["walls"]
    pieces = cfg["pieces"][:]
    targets = list(cfg["targets"])
    player = cfg["player"]
    n = len(pieces)
    best_solution = None
    best_cost = float('inf')

    for target_perm in permutations(range(len(targets)), n):
        assigned = [targets[i] for i in target_perm]
        for piece_order in permutations(range(n)):
            total_acts = []
            cur_player = player
            placed = set()
            remaining = dict(enumerate(pieces))
            failed = False
            for pi in piece_order:
                blocked = set(walls)
                for j, pos in remaining.items():
                    if j != pi:
                        blocked.add(pos)
                for pos in placed:
                    blocked.add(pos)
                result = plan_delivery(cur_player, remaining[pi], assigned[pi], blocked)
                if result is None:
                    failed = True
                    break
                acts, final_pos, _ = result
                total_acts.extend(acts)
                cur_player = final_pos
                del remaining[pi]
                placed.add(assigned[pi])
            if failed or len(total_acts) >= best_cost:
                continue
            best_solution = total_acts
            best_cost = len(total_acts)
    if best_solution:
        print(f"  Decomposition: {best_cost} actions")
    return best_solution


def solve_with_engine(level_idx, max_steps):
    """Engine-based greedy solver for NPC levels."""
    g = Wa30()
    g.set_level(level_idx)
    init_level = g._current_level_index
    cfg = extract_level(g)
    actions = []

    for step_num in range(max_steps):
        if g._current_level_index > init_level or g._state.name == "WIN":
            return actions
        if g._state.name in ("LOSE", "GAME_OVER"):
            return None

        level = g.current_level
        player = level.get_sprites_by_tag("wbmdvjhthc")[0]
        pieces = level.get_sprites_by_tag("geezpjgiyd")
        enemies = level.get_sprites_by_tag("ysysltqlke")
        px, py, rot = player.x, player.y, player.rotation

        carrying = player in g.nsevyuople

        # Count how many pieces still need placement
        unplaced = [p for p in pieces if not (g.shbxbhnhjc((p.x, p.y)) and p not in g.zmqreragji)]
        if not unplaced:
            # All placed — wait for any lingering transitions
            actions.append(1)
            engine_step(g, 1)
            continue

        act = None

        if carrying:
            carried = g.nsevyuople[player]
            carry_off = (carried.x - px, carried.y - py)

            free_targets = set(cfg["targets"])
            for p in pieces:
                if g.shbxbhnhjc((p.x, p.y)) and p not in g.zmqreragji:
                    free_targets.discard((p.x, p.y))

            player_blocked = set(cfg["walls"])
            piece_blocked = set(cfg["piece_walls"])
            for p in pieces:
                if p is not carried:
                    player_blocked.add((p.x, p.y))
                    piece_blocked.add((p.x, p.y))
            for h in level.get_sprites_by_tag("kdweefinfi"):
                player_blocked.add((h.x, h.y))
                piece_blocked.add((h.x, h.y))
            for e in enemies:
                player_blocked.add((e.x, e.y))
                piece_blocked.add((e.x, e.y))

            carry = bfs_carry((px, py), carry_off, free_targets, player_blocked, piece_blocked, cfg["absolute_walls"])
            if carry and len(carry) > 1:
                dx = carry[1][0] - carry[0][0]
                dy = carry[1][1] - carry[0][1]
                act = ACT_FOR_DIR[(dx, dy)]
            elif carry and len(carry) == 1:
                act = 5  # At target, drop
            else:
                # Can't reach target — get piece as close to target as possible
                best_drop = None
                best_tdist = float('inf')
                visited_carry = {(px, py)}
                bfs_q = deque([(px, py)])
                while bfs_q:
                    cpos = bfs_q.popleft()
                    cpiece = (cpos[0] + carry_off[0], cpos[1] + carry_off[1])
                    for t in free_targets:
                        tdist = abs(cpiece[0] - t[0]) + abs(cpiece[1] - t[1])
                        if tdist < best_tdist:
                            best_tdist = tdist
                            best_drop = cpos
                    for dd in DIRS:
                        np_ = (cpos[0] + dd[0], cpos[1] + dd[1])
                        np_p = (np_[0] + carry_off[0], np_[1] + carry_off[1])
                        if np_ not in visited_carry and np_ not in cfg["absolute_walls"]:
                            cp = (cpos[0] + carry_off[0], cpos[1] + carry_off[1])
                            np_ok = (np_ not in player_blocked) or (np_ == cp)
                            p_ok = (np_p not in piece_blocked) or (np_p == cpos)
                            if np_ok and p_ok:
                                visited_carry.add(np_)
                                bfs_q.append(np_)

                if best_drop and best_drop != (px, py):
                    goal_piece = (best_drop[0] + carry_off[0], best_drop[1] + carry_off[1])
                    carry2 = bfs_carry((px, py), carry_off, {goal_piece}, player_blocked, piece_blocked, cfg["absolute_walls"])
                    if carry2 and len(carry2) > 1:
                        dx = carry2[1][0] - carry2[0][0]
                        dy = carry2[1][1] - carry2[0][1]
                        act = ACT_FOR_DIR[(dx, dy)]
                    else:
                        act = 5
                else:
                    act = 5
        else:
            # Not carrying — find best piece+direction to grab
            blocked = set(cfg["walls"])
            for p in pieces:
                blocked.add((p.x, p.y))
            for h in level.get_sprites_by_tag("kdweefinfi"):
                blocked.add((h.x, h.y))
            for e in enemies:
                blocked.add((e.x, e.y))
            blocked.discard((px, py))

            # Check for adjacent enemy to kill
            face = {0: (px, py-STEP), 180: (px, py+STEP), 90: (px+STEP, py), 270: (px-STEP, py)}[rot]
            for e in enemies:
                if (e.x, e.y) == face:
                    act = 5
                    break

            if act is None:
                # Build free targets set
                free_targets = set(cfg["targets"])
                for p in pieces:
                    if g.shbxbhnhjc((p.x, p.y)) and p not in g.zmqreragji:
                        free_targets.discard((p.x, p.y))

                player_bl = set(cfg["walls"])
                piece_bl = set(cfg["piece_walls"])
                for p in pieces:
                    player_bl.add((p.x, p.y))
                    piece_bl.add((p.x, p.y))
                for h in level.get_sprites_by_tag("kdweefinfi"):
                    player_bl.add((h.x, h.y))
                    piece_bl.add((h.x, h.y))

                best_score = float('inf')
                best_act_val = None

                rot_map = {(0,-STEP):0,(0,STEP):180,(-STEP,0):270,(STEP,0):90}

                # Avoid pieces the helper is closer to (let helper handle them)
                helper_pos = None
                for hh in level.get_sprites_by_tag("kdweefinfi"):
                    if hh not in g.nsevyuople:
                        helper_pos = (hh.x, hh.y)
                        break

                for p in unplaced:
                    if p in g.zmqreragji and g.zmqreragji[p] is not player:
                        if "kdweefinfi" in g.zmqreragji[p].tags:
                            continue
                    pp = (p.x, p.y)

                    # Skip if helper is closer and not busy
                    if helper_pos and cfg["n_helpers"] > 0:
                        h_dist = abs(helper_pos[0]-pp[0]) + abs(helper_pos[1]-pp[1])
                        p_dist = abs(px-pp[0]) + abs(py-pp[1])
                        if h_dist < p_dist and len(unplaced) > 2:
                            continue

                    for d in DIRS:
                        approach = (pp[0] - d[0], pp[1] - d[1])
                        if approach in blocked and approach != (px, py):
                            continue

                        carry_bl_p = set(piece_bl); carry_bl_p.discard(pp)
                        carry_bl_pl = set(player_bl); carry_bl_pl.discard(pp)

                        # Try direct delivery to target
                        carry = bfs_carry(approach, d, free_targets, carry_bl_pl, carry_bl_p, cfg["absolute_walls"])
                        if carry is not None:
                            carry_cost = len(carry)
                        else:
                            # Fallback: deposit as close to targets as possible
                            # Only useful if helpers exist to finish delivery
                            if cfg["n_helpers"] == 0:
                                continue
                            # Find closest carry position to any target
                            best_dep = None
                            best_dep_dist = float('inf')
                            vis = {approach}
                            dep_q = deque([approach])
                            while dep_q:
                                cp = dep_q.popleft()
                                cpc = (cp[0]+d[0], cp[1]+d[1])
                                for t in free_targets:
                                    td = abs(cpc[0]-t[0]) + abs(cpc[1]-t[1])
                                    if td < best_dep_dist:
                                        best_dep_dist = td
                                        best_dep = cp
                                for dd in DIRS:
                                    np_ = (cp[0]+dd[0], cp[1]+dd[1])
                                    np_p = (np_[0]+d[0], np_[1]+d[1])
                                    if np_ not in vis and np_ not in cfg["absolute_walls"]:
                                        cur_p = (cp[0]+d[0], cp[1]+d[1])
                                        ok1 = (np_ not in carry_bl_pl) or (np_ == cur_p)
                                        ok2 = (np_p not in carry_bl_p) or (np_p == cp)
                                        if ok1 and ok2:
                                            vis.add(np_)
                                            dep_q.append(np_)
                            orig_min_dist = min(abs(pp[0]-t[0])+abs(pp[1]-t[1]) for t in free_targets)
                            if best_dep is None or best_dep_dist >= orig_min_dist:
                                continue
                            # Compute cost to deposit
                            dep_piece = (best_dep[0]+d[0], best_dep[1]+d[1])
                            carry = bfs_carry(approach, d, {dep_piece}, carry_bl_pl, carry_bl_p, cfg["absolute_walls"])
                            if carry is None:
                                continue
                            carry_cost = len(carry) + 5  # Penalty for needing helper

                        if approach == (px, py):
                            rot_for_d = rot_map[d]
                            if rot == rot_for_d:
                                act = 5
                                best_act_val = None
                                break
                            else:
                                total = 1 + 1 + carry_cost + 1
                                if total < best_score:
                                    best_score = total
                                    best_act_val = ACT_FOR_DIR[d]
                        else:
                            walk = bfs_walk((px, py), {approach}, blocked)
                            if walk is None:
                                continue
                            walk_cost = len(walk) - 1
                            total = walk_cost + 2 + carry_cost + 1
                            if total < best_score:
                                best_score = total
                                dx = walk[1][0] - walk[0][0]
                                dy = walk[1][1] - walk[0][1]
                                best_act_val = ACT_FOR_DIR[(dx, dy)]
                    if act == 5:
                        break

                if act is None and best_act_val is not None:
                    act = best_act_val

            if act is None:
                # No deliverable piece — try approaching enemies
                for e in enemies:
                    ep = (e.x, e.y)
                    approaches = set()
                    for d in DIRS:
                        ap = (ep[0] - d[0], ep[1] - d[1])
                        if ap not in blocked or ap == (px, py):
                            approaches.add(ap)
                    if approaches:
                        walk = bfs_walk((px, py), approaches, blocked)
                        if walk and len(walk) > 1:
                            dx = walk[1][0] - walk[0][0]
                            dy = walk[1][1] - walk[0][1]
                            act = ACT_FOR_DIR[(dx, dy)]
                            break

            if act is None:
                act = 1  # Idle

        actions.append(act)
        engine_step(g, act)

    if g._current_level_index > init_level or g._state.name == "WIN":
        return actions
    return None


def verify_local(all_actions):
    g = Wa30()
    g.set_level(0)
    levels_completed = 0
    for i, a in enumerate(all_actions):
        state = engine_step(g, a)
        if g._current_level_index > levels_completed:
            levels_completed = g._current_level_index
            print(f"  Level {levels_completed} done at action {i+1}")
        if state == "WIN":
            print(f"  GAME WIN at action {i+1}/{len(all_actions)}, levels={levels_completed}")
            return True
        if state in ("LOSE", "GAME_OVER"):
            print(f"  {state} at action {i+1}")
            return False
    print(f"  End: state={g._state.name}, levels={levels_completed}")
    return g._state.name == "WIN"


def solve_all():
    baselines = [71, 119, 183, 98, 368, 68, 79, 442, 415]
    all_actions = []
    solutions = {}
    g = Wa30()

    for level_idx in range(9):
        g.set_level(level_idx)
        cfg = extract_level(g)
        print(f"\n=== Level {level_idx + 1} ===")
        print(f"  Player: {cfg['player']}, {len(cfg['pieces'])} pieces")
        print(f"  {cfg['n_helpers']} helpers, {cfg['n_enemies']} enemies")
        print(f"  Targets: {sorted(cfg['targets'])}")
        print(f"  Step limit: {cfg['step_limit']}, baseline: {baselines[level_idx]}")

        has_npcs = cfg['n_helpers'] > 0 or cfg['n_enemies'] > 0
        if not has_npcs:
            solution = solve_simple(cfg)
        else:
            solution = solve_with_engine(level_idx, cfg['step_limit'])

        if solution is None:
            print(f"  FAILED level {level_idx + 1}")
            break

        solutions[level_idx + 1] = solution
        all_actions.extend(solution)
        print(f"  L{level_idx + 1}: {len(solution)} actions (baseline {baselines[level_idx]})")

    print(f"\n=== Summary ===")
    total = 0
    for lvl, sol in sorted(solutions.items()):
        print(f"  L{lvl}: {len(sol)} (baseline {baselines[lvl-1]})")
        total += len(sol)
    print(f"  Total: {total}")

    if solutions:
        print(f"\nVerifying...")
        verify_local(all_actions)
    return all_actions, solutions


if __name__ == "__main__":
    solve_all()
