"""G50T: analyze the maze pixel array directly to find:
1. All positions where a 5x5 or 7x7 player box fits in the maze floor
2. Whether there's a path to the goal when uwxkstolmf is ignored
3. Whether there's a path to the goal when uwxkstolmf is at its shifted position
"""
import importlib.util
import numpy as np
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

MAZE_X, MAZE_Y = 13, 7  # Where maze sprite is drawn


def can_place_at(maze, player_mask, gx, gy, other_masks=()):
    """Check if player's non-transparent mask fits at global (gx, gy).

    Walkable = maze pixel is >= 0 (part of the maze sprite) AND no other
    entity's non-transparent pixels overlap the player's non-transparent pixels.
    """
    pm = player_mask  # shape (ph, pw) of bools (True = player pixel)
    ph, pw = pm.shape
    mh, mw = maze.shape
    for dy in range(ph):
        for dx in range(pw):
            if not pm[dy, dx]:
                continue  # skip transparent player pixels
            # Global pixel coordinate
            gpx = gx + dx
            gpy = gy + dy
            # Local to maze sprite
            lx = gpx - MAZE_X
            ly = gpy - MAZE_Y
            # Must be inside maze bounds AND maze pixel is walkable (not -1)
            if not (0 <= lx < mw and 0 <= ly < mh):
                return False  # outside maze sprite
            if maze[ly, lx] < 0:
                return False  # transparent = wall
            # Check other entity masks too
            for om_x, om_y, om in other_masks:
                lx2 = gpx - om_x
                ly2 = gpy - om_y
                if 0 <= lx2 < om.shape[1] and 0 <= ly2 < om.shape[0]:
                    if om[ly2, lx2]:
                        return False  # blocked by entity
    return True


def bfs_grid(maze, player_mask, start, other_masks=(), step=6):
    """BFS over 6-pixel step grid, checking collision at each destination."""
    seen = {start: []}
    queue = deque([start])
    moves = {'D': (0, step), 'U': (0, -step), 'L': (-step, 0), 'R': (step, 0)}
    while queue:
        pos = queue.popleft()
        for dname, (dx, dy) in moves.items():
            np_pos = (pos[0] + dx, pos[1] + dy)
            if np_pos in seen:
                continue
            if can_place_at(maze, player_mask, *np_pos, other_masks=other_masks):
                seen[np_pos] = seen[pos] + [dname]
                queue.append(np_pos)
    return seen


def main():
    g = mod.G50t()
    g.set_level(0)

    maze = g.vgwycxsxjz.afbbgvkpip.xmdjbwrpmv.pixels
    player_px = g.vgwycxsxjz.dzxunlkwxt.xmdjbwrpmv.pixels
    print(f"maze shape: {maze.shape}, player shape: {player_px.shape}")

    # Player mask = non-transparent (>= 0) cells
    player_mask = (player_px >= 0)
    print(f"player mask (True=solid):")
    for row in player_mask:
        print('  ' + ''.join('#' if v else '.' for v in row))

    # Goal position
    goal_x = g.vgwycxsxjz.whftgckbcu.x
    goal_y = g.vgwycxsxjz.whftgckbcu.y
    print(f"\ngoal at ({goal_x}, {goal_y})")

    # Uwxkstolmf current position & mask (>= 0 = non-transparent)
    uwx = g.vgwycxsxjz.uwxkstolmf[0]
    uwx_px = uwx.xmdjbwrpmv.pixels
    uwx_mask = (uwx_px >= 0)
    print(f"uwx at ({uwx.x}, {uwx.y}), shape {uwx_px.shape}")

    # Hamay sprite
    ham = g.vgwycxsxjz.hamayflsib[0]
    ham_px = ham.xmdjbwrpmv.pixels
    ham_mask = (ham_px >= 0)
    print(f"ham at ({ham.x}, {ham.y}), shape {ham_px.shape}")

    start = (13, 7)

    # Scenario 1: maze only (no entities)
    print("\n=== Scenario 1: maze only (no entities blocking) ===")
    reach = bfs_grid(maze, player_mask, start)
    print(f"  reachable: {len(reach)} positions")
    # Can we reach a position near the goal?
    for (gx, gy) in sorted(reach):
        if abs(gx - goal_x) < 9 and abs(gy - goal_y) < 9:
            print(f"  NEAR GOAL: {(gx, gy)} via path len={len(reach[(gx, gy)])}")

    # Scenario 2: maze + uwx at original (13, 37)
    print("\n=== Scenario 2: maze + uwx at (13,37) + ham at (37,7) ===")
    others = [(uwx.x, uwx.y, uwx_mask), (ham.x, ham.y, ham_mask)]
    reach2 = bfs_grid(maze, player_mask, start, other_masks=others)
    print(f"  reachable: {len(reach2)} positions")
    for pos in sorted(reach2):
        print(f"    {pos}")

    # Scenario 3: maze + uwx at shifted (19, 37)
    print("\n=== Scenario 3: maze + uwx at (19,37) + ham at (37,7) ===")
    others3 = [(19, 37, uwx_mask), (ham.x, ham.y, ham_mask)]
    reach3 = bfs_grid(maze, player_mask, start, other_masks=others3)
    print(f"  reachable: {len(reach3)} positions")
    # Show only the new ones
    new_pos = set(reach3) - set(reach2)
    print(f"  NEW positions when uwx shifted: {sorted(new_pos)}")


if __name__ == "__main__":
    main()
