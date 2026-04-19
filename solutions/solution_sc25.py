"""Complete solution for SC25 (sc25-f9b21a2f) — all 6 levels.

SC25 is a spell-casting dungeon crawler. Player navigates mazes using
3 spells (teleport, resize, fireball) to destroy doors and reach exits.

Spell casting: click 3x3 grid slots via ACTION6 with x,y coordinates.
Spells: jzukcpajs=teleport, fpokrvgln=resize, aprnrzeyj=fireball.

Each level solution was found using BFS (levels 1-5) and manual path
analysis (level 6) on the local game engine.
"""
import arc_agi
from arcengine import GameAction

CLICK = GameAction.ACTION6
UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4

# Spell slot click coordinates (display coords = grid coords, camera scale=1)
SLOT_XY = {
    (0,0): (25, 50), (0,1): (30, 50), (0,2): (35, 50),
    (1,0): (25, 55), (1,1): (30, 55), (1,2): (35, 55),
    (2,0): (25, 60), (2,1): (30, 60), (2,2): (35, 60),
}

# Spell patterns (slots to click)
RESIZE_SLOTS   = [(0,1), (1,0), (1,2), (2,1)]  # fpokrvgln: toggle scale 1<->2
TELEPORT_SLOTS = [(0,0), (0,1), (1,1)]          # jzukcpajs: teleport to target
FIREBALL_SLOTS = [(0,1), (1,1), (2,1)]          # aprnrzeyj: shoot in facing direction

# Solutions as high-level action sequences
# Moves: U/D/L/R. Spells: resize/teleport/fireball.
# Level 1 has a demo animation that consumes the first input.
SOLUTIONS = {
    1: ['L', 'L', 'L', 'L', 'resize', 'L', 'L', 'L', 'L'],
    2: ['teleport', 'U', 'U'],
    3: ['R', 'fireball', 'D', 'D', 'L', 'L', 'L', 'D', 'L'],
    4: ['D', 'D', 'D', 'resize', 'L', 'resize', 'fireball', 'D', 'D', 'R', 'R', 'R', 'R', 'R'],
    5: ['resize', 'teleport', 'L', 'L', 'L', 'L', 'L', 'L', 'U',
        'resize', 'fireball', 'D', 'D', 'L', 'fireball', 'teleport',
        'U', 'U', 'U', 'U', 'U', 'U'],
    6: ['resize', 'teleport', 'R', 'R', 'U', 'U',
        'fireball',           # destroy first doors (switch at 17,33)
        'resize', 'teleport', # scale 2, tp to (53,37)
        'L', 'L', 'L',
        'fireball',           # destroy second doors (switch at 37,37)
        'teleport',           # tp to (29,33)
        'U', 'R',             # navigate to corridor
        'U', 'U', 'U', 'U',  # up through former second-door area to exit
        'U'],                 # trigger exit
}

DIR_MAP = {'U': UP, 'D': DOWN, 'L': LEFT, 'R': RIGHT}
SPELL_MAP = {
    'resize': RESIZE_SLOTS,
    'teleport': TELEPORT_SLOTS,
    'fireball': FIREBALL_SLOTS,
}


def play_level(env, solution):
    """Play one level's solution. Returns (api_actions_used, last_result)."""
    api_actions = 0
    result = None
    for action in solution:
        if action in SPELL_MAP:
            for (r, c) in SPELL_MAP[action]:
                x, y = SLOT_XY[(r, c)]
                result = env.step(CLICK, data={"x": x, "y": y})
                api_actions += 1
        else:
            result = env.step(DIR_MAP[action])
            api_actions += 1
    return api_actions, result


def verify():
    """Verify all solutions with the arc_agi API."""
    arcade = arc_agi.Arcade()
    env = arcade.make("sc25-f9b21a2f", render_mode=None)
    result = env.reset()

    total = 0
    for level_num in range(1, 7):
        # Level 1 demo animation consumes first input
        if level_num == 1:
            result = env.step(UP)
            total += 1

        actions, result = play_level(env, SOLUTIONS[level_num])
        total += actions
        print(f"Level {level_num}: {actions:3d} API actions, "
              f"levels_completed={result.levels_completed}, state={result.state}")

    print(f"\nTotal: {total} actions")
    print(f"Baseline: {sum([39, 5, 32, 33, 66, 41])} actions")
    print(f"Final state: {result.state}")
    assert str(result.state) == "GameState.WIN", f"Expected WIN, got {result.state}"
    print("ALL VERIFIED!")


if __name__ == "__main__":
    verify()
