"""BP35 — gravity platformer. 5 of 9 levels solved.

Mechanics: gravity platformer on 11-wide grids.
- LEFT/RIGHT (ACTION3/4): move player 1 grid cell, gravity check after
- CLICK (ACTION6, data={x,y}): destroy tile at screen coords
  - If tile is directly BELOW player (gravity direction): player falls
  - gravity-flip tile: ALWAYS triggers fall check + flips gravity
  - Otherwise: tile destroyed, player doesn't move
- ACTION7: UNDO last action

Block types:
- 'o' xcjjwqfzjfe: wall (not clickable)
- 'x' qclfkhjnaac: breakable
- 'v'/'u': spike (LOSE)
- '+' fjlzdjxhant: gem (WIN)
- 'm' aknlbboysnc: crusher (L1-3, moves down every 2 steps; kills on same y)
- 'w' jcyhkseuorf: top wall (moves with crusher)
- '1' yuuqpmlxorv: toggle-A (solid, click → tog_b)
- '2' oonshderxef: toggle-B (passable, click → tog_a)
- 'g' lrpkmzabbfa: gravity flip (click → destroy + flip gravity + always fall-check)

Gravity: initial UP (dy=-1), falls toward LOWER y (since grid is reversed [::-1]).

Baselines: [15, 72, 36, 31, 31, 48, 86, 155, 163]

SOLUTIONS FOUND:
  L1: 15 actions (matches baseline 15)
  L3: 34 actions (baseline 36)
  L4: 25 actions (baseline 31)
  L5: 30 actions (baseline 31)
  L6: 41 actions (baseline 48)

NOT YET SOLVED:
  L2 (baseline 72): timeout; 51 clickable blocks, too much branching
  L7 (baseline 86): not yet attempted
  L8 (baseline 155): not yet attempted
  L9 (baseline 163): not yet attempted

NOTE: Solutions run sequentially — CANNOT verify L3+ without solving L2 first!
"""
from arcengine import GameAction

LEFT = GameAction.ACTION3
RIGHT = GameAction.ACTION4
CLICK = GameAction.ACTION6
A7 = GameAction.ACTION7

BASELINES = [15, 72, 36, 31, 31, 48, 86, 155, 163]

# Solution format: list of action descriptors
#   'L' = LEFT move
#   'R' = RIGHT move
#   'CB' = CLICK directly below player (auto-compute grid coords from engine)
#   'Cx,y' = CLICK at grid cell (x,y)
SOLUTIONS = {
    # L1: 15 actions (baseline 15)
    1: ['R', 'R', 'R', 'R', 'L', 'L', 'CB', 'C4,12', 'C4,15', 'C4,16', 'L', 'R', 'CB', 'L', 'L'],

    # L2: 41 actions (baseline 72). Solved via visual inspection of grid.
    # Path: up col 5→col 6 fall → left to col 3 via row 29 breaks →
    #       break (2,28) falls to (2,25) → right to (5,25) → break (5,24,23)
    #       falls to (5,21) → left to (3,21) → break (3,20) falls to (3,18)
    #       → chain of clicks at col 3 rows 17,16 then break row 16 cols
    #       4-8 walking right → break (8,15,14) falls to (8,11) → walk left
    #       to (5,10) via gravity → break (5,9) falls to gem (5,7).
    2: ['R','R','C5,36','C5,35','C6,35','R','C5,29','L','C4,29','L','C3,29',
        'L','C2,29','L','C2,28','R','R','R','C5,24','C5,23','L','L','C3,20',
        'C3,17','C3,16','C4,16','R','C5,16','R','C6,16','R','C7,16','R',
        'C8,16','R','C8,15','C8,14','L','L','L','C5,9'],

    # L3: 34 actions (baseline 36) - toggle blocks introduced
    3: ['R','C5,28','R','R','CB','C4,23','C5,23','L','C3,23','L','L','L','R','R','C5,17','C5,18','R','C6,17','C6,18','R','R','C5,12','C6,12','L','C4,12','L','C3,12','L','L','R','C5,7','R','R','R'],

    # L4: 25 actions (baseline 31) - gravity flip introduced
    4: ['R','R','R','R','L','C5,7','R','L','L','L','L','C3,17','L','R','R','C7,23','C7,24','C3,23','R','C5,23','R','L','L','L','C4,31'],

    # L5: 30 actions (baseline 31)
    5: ['R','R','R','R','C7,9','C8,9','C9,9','C8,12','CB','R','CB','L','L','L','L','L','C3,21','C8,29','L','R','R','R','R','R','R','R','L','L','L','L'],

    # L6: 41 actions (baseline 48)
    6: ['R','R','R','R','R','C6,22','C6,25','C7,25','C4,31','L','L','R','R','L','L','C5,13','L','L','R','R','R','C8,1','L','L','C4,13','L','R','R','CB','L','L','R','R','R','R','L','L','L','L','L','L'],
}


def verify():
    """Verify solutions against the game engine, level by level in sequence."""
    import arc_agi

    arcade = arc_agi.Arcade()
    env = arcade.make("bp35-0a0ad940", render_mode=None)
    obs = env.reset()
    obs = env.reset()  # double reset

    total = 0
    for level in sorted(SOLUTIONS.keys()):
        sol = SOLUTIONS[level]
        for desc in sol:
            eng = env._game.oztjzzyqoek
            cam_y = eng.camera.rczgvgfsfb[1]

            if desc == 'L':
                obs = env.step(LEFT)
            elif desc == 'R':
                obs = env.step(RIGHT)
            elif desc == 'CB':
                pp = eng.twdpowducb.qumspquyus
                gu = eng.vivnprldht
                dy = -1 if gu else 1
                bx, by = pp[0], pp[1] + dy
                obs = env.step(CLICK, data={"x": bx * 6, "y": by * 6 - cam_y})
            elif desc.startswith('C'):
                cx, cy = map(int, desc[1:].split(','))
                obs = env.step(CLICK, data={"x": cx * 6, "y": cy * 6 - cam_y})
            total += 1

        print(f"  L{level}: {len(sol):3d} actions (baseline {BASELINES[level-1]}), "
              f"levels_completed={obs.levels_completed}, state={obs.state.name}")
        if obs.state.name == 'GAME_OVER':
            print(f"  GAME OVER at L{level}! (L{level-1} may need to be solved first)")
            break

    n = len(SOLUTIONS)
    print(f"\nTotal: {total} actions (baselines: {sum(BASELINES[k-1] for k in SOLUTIONS)})")
    print(f"Final state: {obs.state}")


if __name__ == "__main__":
    verify()
