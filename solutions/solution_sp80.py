"""SP80 verifier v2 — clean implementation with proper rotation + pathfinding."""
import arc_agi
import importlib.util
from collections import deque
from arcengine import GameAction

spec = importlib.util.spec_from_file_location('sp80', 'environment_files/sp80/0ee2d095/sp80.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

SOLUTIONS = {
    1: ((6, 11),),
    2: ((5, 3), (8, 8), (4, 4)),
    3: ((3, 11), (10, 3), (0, 3), (9, 9)),
    4: ((10, 11), (4, 6), (6, 3), (14, 7), (1, 3)),
    5: ((8, 11), (15, 10), (4, 3), (13, 7)),
    6: ((4, 8), (11, 8), (13, 10), (11, 11)),  # reachable solution
}

# Direction → grid delta
DIR = {"right": (1,0), "left": (-1,0), "down": (0,1), "up": (0,-1)}

# For each rotation k, the API action needed for each grid direction
# k=0: normal. k=2: 180° flipped.
ACTION_MAP = {
    0: {"up": GameAction.ACTION1, "down": GameAction.ACTION2,
        "left": GameAction.ACTION3, "right": GameAction.ACTION4},
    2: {"up": GameAction.ACTION2, "down": GameAction.ACTION1,
        "left": GameAction.ACTION4, "right": GameAction.ACTION3},
}


def click_sprite(env, g, sprite):
    """Click on a sprite to select it. Uses a pixel unique to this sprite."""
    k = g.sywpxxgfq
    scale, _, _ = g.camera._calculate_scale_and_offset()

    # Find API coords that, after rotation+camera transform, map to sprite's grid position
    gcx = sprite.x + sprite.width // 2
    gcy = sprite.y + sprite.height // 2

    # The transform chain: API(ax,ay) → lnqtlqefzv(udeubouzyp) → camera.display_to_grid → grid
    # For k=0: camera.d2g(ax, ay) = grid
    # For k=2: camera.d2g(63-ax, 63-ay) = grid
    # So find (tx,ty) where camera.d2g(tx,ty) = (gcx,gcy), then apply inverse rotation

    for tx in range(64):
        for ty in range(64):
            result = g.camera.display_to_grid(tx, ty)
            if result and result[0] == gcx and result[1] == gcy:
                # Apply inverse of udeubouzyp
                if k == 0:
                    ax, ay = tx, ty
                elif k == 2:
                    ax, ay = 63 - tx, 63 - ty
                elif k == 1:
                    ax, ay = 63 - ty, tx
                else:  # k == 3
                    ax, ay = ty, 63 - tx
                return env.step(GameAction.ACTION6, data={"x": ax, "y": ay})

    print(f"    Cannot find display coords for {sprite.name} at ({sprite.x},{sprite.y})")
    return env.step(GameAction.ACTION6, data={"x": 0, "y": 0})


def move_sprite(env, g, sprite, tx, ty):
    """Move sprite from current position to (tx,ty) using BFS + movement actions."""
    k = g.sywpxxgfq
    amap = ACTION_MAP.get(k, ACTION_MAP[0])

    sx, sy = sprite.x, sprite.y
    if sx == tx and sy == ty:
        return 0

    # BFS for shortest path
    visited = {(sx, sy)}
    queue = deque([((sx, sy), [])])
    path = None

    while queue:
        (cx, cy), p = queue.popleft()
        for d, (dx, dy) in DIR.items():
            nx, ny = cx + dx, cy + dy
            if (nx, ny) in visited:
                continue
            visited.add((nx, ny))
            if not g.aqltiyljgy(sprite, nx, ny):
                continue
            np_ = p + [d]
            if nx == tx and ny == ty:
                path = np_
                queue.clear()
                break
            if len(np_) < 80:
                queue.append(((nx, ny), np_))

    if path is None:
        print(f"    No path from ({sx},{sy}) to ({tx},{ty})!")
        return -1

    # Execute path
    actions = 0
    for d in path:
        env.step(amap[d])
        actions += 1
    return actions


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make('sp80-0ee2d095', render_mode=None)
    env.reset()
    total = 0

    for lv in range(1, 7):
        g = env._game
        targets = SOLUTIONS[lv]
        sprites = g.rxjmwfcjyw()
        k = g.sywpxxgfq
        print(f"\nLevel {lv}: k={k}, steps={g.tunzhnhfa}, sprites={len(sprites)}")

        for i, (tx, ty) in enumerate(targets):
            sprite = sprites[i]
            print(f"  [{i}] {sprite.name} ({sprite.x},{sprite.y})→({tx},{ty})", end="")

            # Select if not current
            if g.dpkgglmdup != sprite:
                click_sprite(env, g, sprite)
                total += 1
                if g.dpkgglmdup != sprite:
                    print(f" SELECT FAILED (got {g.dpkgglmdup.name if g.dpkgglmdup else None})")
                    # Try clicking by name match
                    continue

            n = move_sprite(env, g, sprite, tx, ty)
            total += n
            actual = (sprite.x, sprite.y)
            ok = "✓" if actual == (tx, ty) else f"✗ at {actual}"
            print(f" → {ok} ({n} moves)")
            if g.dpkgglmdup != sprite and n >= 0:
                # Selection failed but movement happened on wrong sprite
                # Try clicking at sprite's NEW position (it might have been pushed)
                click_sprite(env, g, sprite)
                total += 1
                if g.dpkgglmdup == sprite:
                    n2 = move_sprite(env, g, sprite, tx, ty)
                    total += n2
                    print(f"    Retry: moved to ({sprite.x},{sprite.y}) in {n2} moves")

        # Spill
        r = env.step(GameAction.ACTION5)
        total += 1
        print(f"  Level {lv}: completed={r.levels_completed} (total={total})")

        if r.levels_completed < lv:
            print(f"  FAILED!")
            break

    print(f"\nFinal: total={total}, state={r.state}")
    if str(r.state) == "GameState.WIN":
        print("ALL VERIFIED! ✓")


if __name__ == "__main__":
    main()
