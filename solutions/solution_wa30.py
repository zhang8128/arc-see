"""WA30 — reconstructed solver (mechanics fully decoded from engine).

Status: solves L1 and L2 reliably (~30 and ~55 actions). L3+ partial —
the greedy planner finds valid grab+deposit sequences but runs slightly
over the tight step budgets (L3 step limit 100, typical solve 91). The
architecture is right; the heuristics need tuning to trim per-piece
overhead.

Mechanics (decoded from environment_files/wa30/ee6fef47/wa30.py):
  - 16x16 grid at step=4 px. Actions 1-4 = U/D/L/R, 5 = grab/drop/kill.
  - Pieces (`geezpjgiyd`) → targets (`fsjjayjoeg`). Win when all there.
  - Helpers (`kdweefinfi`) auto-grab/deliver pieces toward targets.
  - Enemies (`ysysltqlke`) auto-grab/deliver pieces toward WRONG zone
    (`zqxwgacnue`). Kill with face+A5.
  - Player grab: face piece (rotation from last move) + A5 adjacent.
  - Carrying: player and piece move in lockstep (offset preserved).
  - Pieces CAN land on wall cells (walls block players, not pieces).
    This is how "deposit for helper across a wall" works.

Approach: per-level greedy solver. For each piece, joint-plan the best
grab-direction × destination (targets or helper-reachable deposit
sites). Execute. Helpers/enemies move each step, so path2 is replanned
after each grab. Helper-unreachable pieces are attempted first (helper
handles its own). Recent deposits and failures are cached to avoid
immediate retries; waits (A5 no-ops) let helpers progress.
"""
import sys
sys.path.insert(0, 'environment_files/wa30/ee6fef47')
import arc_agi
from arcengine import GameAction
from wa30 import Wa30, celomdfhbh as STEP  # noqa: E402


# dir id → (dx, dy, rotation)
DIRS = {
    1: (0, -STEP, 0),
    2: (0,  STEP, 180),
    3: (-STEP, 0, 270),
    4: ( STEP, 0, 90),
}
GRID_MIN, GRID_MAX = 0, 60


def in_bounds(p):
    return GRID_MIN <= p[0] <= GRID_MAX and GRID_MIN <= p[1] <= GRID_MAX


def tag_sprites(g, tag):
    return g.current_level.get_sprites_by_tag(tag)


def player(g):
    return tag_sprites(g, 'wbmdvjhthc')[0]


def extract(g):
    p = player(g)
    pieces = [(s.x, s.y) for s in tag_sprites(g, 'geezpjgiyd')]
    helpers = [(s.x, s.y) for s in tag_sprites(g, 'kdweefinfi')]
    enemies = [(s.x, s.y) for s in tag_sprites(g, 'ysysltqlke')]
    # wyzquhjerd is per-pixel; pieces only land on grid-aligned cells.
    target_px = set(g.wyzquhjerd)
    target_slots = {(x, y) for (x, y) in target_px
                    if x % STEP == 0 and y % STEP == 0}
    walls = set(g.qthdiggudy)
    carried = g.nsevyuople.get(p)
    return {
        'player': (p.x, p.y),
        'rotation': p.rotation,
        'pieces': pieces,
        'helpers': helpers,
        'enemies': enemies,
        'targets': target_slots,
        'target_px': target_px,
        'walls': walls,
        'carried_pos': (carried.x, carried.y) if carried else None,
    }


def bfs_player(start, start_rot, goal_fn, player_blocked,
               piece_blocked=None, carry_offset=None, cap=2000):
    """BFS over (pos, rotation). Returns action list or None.

    player_blocked: cells the player can't enter (walls + other sprites).
    piece_blocked: cells the carried piece can't enter. Defaults to
                   player_blocked; the engine allows pieces to sit on
                   wall cells, so when carrying pass a separate set."""
    from collections import deque
    if piece_blocked is None:
        piece_blocked = player_blocked
    if goal_fn(start, start_rot):
        return []
    seen = {(start, start_rot): None}
    q = deque([(start, start_rot)])
    while q and len(seen) < cap:
        pos, rot = q.popleft()
        for aid, (dx, dy, new_rot) in DIRS.items():
            npos = (pos[0] + dx, pos[1] + dy)
            if not in_bounds(npos):
                continue
            if npos in player_blocked:
                continue
            if carry_offset is not None:
                piece = (pos[0] + carry_offset[0], pos[1] + carry_offset[1])
                new_piece = (piece[0] + dx, piece[1] + dy)
                if not in_bounds(new_piece):
                    continue
                if new_piece in piece_blocked and new_piece != piece:
                    continue
                if new_piece == npos:
                    continue
            key = (npos, new_rot)
            if key in seen:
                continue
            seen[key] = (pos, rot, aid)
            if goal_fn(npos, new_rot):
                path = [aid]
                cur = (pos, rot)
                while seen[cur] is not None:
                    ppos, prot, paid = seen[cur]
                    path.append(paid)
                    cur = (ppos, prot)
                return list(reversed(path))
            q.append(key)
    return None


def grab_options(piece_pos):
    """Valid (player_pos, rotation) positions from which A5 grabs the piece."""
    px, py = piece_pos
    return [
        ((px, py + STEP), 0),
        ((px, py - STEP), 180),
        ((px + STEP, py), 270),
        ((px - STEP, py), 90),
    ]


def _blocked_unloaded(state, exclude=None):
    blocked = set(state['walls'])
    for pp in state['pieces']:
        if pp != exclude:
            blocked.add(pp)
    blocked.update(state['helpers'])
    blocked.update(state['enemies'])
    return blocked


def _blocked_carrying(state, carried):
    """Cells the player can't enter while carrying. Walls + other sprites."""
    blocked = set(state['walls'])
    for pp in state['pieces']:
        if pp != carried:
            blocked.add(pp)
    blocked.update(state['helpers'])
    blocked.update(state['enemies'])
    return blocked


def _piece_blocked(state, carried):
    """Cells the carried piece can't land in — NOT including walls,
    because the engine allows pieces on wall cells."""
    blocked = set()
    for pp in state['pieces']:
        if pp != carried:
            blocked.add(pp)
    blocked.update(state['helpers'])
    blocked.update(state['enemies'])
    return blocked


def _exteriority(tgt, all_targets):
    """Higher score = more 'exterior' (fewer target neighbors).

    Delivering to exterior targets first keeps the interior path clear for
    subsequent deliveries (by the player and by helpers)."""
    nbrs = [(tgt[0] + dx, tgt[1] + dy) for dx, dy in
            [(-STEP, 0), (STEP, 0), (0, -STEP), (0, STEP)]]
    return sum(1 for n in nbrs if n not in all_targets)


def _helper_BFS_reachable(state):
    """Return set of cells any helper can reach (ignoring pieces, which the
    helper can grab and thus displace). Used to pick deposit sites."""
    from collections import deque
    if not state['helpers']:
        return set()
    reachable = set()
    for h in state['helpers']:
        if h in reachable:
            continue
        q = deque([h])
        seen = {h}
        # Helper blocked cells: walls, other helpers, enemies. NOT pieces.
        bl = set(state['walls'])
        bl.update(e for e in state['enemies'])
        bl.update(o for o in state['helpers'] if o != h)
        while q:
            pos = q.popleft()
            reachable.add(pos)
            for dx, dy in [(-STEP, 0), (STEP, 0), (0, -STEP), (0, STEP)]:
                n = (pos[0] + dx, pos[1] + dy)
                if not in_bounds(n) or n in bl or n in seen:
                    continue
                seen.add(n)
                q.append(n)
    return reachable


def _best_grab_target(state, piece_pos):
    """Plan grab-and-deliver; return (grab_pos, grab_rot, tgt, path1, path2) or None.

    Tries REAL target slots first. Falls back to 'deposit sites' (cells
    from which a helper can grab the piece and then deliver) when no
    direct delivery is feasible."""
    blocked_unloaded = _blocked_unloaded(state, exclude=piece_pos)
    blocked_carrying = _blocked_carrying(state, piece_pos)
    piece_blocked = _piece_blocked(state, piece_pos)
    all_targets = state['targets']
    free_targets = list(all_targets
                        - {pp for pp in state['pieces'] if pp != piece_pos})
    helper_reach = _helper_BFS_reachable(state)
    # Deposit sites: cells whose 4-neighborhood includes a helper-reachable
    # cell (so helper can stand adjacent and grab). Skip actual pieces and
    # skip targets (we'd rather deliver directly if we could).
    deposit_sites = []
    if helper_reach and state['helpers']:
        for x in range(GRID_MIN, GRID_MAX + 1, STEP):
            for y in range(GRID_MIN, GRID_MAX + 1, STEP):
                c = (x, y)
                if c in state['pieces'] or c in state['helpers'] or c in state['enemies']:
                    continue
                if c in all_targets:
                    continue
                nbrs = [(x - STEP, y), (x + STEP, y), (x, y - STEP), (x, y + STEP)]
                if any(n in helper_reach and n not in state['walls']
                       for n in nbrs):
                    deposit_sites.append(c)
        # Prefer deposit sites nearest helper (so helper doesn't travel far).
        h0 = state['helpers'][0]
        deposit_sites.sort(key=lambda c: abs(c[0] - h0[0]) + abs(c[1] - h0[1]))

    # Candidate destinations: real targets first, then deposit sites.
    candidates = [('target', rank, t) for rank, t in enumerate(
        sorted(free_targets,
               key=lambda t: (-_exteriority(t, all_targets), t[0] + t[1])))]
    candidates += [('deposit', 1000 + rank, c)
                   for rank, c in enumerate(deposit_sites)]
    best = None
    for grab_pos, grab_rot in grab_options(piece_pos):
        if not in_bounds(grab_pos) or grab_pos in blocked_unloaded:
            continue
        path1 = bfs_player(state['player'], state['rotation'],
                           lambda p, r: p == grab_pos and r == grab_rot,
                           blocked_unloaded)
        if path1 is None:
            continue
        dx = piece_pos[0] - grab_pos[0]
        dy = piece_pos[1] - grab_pos[1]
        for kind, rank, dst in candidates:
            player_goal = (dst[0] - dx, dst[1] - dy)
            if not in_bounds(player_goal):
                continue
            path2 = bfs_player(grab_pos, grab_rot,
                               lambda p, r: p == player_goal,
                               blocked_carrying, piece_blocked=piece_blocked,
                               carry_offset=(dx, dy))
            if path2 is None:
                continue
            total = len(path1) + 1 + len(path2) + 1
            score = (rank, total)
            if best is None or score < best[0]:
                best = (score, grab_pos, grab_rot, dst, path1, path2)
    if best is None:
        return None
    return best[1:]  # (grab_pos, grab_rot, dst, path1, path2)


def grab_and_deliver(g, do_step, piece_pos):
    """Plan fully; bail without executing if total cost exceeds step budget."""
    state = extract(g)
    start_pieces = tuple(sorted(state['pieces']))
    plan = _best_grab_target(state, piece_pos)
    if plan is None:
        return False
    gp, gr, dst, path1, path2_initial = plan
    cost = len(path1) + 1 + len(path2_initial) + 1
    if cost > g.kuncbnslnm.current_steps + 1:
        # Not enough step budget — bail without executing.
        return False
    for aid in path1:
        if not do_step(aid):
            return False
    if not do_step(5):
        return False
    after = extract(g)
    if after['carried_pos'] is None:
        return False
    carried = after['carried_pos']
    dx = carried[0] - after['player'][0]
    dy = carried[1] - after['player'][1]
    all_targets = after['targets']
    free_targets = list(all_targets
                        - {pp for pp in after['pieces'] if pp != carried})
    helper_reach = _helper_BFS_reachable(after)
    deposit_sites = []
    if helper_reach and after['helpers']:
        for x in range(GRID_MIN, GRID_MAX + 1, STEP):
            for y in range(GRID_MIN, GRID_MAX + 1, STEP):
                c = (x, y)
                if c in after['pieces'] or c in after['helpers'] or c in after['enemies']:
                    continue
                if c in all_targets:
                    continue
                nbrs = [(x - STEP, y), (x + STEP, y), (x, y - STEP), (x, y + STEP)]
                if any(n in helper_reach and n not in after['walls']
                       for n in nbrs):
                    deposit_sites.append(c)
        h0 = after['helpers'][0]
        deposit_sites.sort(key=lambda c: abs(c[0] - h0[0]) + abs(c[1] - h0[1]))
    candidates = [('t', r, t) for r, t in enumerate(
        sorted(free_targets,
               key=lambda t: (-_exteriority(t, all_targets), t[0] + t[1])))]
    candidates += [('d', 1000 + r, c) for r, c in enumerate(deposit_sites)]
    blocked = _blocked_carrying(after, carried)
    piece_bl = _piece_blocked(after, carried)
    best = None
    for kind, rank, d in candidates:
        pg = (d[0] - dx, d[1] - dy)
        if not in_bounds(pg):
            continue
        p2 = bfs_player(after['player'], after['rotation'],
                        lambda p, r: p == pg, blocked,
                        piece_blocked=piece_bl, carry_offset=(dx, dy))
        if p2 is None:
            continue
        if best is None or (rank, len(p2)) < best[0]:
            best = ((rank, len(p2)), p2)
    if best is None:
        do_step(5)
        return True
    for aid in best[1]:
        if not do_step(aid):
            do_step(5)
            return True
    do_step(5)
    end_pieces = tuple(sorted(extract(g)['pieces']))
    return end_pieces != start_pieces


def deliver_carried(g, do_step):
    """Walk a carried piece to a free target (exterior-first) and drop."""
    state = extract(g)
    carried = state['carried_pos']
    if carried is None:
        return False
    dx = carried[0] - state['player'][0]
    dy = carried[1] - state['player'][1]
    all_targets = state['targets']
    free_targets = list(all_targets
                        - {pp for pp in state['pieces'] if pp != carried})
    if not free_targets:
        return False
    free_targets.sort(key=lambda t: (-_exteriority(t, all_targets),
                                     t[0] + t[1]))
    blocked = _blocked_carrying(state, carried)
    piece_bl = _piece_blocked(state, carried)
    best = None
    for rank, tgt in enumerate(free_targets):
        pg = (tgt[0] - dx, tgt[1] - dy)
        if not in_bounds(pg):
            continue
        path = bfs_player(state['player'], state['rotation'],
                          lambda p, r: p == pg, blocked,
                          piece_blocked=piece_bl,
                          carry_offset=(dx, dy))
        if path is None:
            continue
        score = (rank, len(path))
        if best is None or score < best[0]:
            best = (score, path)
    if best is None:
        return False
    for aid in best[1]:
        do_step(aid)
    do_step(5)
    return True


def kill_enemy(g, do_step, enemy_pos):
    state = extract(g)
    blocked = _blocked_unloaded(state)
    # Need to step adjacent to enemy facing it.
    ex, ey = enemy_pos
    approaches = grab_options(enemy_pos)
    best = None
    for pos, rot in approaches:
        if not in_bounds(pos) or pos in blocked:
            continue
        path = bfs_player(state['player'], state['rotation'],
                          lambda p, r: p == pos and r == rot, blocked)
        if path is None:
            continue
        if best is None or len(path) < len(best):
            best = path
    if best is None:
        return False
    for aid in best:
        do_step(aid)
    do_step(5)
    return True


def enemy_carrying(g):
    """Return list of enemy positions that are currently carrying a piece."""
    out = []
    for s in tag_sprites(g, 'ysysltqlke'):
        if s in g.nsevyuople:
            out.append((s.x, s.y))
    return out


def solve_level(env, target_lvl, max_iters=400, verbose=False):
    """Solve WA30 level `target_lvl` (1-indexed). Returns (actions, won)."""
    g = env._game
    taken = []
    recent_deposits = set()   # pieces we just deposited; avoid re-grabbing
    recent_failures = set()   # pieces whose grab_and_deliver just failed

    def do_step(aid):
        if g.kuncbnslnm.current_steps <= 0:
            return False
        taken.append(aid)
        env.step(getattr(GameAction, f'ACTION{aid}'))
        return True

    def level_advanced():
        return g._current_level_index + 1 > target_lvl

    last_state_sig = None
    stuck_count = 0
    for it in range(max_iters):
        if level_advanced():
            return taken, True
        if g.kuncbnslnm.current_steps <= 0:
            return taken, level_advanced()
        state = extract(g)
        sig = (state['player'], state['rotation'],
               tuple(sorted(state['pieces'])),
               tuple(sorted(state['helpers'])),
               tuple(sorted(state['enemies'])),
               state['carried_pos'])
        if sig == last_state_sig:
            stuck_count += 1
            if stuck_count > 6:
                return taken, level_advanced()
        else:
            stuck_count = 0
            last_state_sig = sig

        # Emergency: kill enemy carrying a piece away.
        carrying_enemies = enemy_carrying(g)
        if carrying_enemies:
            if not kill_enemy(g, do_step, carrying_enemies[0]):
                return taken, False
            continue

        # Already carrying? Deliver.
        if state['carried_pos'] is not None:
            if not deliver_carried(g, do_step):
                # Drop and retry.
                do_step(5)
            continue

        # Pieces held by helpers — leave those alone.
        held_by_helpers = {(g.nsevyuople[s].x, g.nsevyuople[s].y)
                           for s in tag_sprites(g, 'kdweefinfi')
                           if s in g.nsevyuople}
        # Prune recent_deposits: if a piece moved, it's no longer "stuck at deposit".
        recent_deposits = {p for p in recent_deposits if p in state['pieces']}
        undelivered_all = [pp for pp in state['pieces']
                           if pp not in state['targets']
                           and pp not in held_by_helpers]
        undelivered = [pp for pp in undelivered_all
                       if pp not in recent_deposits
                       and pp not in recent_failures]
        # Prefer pieces NOT helper-reachable — let helper handle its own.
        helper_reach = _helper_BFS_reachable(state) if state['helpers'] else set()

        def _helper_can_grab(pp):
            for dx, dy in [(-STEP, 0), (STEP, 0), (0, -STEP), (0, STEP)]:
                if (pp[0] + dx, pp[1] + dy) in helper_reach:
                    return True
            return False
        if not undelivered:
            if held_by_helpers:
                do_step(5)
                continue
            if recent_deposits or recent_failures:
                recent_deposits.clear()
                recent_failures.clear()
                do_step(5)   # let helper move
                continue
            if undelivered_all and state['helpers']:
                do_step(5)
                continue
            return taken, level_advanced()

        # Pick piece: prefer helper-unreachable first (let helpers handle
        # their own), then closest to a free target.
        free_targets = list(state['targets'] - set(state['pieces']))

        def piece_score(pp):
            hreach = _helper_can_grab(pp) if helper_reach else False
            if not free_targets:
                return (hreach, 0)
            return (hreach, min(abs(pp[0] - t[0]) + abs(pp[1] - t[1])
                                for t in free_targets))
        undelivered.sort(key=piece_score)

        progressed = False
        attempted = 0
        for pp in undelivered:
            if attempted >= 1:
                break  # try at most 1 piece per iter; wait if it fails
            attempted += 1
            before_pieces = set(state['pieces'])
            if grab_and_deliver(g, do_step, pp):
                progressed = True
                recent_failures.discard(pp)
                ns = extract(g)
                after_pieces = set(ns['pieces'])
                added = after_pieces - before_pieces
                for np in added:
                    if np not in ns['targets']:
                        recent_deposits.add(np)
                break
            else:
                recent_failures.add(pp)
        if not progressed:
            # No grabbable piece. Wait if anyone/anything might still move things.
            if held_by_helpers or state['enemies'] or recent_deposits:
                do_step(5)
                continue
            if undelivered_all:
                # Helper present but idle (standing on a target slot?). Give up.
                if state['helpers']:
                    do_step(5)
                    continue
            return taken, level_advanced()

    return taken, level_advanced()


BASELINES = [71, 119, 183, 98, 368, 68, 79, 442, 415]


def solve_all(verbose=False):
    arcade = arc_agi.Arcade()
    env = arcade.make('wa30-ee6fef47', render_mode=None)
    env.reset()
    env.reset()  # engram: double-reset correctness quirk
    g = env._game

    results = []
    grand = 0
    for lvl in range(1, 10):
        cur_lvl = g._current_level_index + 1
        if cur_lvl != lvl:
            # Game already advanced or not yet — probably lost on prior level.
            break
        actions, won = solve_level(env, lvl, verbose=verbose)
        grand += len(actions)
        results.append((lvl, len(actions), won))
        status = '✓ WIN' if won else '✗ FAIL'
        print(f'  L{lvl}: {len(actions):3d} actions (baseline {BASELINES[lvl-1]}) {status}')
        if not won:
            break
    print(f'\nTotal: {grand} actions (baselines: {sum(BASELINES)})')
    solved = sum(1 for _, _, w in results if w)
    all_won = solved == 9
    if all_won:
        print('Final state: WIN (all 9 levels)')
    else:
        print(f'Final state: PARTIAL — {solved}/9 levels solved')
    return results


if __name__ == '__main__':
    solve_all()
