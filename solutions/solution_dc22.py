"""Complete solution for DC22 (dc22-4c9bff3e) — all 6 levels.

Track/teleport/bridge puzzle. UDLR movement + click buttons/teleporters.
Total: 426 actions. Baselines: 1192.
"""
import arc_agi
from arcengine import GameAction

UP = GameAction.ACTION1
DOWN = GameAction.ACTION2
LEFT = GameAction.ACTION3
RIGHT = GameAction.ACTION4
CLICK = GameAction.ACTION6
BASELINES = [64, 117, 59, 78, 324, 550]

# Encoded as: U/D/L/R for directional, Cx,y for clicks
# API-verified: all 6 levels replay sequentially to GameState.WIN
SOLUTIONS = {
    1: "U C48,36 U U U U R R R R R C48,19 U U U C48,36 U U R R",
    2: "C52,40 D D D D D D R R R R R R C52,22 D D D D D U U U U U U U U U U C52,31 R U U U U U U U U U U R",
    3: "L C51,18 C51,27 L L L D D D L C51,18 L L L L C51,27 L L L C51,18 C51,27 U U U U C51,36 U U R R U R C51,45 U U U R R R R R R D D R",
    4: "D R C46,28 C46,28 C46,28 C46,28 C46,28 C57,29 R C57,29 R C57,29 R C57,29 R R R R R R D D D D L L L D D C52,19 D R R C46,28 D D D D D D C46,28 R C46,28 R C46,28 R C46,28 R C57,29 D C57,29 R C57,29 R C57,29 R R R R D D R",
    5: "L C52,41 L U U L C52,41 C47,22 C47,22 C47,22 C47,22 C57,23 C57,23 C57,23 C57,23 C50,30 C50,30 C50,30 C55,30 C55,30 C55,30 C52,35 C45,30 C45,30 C45,30 C60,30 C60,30 C60,30 C55,30 C55,30 C55,30 L U U U U R U C45,30 C45,30 C45,30 C50,30 C50,30 C50,30 C55,30 C55,30 C55,30 L U U U U U U U C52,48 R C45,30 C45,30 C45,30 C60,30 C60,30 C60,30 U U U U U U U U D D D D D D D D D D D D D R R R R R R R C52,14 D D D D D L L C52,14 U U L L L L L L",
    6: "L L L L L U U C51,25 U U R L D D C51,25 D D C51,25 C56,8 C56,8 C56,8 C56,8 D D L L L D L C56,8 U L C56,8 U U U U U U U U U U U U U U U U U U U L D D R D D D D D D D D D D D D D D D D R C56,8 R C56,8 R C56,8 R C56,8 R U U U C51,48 C51,48 C51,48 C51,25 L C47,37 C47,37 C47,37 C47,37 C51,18 R R C55,37 C55,37 C55,37 C55,37 C55,37 L U C51,33 C51,33 C51,33 L D C47,37 C47,37 R U C51,33 C51,33 C51,33 R D L C51,25 C51,48 C51,48 C51,48 C51,25 D D D R R R R R R R R R R R R R R R R R R R R R U U",
}

DIR_MAP = {'U': UP, 'D': DOWN, 'L': LEFT, 'R': RIGHT}


def decode(encoded):
    """Decode action string to list of (action_id, data) tuples."""
    actions = []
    for token in encoded.split():
        if token in DIR_MAP:
            actions.append((DIR_MAP[token], None))
        elif token.startswith('C'):
            x, y = token[1:].split(',')
            actions.append((CLICK, {'x': int(x), 'y': int(y)}))
    return actions


def verify():
    arcade = arc_agi.Arcade()
    env = arcade.make("dc22-4c9bff3e", render_mode=None)
    result = env.reset()
    total = 0

    for level in range(1, 7):
        actions = decode(SOLUTIONS[level])
        for a_id, a_data in actions:
            if a_data:
                result = env.step(a_id, data=a_data)
            else:
                result = env.step(a_id)
        total += len(actions)
        print(f"  L{level}: {len(actions):3d} actions (baseline {BASELINES[level-1]}), levels_completed={result.levels_completed}")

    print(f"\nTotal: {total} actions (baselines: {sum(BASELINES)})")
    print(f"Final state: {result.state}")
    assert str(result.state) == "GameState.WIN", f"Expected WIN, got {result.state}"
    print("ALL VERIFIED!")


if __name__ == "__main__":
    verify()
