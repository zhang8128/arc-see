"""SC25 solver — spell-casting dungeon crawler.

Game mechanics:
- Player (nwxssyzit) starts at scale 2, moves 4px per step with ACTION1-4
- Exit (pcohqadae) — touching it advances to next level
- 3 spells cast via 3x3 clickable grid (ACTION6 with x,y):
  - jzukcpajs (teleport): pattern [(0,0),(0,1),(1,1)] — teleport to marked target
  - fpokrvgln (size change): pattern [(0,1),(1,0),(1,2),(2,1)] — toggle scale 1<->2
  - aprnrzeyj (fireball): pattern [(0,1),(1,1),(2,1)] — shoot in facing direction, destroy doors
- Doors block paths, destroyed by fireball hitting switch (edusagitv)
- Energy packs reduce action counter by 10
- Action limits per level: 50, 25, 50, 35, 65, 60
"""
import arc_agi
import importlib.util
from arcengine import GameAction

# Load game module to inspect camera
spec = importlib.util.spec_from_file_location('sc25', 'environment_files/sc25/f9b21a2f/sc25.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Spell slot grid positions in the game:
# Row 0: (24,49), (29,49), (34,49)
# Row 1: (24,54), (29,54), (34,54)
# Row 2: (24,59), (29,59), (34,59)
#
# The game has hardcoded display coordinates for each slot:
SLOT_DISPLAY = {
    (0,0): (25, 50), (0,1): (30, 50), (0,2): (35, 50),
    (1,0): (25, 55), (1,1): (30, 55), (1,2): (35, 55),
    (2,0): (25, 60), (2,1): (30, 60), (2,2): (35, 60),
}

# Spell patterns (which slots to click):
SPELLS = {
    "teleport": [(0,0), (0,1), (1,1)],      # jzukcpajs
    "resize":   [(0,1), (1,0), (1,2), (2,1)], # fpokrvgln
    "fireball": [(0,1), (1,1), (2,1)],         # aprnrzeyj
}

UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4


def discover_slot_clicks(env, game):
    """Find the correct API coordinates for clicking each spell slot."""
    # Try the display coordinates directly first
    cam = game.camera
    print(f"Camera: bg={cam.background}, letterbox={cam.letter_box}")
    scale, ox, oy = cam._calculate_scale_and_offset()
    print(f"Scale={scale}, offset=({ox},{oy})")

    # Test display_to_grid for the slot positions
    for (r,c), (dx, dy) in SLOT_DISPLAY.items():
        result = cam.display_to_grid(dx, dy)
        print(f"  Slot ({r},{c}) display ({dx},{dy}) -> grid {result}")

    return SLOT_DISPLAY  # Start with these, adjust if needed


def cast_spell(env, spell_name):
    """Cast a spell by clicking the required slots. Returns list of actions taken."""
    slots = SPELLS[spell_name]
    actions = []
    for (r, c) in slots:
        dx, dy = SLOT_DISPLAY[(r, c)]
        result = env.step(GameAction.ACTION6, data={"x": dx, "y": dy})
        actions.append(f"CLICK({r},{c})")
        # Need to wait for animations - step through frames
        while True:
            result2 = env.step(GameAction.ACTION6, data={"x": dx, "y": dy})
            # Check if action completed
            break
    return actions


def move(env, direction, count=1):
    """Move the player in a direction multiple times."""
    results = []
    for _ in range(count):
        result = env.step(direction)
        results.append(result)
    return results


def explore_level(env):
    """Interactively explore the current level state."""
    game = mod.Sc25()
    # Can't easily get state from env, but we can try actions and see results
    pass


def solve():
    """Main solver - run through all levels."""
    arcade = arc_agi.Arcade()
    env = arcade.make("sc25-f9b21a2f", render_mode=None)
    result = env.reset()
    print(f"Initial state: {result.state}, levels_completed={result.levels_completed}")

    # First, discover click coordinates
    game = mod.Sc25()
    discover_slot_clicks(env, game)

    total_actions = 0

    # Level 1: Player at (39,19) scale 2, exit at (12,17)
    # Available spell: fpokrvgln (resize)
    # Need to resize to small, navigate to exit
    # Player starts facing right (rotation 90)
    # At scale 2, player is 4x4 px, moves 4px per step
    # At scale 1, player is 2x2 px, moves 2px per step
    # Exit at (12,17), player at (39,19)
    # dx = 12-39 = -27, dy = 17-19 = -2
    # At scale 2: 27/4 ~ 7 left, 2/4 ~ 0-1 up
    # But try_move has collision detection, need clear path

    print("\n=== Level 1 ===")
    print("Player (39,19) scale 2 -> Exit (12,17)")
    print("Spell: resize (fpokrvgln)")

    # Try: move left toward exit, then adjust vertically
    actions = []

    # Move left: 39 -> 12 = 27px, at 4px/step = ~7 steps
    # Move up: 19 -> 17 = 2px, at 4px/step = 1 step (may overshoot)

    # Actually let me just try moving directly
    for _ in range(7):
        r = env.step(LEFT)
        actions.append("LEFT")

    # Check position - at 39-28=11, might need adjustment
    r = env.step(UP)
    actions.append("UP")

    print(f"  After {len(actions)} moves: state={r.state}, levels={r.levels_completed}")

    if r.levels_completed < 1:
        # Need more movement or resize spell
        # Try resize to small, then fine movement
        for slot in SPELLS["resize"]:
            dx, dy = SLOT_DISPLAY[slot]
            r = env.step(GameAction.ACTION6, data={"x": dx, "y": dy})
            actions.append(f"CLICK")
            # Wait for animation frames
            for _ in range(20):
                r = env.step(GameAction.ACTION1, data={})  # no-op to advance frame?

        print(f"  After resize: state={r.state}, levels={r.levels_completed}")

    total_actions += len(actions)
    print(f"Level 1: {len(actions)} actions, state={r.state}")
    print(f"\nTotal so far: {total_actions}")
    print(f"Final state: {r.state}")


def interactive_explore():
    """Explore game interactively to figure out solutions."""
    arcade = arc_agi.Arcade()
    env = arcade.make("sc25-f9b21a2f", render_mode=None)
    result = env.reset()

    game = mod.Sc25()
    cam = game.camera
    scale, ox, oy = cam._calculate_scale_and_offset()
    print(f"Camera: scale={scale}, offset=({ox},{oy})")

    # Check display_to_grid mapping
    for (r,c), (dx, dy) in SLOT_DISPLAY.items():
        g = cam.display_to_grid(dx, dy)
        print(f"  Slot ({r},{c}) display ({dx},{dy}) -> grid {g}")

    print(f"\nStarting exploration...")
    print(f"State: {result.state}, levels_completed={result.levels_completed}")
    print(f"Actions available: {result.available_actions}")

    # Level 1: Player at (39,19) scale 2, exit at (12,17)
    # Try moving left several times
    print("\n--- Moving LEFT ---")
    for i in range(8):
        result = env.step(LEFT)
        print(f"  Step {i+1} LEFT: state={result.state}, levels={result.levels_completed}, actions={result.actions_taken}")
        if result.levels_completed > 0:
            print(f"  LEVEL COMPLETE!")
            break

    if result.levels_completed == 0:
        print("\n--- Moving UP ---")
        result = env.step(UP)
        print(f"  UP: state={result.state}, levels={result.levels_completed}, actions={result.actions_taken}")

    if result.levels_completed == 0:
        print("\n--- Trying more LEFT ---")
        for i in range(5):
            result = env.step(LEFT)
            print(f"  LEFT: state={result.state}, levels={result.levels_completed}, actions={result.actions_taken}")
            if result.levels_completed > 0:
                break


if __name__ == "__main__":
    interactive_explore()
