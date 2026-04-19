"""CN04 solver — marker overlap puzzle. Place pieces so 8-markers pair up.

Analytically solved: compute target positions where all markers overlap,
then execute select-move-rotate-place sequences.
"""
import importlib.util, copy
import arc_agi
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('cn04', 'environment_files/cn04/65d47d14/cn04.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
ROTATE = GameAction.ACTION5
CLICK = GameAction.ACTION6

# Analytical solutions: target (x, y, rotation) per sprite per level
TARGETS = {
    0: [('dzfylahsaw', 9, 3, 0), ('vmgdxvpgkh', 4, 4, 0)],
    1: [('glojtydbea', 8, 6, 0), ('grpgefeksy', 4, 5, 0), ('lejuhuvrjg', 3, 3, 0)],
    2: [('gqxqpkuwab', 11, 5, 90), ('hjqjqsmhmf', 6, 5, 0), ('nhppemmlcd', 8, 5, 90)],
    3: [('udepuflbbb', 11, 4, 90), ('ygyvhkssnz', 9, 5, 270), ('zhhaofpbyw', 10, 4, 90)],
    4: [('dnkiufrohe', 7, 6, 180), ('lxgvcnpsir', 11, 9, 0), ('oncjjftokv', 7, 14, 90), ('supigciwwi', 2, 9, 0)],
}


def find_click_for_sprite(g, target_name):
    """Find display coordinates that select a specific sprite."""
    s, ox, oy = g.camera._calculate_scale_and_offset()
    for sp in g.current_level.get_sprites():
        if sp.name == target_name:
            # Scan sprite pixels for a non-transparent one
            h, w = sp.pixels.shape
            for py in range(h):
                for px in range(w):
                    if sp.pixels[py, px] >= 0 and sp.pixels[py, px] != -1:
                        dx = sp.x * s + ox + px * s + s // 2
                        dy = sp.y * s + oy + py * s + s // 2
                        # Verify this click selects the right sprite
                        g2 = copy.deepcopy(g)
                        g2.perform_action(ActionInput(id=CLICK, data={'x': dx, 'y': dy}))
                        if g2.weqid and g2.weqid.name == target_name:
                            return dx, dy
    return None


def execute_level(g, level_idx):
    """Execute the solution for one level. Returns list of API actions."""
    targets = TARGETS[level_idx]
    actions = []

    for target_name, tx, ty, trot in targets:
        # Find current sprite
        sp = None
        for s in g.current_level.get_sprites():
            if s.name == target_name:
                sp = s
                break
        if not sp:
            continue

        # If this sprite is already selected (weqid), good. Otherwise click to select it.
        if not g.weqid or g.weqid.name != target_name:
            click_pos = find_click_for_sprite(g, target_name)
            if click_pos:
                g.perform_action(ActionInput(id=CLICK, data={'x': click_pos[0], 'y': click_pos[1]}))
                actions.append((CLICK, {'x': click_pos[0], 'y': click_pos[1]}))

        if not g.weqid or g.weqid.name != target_name:
            print(f"  WARNING: couldn't select {target_name}")
            continue

        # Rotate to target rotation
        while g.weqid.rotation != trot:
            g.perform_action(ActionInput(id=ROTATE))
            actions.append((ROTATE, None))

        # Move to target position
        dx = tx - g.weqid.x
        dy = ty - g.weqid.y

        for _ in range(abs(dx)):
            d = RIGHT if dx > 0 else LEFT
            g.perform_action(ActionInput(id=d))
            actions.append((d, None))

        for _ in range(abs(dy)):
            d = DOWN if dy > 0 else UP
            g.perform_action(ActionInput(id=d))
            actions.append((d, None))

        # Check if level advanced
        if g._current_level_index > level_idx or g._state.name == "WIN":
            return actions

    return actions


def verify():
    """Verify all solutions with the arc_agi API."""
    # First test locally
    all_actions = {}
    for level_idx in range(5):
        g = mod.Cn04()
        g.set_level(level_idx)
        actions = execute_level(g, level_idx)
        won = g._current_level_index > level_idx or g._state.name == "WIN"
        print(f"L{level_idx+1}: {len(actions)} actions, won={won}")
        if won:
            all_actions[level_idx] = actions
        else:
            print(f"  FAILED locally!")
            return

    # Verify with API
    print("\nVerifying with API...")
    arcade = arc_agi.Arcade()
    env = arcade.make("cn04-65d47d14", render_mode=None)
    result = env.reset()
    total = 0
    for level_idx in range(5):
        for a_id, a_data in all_actions[level_idx]:
            if a_data:
                result = env.step(a_id, data=a_data)
            else:
                result = env.step(a_id)
            total += 1
        print(f"  L{level_idx+1}: {len(all_actions[level_idx])} actions, levels={result.levels_completed}")
    print(f"\nTotal: {total}, State: {result.state}")
    baseline = sum([16, 54, 69, 318, 208])
    print(f"Baseline: {baseline}")
    if str(result.state) == "GameState.WIN":
        print("ALL VERIFIED!")


if __name__ == "__main__":
    verify()
