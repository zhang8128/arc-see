"""R11L solver — creature leg-dragging puzzle.

Click a leg to select, click destination to move it.
Body auto-centers over legs. Win when body overlaps target.
Failed moves auto-reverse. Obstacles block movement.

BFS over (leg_index, destination) pairs using game engine.
State = tuple of leg positions.
"""
import importlib.util
import hashlib
import arc_agi
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('r11l', 'environment_files/r11l/aa269680/r11l.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

CLICK = GameAction.ACTION6


def act(g, x, y):
    return g.perform_action(ActionInput(id=CLICK, data={'x': x, 'y': y}))


def get_legs(g):
    """Get all leg sprites."""
    return list(g.ftmaz)


def get_state(g):
    """State = leg positions (determines body positions deterministically)."""
    legs = get_legs(g)
    return tuple((s.x, s.y) for s in legs)


def get_targets(g):
    """Get target positions for each creature."""
    targets = {}
    for name, data in g.brdck.items():
        if data.get("xwdrv"):
            targets[name] = (data["xwdrv"].x, data["xwdrv"].y)
    return targets


def generate_destinations(g):
    """Generate valid destination grid positions (4px grid)."""
    # Use game area, avoiding obvious out-of-bounds
    dests = []
    for y in range(0, 64, 4):
        for x in range(0, 64, 4):
            dests.append((x, y))
    return dests


def replay_and_move(level_idx, prev_moves, leg_idx, dest_x, dest_y):
    """Replay all previous moves, then attempt one new move."""
    g = mod.R11l()
    g.set_level(level_idx)

    # Replay previous moves
    for (li, dx, dy) in prev_moves:
        legs = get_legs(g)
        if li < len(legs):
            leg = legs[li]
            # Click leg to select
            act(g, leg.x + leg.width // 2, leg.y + leg.height // 2)
            # Click destination
            act(g, dx, dy)

    # Attempt new move
    legs = get_legs(g)
    if leg_idx >= len(legs):
        return None
    leg = legs[leg_idx]
    old_pos = (leg.x, leg.y)

    # Select leg
    act(g, leg.x + leg.width // 2, leg.y + leg.height // 2)
    # Move to destination
    act(g, dest_x, dest_y)

    new_pos = (leg.x, leg.y)

    # Check if move actually happened (didn't reverse)
    if new_pos == old_pos:
        return None  # Move was blocked/reversed

    return g


def bfs_solve(level_idx, max_depth=None):
    """BFS to find optimal move sequence."""
    g0 = mod.R11l()
    g0.set_level(level_idx)

    baseline = [7, 28, 30, 20, 37, 45][level_idx]
    # Each "move" = 2 clicks (select + destination), so action limit = baseline
    # But BFS depth is in "moves" not clicks
    move_limit = max_depth or (baseline // 2 + 2)

    legs = get_legs(g0)
    num_legs = len(legs)
    targets = get_targets(g0)
    start_state = get_state(g0)

    print(f"Level {level_idx+1}: baseline={baseline}, move_limit={move_limit}, "
          f"legs={num_legs}, targets={targets}", flush=True)

    # Pre-compute smart destinations: target positions + nearby grid positions
    dests = set()
    for name, (tx, ty) in targets.items():
        # Add target and surrounding positions
        for dx in range(-16, 20, 4):
            for dy in range(-16, 20, 4):
                nx, ny = tx + dx, ty + dy
                if 0 <= nx < 64 and 0 <= ny < 64:
                    dests.add((nx, ny))
    # Also add current leg positions shifted
    for leg in legs:
        for dx in range(-20, 24, 4):
            for dy in range(-20, 24, 4):
                nx, ny = leg.x + dx, leg.y + dy
                if 0 <= nx < 64 and 0 <= ny < 64:
                    dests.add((nx, ny))
    dests = sorted(dests)

    print(f"  Destinations: {len(dests)}", flush=True)

    queue = deque()
    queue.append(([], start_state))
    visited = {start_state}
    iters = 0

    while queue:
        moves, state = queue.popleft()
        iters += 1
        if iters % 1000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(moves)} v={len(visited)}", flush=True)

        if len(moves) >= move_limit:
            continue

        for leg_idx in range(num_legs):
            for (dx, dy) in dests:
                g = replay_and_move(level_idx, moves, leg_idx, dx, dy)
                if g is None:
                    continue

                # Check win
                if g._current_level_index > level_idx or g._state.name == "WIN":
                    all_moves = moves + [(leg_idx, dx, dy)]
                    print(f"  FOUND! {len(all_moves)} moves = {len(all_moves)*2} clicks ({iters} iters)",
                          flush=True)
                    return all_moves

                new_state = get_state(g)
                if new_state not in visited:
                    visited.add(new_state)
                    queue.append((moves + [(leg_idx, dx, dy)], new_state))

    print(f"  No solution ({iters} iters, {len(visited)} states)", flush=True)
    return None


def moves_to_clicks(g, moves):
    """Convert moves to API click coordinates."""
    clicks = []
    g2 = mod.R11l()
    g2.set_level(g._current_level_index if hasattr(g, '_current_level_index') else 0)

    for (li, dx, dy) in moves:
        legs = get_legs(g2)
        leg = legs[li]
        # Select
        clicks.append((leg.x + leg.width // 2, leg.y + leg.height // 2))
        act(g2, leg.x + leg.width // 2, leg.y + leg.height // 2)
        # Move
        clicks.append((dx, dy))
        act(g2, dx, dy)

    return clicks


if __name__ == "__main__":
    all_solutions = {}
    for level in range(6):
        moves = bfs_solve(level)
        if moves:
            g0 = mod.R11l()
            g0.set_level(level)
            clicks = moves_to_clicks(g0, moves)
            all_solutions[level] = clicks
            print(f"  Clicks: {clicks}", flush=True)
        else:
            print(f"  FAILED", flush=True)
            break
        print(flush=True)

    print("=" * 60, flush=True)
    total = sum(len(p) for p in all_solutions.values())
    baseline = sum([7, 28, 30, 20, 37, 45])
    print(f"Solved {len(all_solutions)}/6, Total: {total} clicks, Baseline: {baseline}", flush=True)

    if len(all_solutions) == 6:
        print("\nVerifying with API...", flush=True)
        arcade = arc_agi.Arcade()
        env = arcade.make("r11l-aa269680", render_mode=None)
        result = env.reset()
        api_total = 0
        for level_idx in range(6):
            for (x, y) in all_solutions[level_idx]:
                result = env.step(CLICK, data={"x": x, "y": y})
                api_total += 1
            print(f"  Level {level_idx+1}: {len(all_solutions[level_idx])} clicks, "
                  f"levels={result.levels_completed}")
        print(f"\nTotal: {api_total}, State: {result.state}")
