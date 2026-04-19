"""Verify SC25 solutions L1-L5 with the arc_agi API."""
import arc_agi
from arcengine import GameAction

CLICK = GameAction.ACTION6
UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4

SLOT_XY = {
    (0,0): (25, 50), (0,1): (30, 50), (0,2): (35, 50),
    (1,0): (25, 55), (1,1): (30, 55), (1,2): (35, 55),
    (2,0): (25, 60), (2,1): (30, 60), (2,2): (35, 60),
}
RESIZE_SLOTS = [(0,1), (1,0), (1,2), (2,1)]
TELEPORT_SLOTS = [(0,0), (0,1), (1,1)]
FIREBALL_SLOTS = [(0,1), (1,1), (2,1)]

# BFS solutions for levels 1-5
SOLUTIONS = {
    1: ['L', 'L', 'L', 'L', 'resize', 'L', 'L', 'L', 'L'],
    2: ['teleport', 'U', 'U'],
    3: ['R', 'fireball', 'D', 'D', 'L', 'L', 'L', 'D', 'L'],
    4: ['D', 'D', 'D', 'resize', 'L', 'resize', 'fireball', 'D', 'D', 'R', 'R', 'R', 'R', 'R'],
    5: ['resize', 'teleport', 'L', 'L', 'L', 'L', 'L', 'L', 'U', 'resize', 'fireball', 'D', 'D', 'L', 'fireball', 'teleport', 'U', 'U', 'U', 'U', 'U', 'U'],
}

SPELL_COST = {"resize": 5, "teleport": 4, "fireball": 4}
DIR_MAP = {"U": UP, "D": DOWN, "L": LEFT, "R": RIGHT}


def play_solution(env, solution):
    """Play a solution, return (actions_used, last_result)."""
    actions = 0
    result = None
    for a in solution:
        if a in ("resize", "teleport", "fireball"):
            slots = {"resize": RESIZE_SLOTS, "teleport": TELEPORT_SLOTS, "fireball": FIREBALL_SLOTS}[a]
            for (r, c) in slots:
                x, y = SLOT_XY[(r, c)]
                result = env.step(CLICK, data={"x": x, "y": y})
                actions += 1
        else:
            result = env.step(DIR_MAP[a])
            actions += 1
    return actions, result


def action_cost(solution):
    return sum(SPELL_COST.get(a, 1) for a in solution)


def verify():
    arcade = arc_agi.Arcade()
    env = arcade.make("sc25-f9b21a2f", render_mode=None)
    result = env.reset()
    print(f"Game started: {result.state}")

    total = 0
    for level_num in range(1, 6):
        sol = SOLUTIONS[level_num]
        expected_cost = action_cost(sol)

        # Level 1 needs a dummy first action for demo
        if level_num == 1:
            result = env.step(UP)  # consumed by demo
            total += 1

        actions_used, result = play_solution(env, sol)
        total += actions_used
        print(f"Level {level_num}: {actions_used} API actions (logical cost={expected_cost}), "
              f"levels_completed={result.levels_completed}, state={result.state}")

    print(f"\nTotal API actions: {total}")
    print(f"Levels completed: {result.levels_completed}")
    print(f"State: {result.state}")


if __name__ == "__main__":
    verify()
