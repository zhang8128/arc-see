"""SB26 solver v4 — pure Python verification + permutation search.

Simulate the game's verification logic in pure Python:
1. Read items from frame slots left→right
2. lngftsryyw: match color against pattern sequence
3. vgszefyyyp: branch into referenced sub-frame
4. After sub-frame completes, return to parent
5. Win when entire pattern consumed without mismatch
"""
import importlib.util
from itertools import permutations
from arcengine import GameAction

spec = importlib.util.spec_from_file_location('sb26', 'environment_files/sb26/7fbdac44/sb26.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

evrmzyfopo = getattr(mod, 'evrmzyfopo', 30)
kojduumcap = getattr(mod, 'kojduumcap', 7)


def extract_level_data(level_idx):
    """Extract all level data needed for solving."""
    g = mod.Sb26()
    g.full_reset()
    g.set_level(level_idx)

    # Pattern (expected colors)
    expected = [int(s.pixels[0, 0]) for s in g.wcfyiodrx]

    # Frames
    frames = []
    for f in g.qaagahahj:
        n_slots = int(f.name[-1])
        frame_color = int(f.pixels[0, 0])
        slot_positions = []
        for i in range(n_slots):
            x = f.x + 2 + i * kojduumcap
            y = f.y + 2
            slot_positions.append((x, y))
        frames.append({"sprite": f, "color": frame_color, "n_slots": n_slots, "positions": slot_positions})

    # Items: what's at each position
    item_map = {}  # (x, y) -> {"name": ..., "color": ...}
    for s in g.dkouqqads:
        item_map[(s.x, s.y)] = {"name": s.name, "color": int(s.pixels[1, 1]), "sprite": s}

    # Pre-placed items (in frame slots, not moveable)
    prefilled = {}  # (x, y) -> item_info
    for frame in frames:
        for pos in frame["positions"]:
            if pos in item_map:
                prefilled[pos] = item_map[pos]

    # Bottom items (moveable)
    bottom_items = []
    for s in g.dkouqqads:
        if s.y > evrmzyfopo:
            bottom_items.append({"name": s.name, "color": int(s.pixels[1, 1]), "sprite": s})

    # Empty slots in frame area
    empty_slots = []
    for frame in frames:
        for pos in frame["positions"]:
            if pos not in prefilled:
                empty_slots.append(pos)

    return {
        "expected": expected,
        "frames": frames,
        "prefilled": prefilled,
        "bottom_items": bottom_items,
        "empty_slots": empty_slots,
        "game": g,
    }


def verify_arrangement(data, slot_assignment):
    """Check if a given slot assignment passes verification.

    slot_assignment: dict (x, y) -> item_info for all slots.
    Returns True if the arrangement matches the expected pattern.
    """
    expected = data["expected"]
    frames = data["frames"]
    frame_by_color = {f["color"]: f for f in frames}

    pattern_idx = [0]  # mutable for closure

    def check_frame(frame, depth=0):
        if depth > 20:
            return False  # prevent infinite recursion
        for pos in frame["positions"]:
            # If pattern fully consumed, we're done — win!
            if pattern_idx[0] >= len(expected):
                return True
            item = slot_assignment.get(pos)
            if item is None:
                return False

            if item["name"] == "vgszefyyyp":
                # Branch into sub-frame
                branch_color = item["color"]
                sub_frame = frame_by_color.get(branch_color)
                if sub_frame is None:
                    return False
                if not check_frame(sub_frame, depth + 1):
                    return False
            elif item["name"] == "lngftsryyw":
                # Check color match
                if item["color"] != expected[pattern_idx[0]]:
                    return False
                pattern_idx[0] += 1
            else:
                return False

        return True

    # Start with first frame
    if not frames:
        return False
    if not check_frame(frames[0]):
        return False

    # All pattern entries consumed?
    return pattern_idx[0] == len(expected)


def solve_level(level_idx):
    """Find the correct arrangement for a level."""
    data = extract_level_data(level_idx)
    expected = data["expected"]
    bottom_items = data["bottom_items"]
    empty_slots = data["empty_slots"]
    prefilled = data["prefilled"]

    print(f"  Expected: {expected}")
    print(f"  Bottom items: {[i['color'] for i in bottom_items]} ({len(bottom_items)})")
    print(f"  Empty slots: {empty_slots} ({len(empty_slots)})")
    print(f"  Prefilled: {len(prefilled)}")

    n = len(bottom_items)
    if n != len(empty_slots):
        print(f"  WARNING: mismatch: {n} items vs {len(empty_slots)} slots")
        n = min(n, len(empty_slots))

    # Build base assignment from prefilled items
    base_assignment = dict(prefilled)

    # Try all permutations of items into empty slots
    checked = 0
    for perm in permutations(range(n)):
        slot_assignment = dict(base_assignment)
        for i, slot_pos in enumerate(empty_slots[:n]):
            slot_assignment[slot_pos] = bottom_items[perm[i]]

        if verify_arrangement(data, slot_assignment):
            print(f"  Found solution after {checked + 1} permutations")
            # Return the ordered list: (item, slot_pos)
            return [(bottom_items[perm[i]], empty_slots[i]) for i in range(n)], data
        checked += 1

    print(f"  No solution found in {checked} permutations")
    return None


def main():
    import arc_agi
    arcade = arc_agi.Arcade()
    env = arcade.make('sb26-7fbdac44', render_mode=None)
    env.reset()

    total = 0

    for lv in range(1, 9):
        print(f"\n{'='*40}")
        print(f"Level {lv}")
        print(f"{'='*40}")

        result = solve_level(lv - 1)
        if result is None:
            print(f"  FAILED")
            break

        placements, data = result

        # Execute via API
        level_actions = 0
        for item_info, (sx, sy) in placements:
            sprite = item_info["sprite"]
            # Select item
            icx, icy = sprite.x + 3, sprite.y + 3
            env.step(GameAction.ACTION6, data={"x": icx, "y": icy})
            level_actions += 1
            # Place in slot
            env.step(GameAction.ACTION6, data={"x": sx + 3, "y": sy + 3})
            level_actions += 1

        # Verify
        r = env.step(GameAction.ACTION5)
        level_actions += 1
        total += level_actions

        if r.levels_completed >= lv:
            print(f"  ✓ Solved in {level_actions} actions (total: {total})")
        else:
            print(f"  ✗ API verification failed! completed={r.levels_completed}")
            break

    print(f"\nFinal: total={total}, completed={r.levels_completed}, state={r.state}")

    if str(r.state) == "GameState.WIN":
        print("ALL VERIFIED! ✓")


if __name__ == "__main__":
    main()
