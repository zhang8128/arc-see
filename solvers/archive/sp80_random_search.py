"""SP80 solver v2 — includes reachability checking in random search.

For each candidate position combo, verify:
1. Spill marks all boundaries (existing check)
2. Each sprite can reach its target via BFS (new)
3. Total movement cost fits within step budget (new)
"""
import importlib.util
import random
import time
from collections import deque
from arcengine import GameAction

spec = importlib.util.spec_from_file_location('sp80', 'environment_files/sp80/0ee2d095/sp80.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def simulate_spill(g):
    g.tadqvfdobr()
    g.action.id = GameAction.ACTION5
    g.action.data = {}
    for _ in range(500):
        if g.epilwznfbr or not g.pksbqruoge:
            break
        g.step()
    bs = g.mldlhgjtqi()
    return all(b in g.srwrqoodsc for b in bs) and not g.enlvswjeov


def bfs_distance(g, sprite_w, sprite_h, sx, sy, tx, ty):
    """BFS distance from (sx,sy) to (tx,ty) for a sprite of given size."""
    if sx == tx and sy == ty:
        return 0
    grid_w, grid_h = g.current_level.grid_size

    # Build blocked set from boundaries
    boundaries = g.mldlhgjtqi()
    blocked = set()
    for b in boundaries:
        bx, by, bw, bh = b.x, b.y, b.width, b.height
        for dy in range(-1, bh + 1):
            for dx in range(-1, bw + 1):
                blocked.add((bx + dx, by + dy))

    visited = {(sx, sy)}
    queue = deque([(sx, sy, 0)])
    while queue:
        cx, cy, d = queue.popleft()
        if d > 80:
            continue
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = cx+dx, cy+dy
            if (nx, ny) in visited:
                continue
            if nx < 0 or ny < 3 or nx + sprite_w > grid_w or ny + sprite_h > grid_h:
                visited.add((nx, ny))
                continue
            # Check if any pixel of sprite overlaps blocked area
            ok = True
            for sx2 in range(sprite_w):
                for sy2 in range(sprite_h):
                    if (nx + sx2, ny + sy2) in blocked:
                        ok = False
                        break
                if not ok:
                    break
            if not ok:
                visited.add((nx, ny))
                continue
            visited.add((nx, ny))
            if nx == tx and ny == ty:
                return d + 1
            queue.append((nx, ny, d + 1))
    return -1  # unreachable


def solve_level(level_idx, max_iters=2000000):
    """Solve a level with reachability checking."""
    g0 = mod.Sp80()
    g0.full_reset()
    g0.set_level(level_idx)

    moveables = g0.rxjmwfcjyw()
    grid_w, grid_h = g0.current_level.grid_size
    boundaries = g0.mldlhgjtqi()
    max_by = max(b.y for b in boundaries) if boundaries else grid_h - 3
    steps = g0.tunzhnhfa

    print(f"\n=== Level {level_idx + 1} ===")
    print(f"  Grid: {grid_w}x{grid_h}, steps: {steps}")
    print(f"  Sprites: {len(moveables)}")
    for m in moveables:
        print(f"    {m.name} at ({m.x},{m.y}) {m.width}x{m.height}")

    positions = []
    for sp in moveables:
        pos = [(x, y) for y in range(3, max_by) for x in range(grid_w - sp.width + 1)]
        positions.append(pos)

    start = time.time()
    checked = 0
    best_cost = float('inf')
    best_combo = None

    for seed in range(500):
        rng = random.Random(seed * 7919)
        for _ in range(max_iters // 500):
            combo = tuple(rng.choice(p) for p in positions)

            g = mod.Sp80()
            g.full_reset()
            g.set_level(level_idx)
            mv = g.rxjmwfcjyw()

            valid = True
            for i, (x, y) in enumerate(combo):
                if not g.aqltiyljgy(mv[i], x, y):
                    valid = False
                    break
                mv[i].set_position(x, y)
            if not valid:
                continue

            # Check overlaps
            overlap = any(g.ccgagqcmlv(mv[i], mv[j])
                          for i in range(len(combo)) for j in range(i+1, len(combo)))
            if overlap:
                continue

            if not simulate_spill(g):
                checked += 1
                if checked % 50000 == 0:
                    elapsed = time.time() - start
                    print(f"  checked {checked} ({elapsed:.0f}s)")
                continue

            checked += 1

            # Spill works! Now check reachability
            total_cost = 0
            reachable = True
            for i, sp in enumerate(moveables):
                tx, ty = combo[i]
                dist = bfs_distance(g0, sp.width, sp.height, sp.x, sp.y, tx, ty)
                if dist < 0:
                    reachable = False
                    break
                total_cost += dist
                if i > 0:
                    total_cost += 1  # click to select

            if not reachable:
                continue

            total_cost += 1  # ACTION5
            if total_cost < steps and total_cost < best_cost:
                best_cost = total_cost
                best_combo = combo
                elapsed = time.time() - start
                names = [m.name for m in moveables]
                print(f"  FOUND: cost={total_cost} ({checked} checked, {elapsed:.1f}s)")
                print(f"    {list(zip(names, combo))}")
                if total_cost < steps * 0.8:
                    return best_combo  # good enough

    return best_combo


def main():
    all_solutions = {}
    for level_idx in range(6):
        combo = solve_level(level_idx)
        if combo:
            all_solutions[level_idx + 1] = combo
        else:
            print(f"  FAILED")
            break

    if len(all_solutions) == 6:
        print("\nAll 6 levels solved! Verifying with API...")
        # Write solutions for verification
        for lv, combo in all_solutions.items():
            print(f"  Level {lv}: {combo}")


if __name__ == "__main__":
    main()
