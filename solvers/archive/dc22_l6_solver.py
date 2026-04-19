"""DC22 Level 6 solver — comprehensive BFS with all mechanics.
State = pixel hash + piece position. Actions = UDLR + all visible clickable buttons."""
import importlib.util, copy, hashlib, sys
from collections import deque
from arcengine import GameAction, ActionInput, InteractionMode

spec = importlib.util.spec_from_file_location('dc22', 'environment_files/dc22/4c9bff3e/dc22.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
CLICK = GameAction.ACTION6
DIR_NAMES = {UP: 'U', DOWN: 'D', LEFT: 'L', RIGHT: 'R'}


def state_key(g):
    px = (g.fdvakicpimr.x, g.fdvakicpimr.y)
    frame = g.get_pixels(0, 0, 64, 64)
    return (px, hashlib.md5(frame.tobytes()).hexdigest())


def get_clickables(g):
    """Get all clickable button positions."""
    clicks = []
    seen = set()
    for sp in g.current_level.get_sprites():
        if sp.interaction in (InteractionMode.REMOVED, InteractionMode.INVISIBLE):
            continue
        if not sp.is_visible:
            continue
        has_jpug = 'jpug' in sp.tags
        has_sys = 'sys_click' in sp.tags
        if not (has_jpug or has_sys):
            continue
        cx = sp.x + sp.width // 2
        cy = sp.y + sp.height // 2
        key = (cx, cy)
        if key in seen:
            continue
        seen.add(key)
        clicks.append((cx, cy, sp.name))
    return clicks


def solve_level6(max_depth=300):
    g0 = mod.Dc22()
    g0.set_level(5)  # 0-indexed

    start = state_key(g0)
    queue = deque([(g0, [], 0)])
    visited = {start}
    iters = 0
    best_depth = max_depth

    while queue:
        g, path, depth = queue.popleft()
        iters += 1

        if iters % 2000 == 0:
            pos = (g.fdvakicpimr.x, g.fdvakicpimr.y)
            print(f"  iter={iters} q={len(queue)} v={len(visited)} d={depth} pos={pos}", flush=True)

        if depth >= best_depth:
            continue

        if g._current_level_index > 5 or g._state.name == "WIN":
            print(f"  FOUND! {depth} steps ({iters} iters)", flush=True)
            best_depth = depth
            print(f"  Path:", flush=True)
            for a in path:
                print(f"    {a}", flush=True)
            continue  # try to find shorter

        if g._state.name == "GAME_OVER":
            continue

        # Movement
        for d in [UP, DOWN, LEFT, RIGHT]:
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=d))
            if g2._state.name == "GAME_OVER":
                continue
            sk = state_key(g2)
            if sk not in visited:
                visited.add(sk)
                queue.append((g2, path + [DIR_NAMES[d]], depth + 1))

        # Clicks
        for cx, cy, bname in get_clickables(g):
            g2 = copy.deepcopy(g)
            g2.perform_action(ActionInput(id=CLICK, data={'x': cx, 'y': cy}))
            if g2._state.name == "GAME_OVER":
                continue
            sk = state_key(g2)
            if sk not in visited:
                visited.add(sk)
                queue.append((g2, path + [f"click({bname},{cx},{cy})"], depth + 1))

    print(f"  Done: {iters} iters, {len(visited)} states, best={best_depth}", flush=True)
    return best_depth


if __name__ == "__main__":
    depth = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    print(f"DC22 L6 BFS solver (max_depth={depth})")
    solve_level6(depth)
