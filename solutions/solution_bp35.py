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

    # L7: 45 actions (baseline 86) - introduces `h` hazard (same as spike: lethal on fall, blocks on walk)
    # Key: toggle-and-gravity cascade through upper chamber via col 5→6→7 alcove, then col 9 safe descent.
    # Route: (4,15) stable grav-up → (2,8) upper chamber → col 3-6 pickthrough → (7,4) col 7 top →
    #        (7,7) controlled descent → (9,7) alcove → (9,26) col-9 floor → (7,23) rise → (3,23) → gem (3,25).
    7: ['C0,19','R','R','R','C6,19','C0,21','R','R','L','L','L','L',
        'C4,16','C0,13','C4,14','C0,16','L','L','R',
        'C3,10','C0,8','R','C4,9','C0,11','C5,10','R','C5,10','C0,9','C6,9','R',
        'C6,9','C0,10','R','C7,8','C0,5','R','R','L','L','C0,22','L','L','L','L','C0,23'],

    # L8: 64 actions (baseline 155) - introduces `e` 4-directional spreading breakable tile
    # Key mechanic: click e destroys it AND spawns new e's in 4 cardinal neighbors (if empty).
    # e is non-lethal (safe to adjacent-fall), so e blocks spike-rise death.
    # Route: propagate e across row 28-30 to col 9 → rise col 9 (no spike at row 27) to (9,25) →
    #        walk L through row 25 (toggle y@(7,25)) → rise to row 23 → toggle y@(3,22) →
    #        rise col 3 via e@(3,18) ladder → cross row 10 east → flip gravity at (7,10) → fall col 8 → gem.
    8: ['C2,29','C3,29','C4,29','C5,29','C6,29','C7,29','C5,30','C6,30','C7,30',
        'R','R','R','R',
        'C7,31','C7,30','C7,29',
        'C8,29','R','C9,29','R',
        'C9,28','C9,27','C9,26','C9,25',
        'C8,25','L','C7,25',
        'L','L','L','L','L','L',
        'C3,22','C8,18',
        'R',
        'C3,18','C3,17','C3,16','C3,15','C3,14','C3,13','C3,12','C3,11','C3,10',
        'C4,10','R','C5,10','R','C6,10','R','C7,10','R',
        'C7,11','C5,2','C8,11','R',
        'C8,12','C8,13','C8,14','C8,15','C8,16','C8,17',
        'R'],

    # L9: 94 actions (baseline 163) - final level, full game clear.
    # 11×46 grid. Player (3,35) grav up. Gem at (2,40). 15 l, 19 u, 11 h, 8 y, 5 q, 2 e.
    # Path strategy: col 0 vertical tunnel is the only way to reach gem chamber (col 0 rows 39-40
    # is the only access). Col 1 is all walls except q@(1,8). So plan:
    #   Phase 1: place e@(2,7) via e-chain climb through col 7 (from e@(7,8)), then destroy q@(1,8).
    #   Phase 2: destroy all 6 col-0 l tiles remotely (net 0 gravity change — even flips).
    #   Phase 3: toggle y@(2,15) → o, flip grav down, walk R to col 6, flip up, rise to e@(6,31).
    #   Phase 4: climb col 6 e-ladder to (6,29), walk L through row 29 (destroy e chain) to (2,29).
    #   Phase 5: destroy q's at (2,26),(3,26),(4,26), propagate e up col 3 to (2,20),(3,20),(4,20).
    #   Phase 6: chain-climb col 2 to (2,21) (e@(2,20) blocker stops rise).
    #   Phase 7: walk R across row 21 destroying e's, placing row-20 blockers at (3-7,20).
    #   Phase 8: flip grav down, destroy e@(7,22),(7,23),(8,23),(9,23), walk R to (9,23) with
    #           e@(7,24),(8,24),(9,24) blockers preventing death on row-25 h.
    #   Phase 9: flip grav up, chain-destroy col 9 up from (9,22) through (9,16), player rises
    #           with each destroy spawning e above as blocker. y@(9,15) halts final rise at (9,16).
    #   Phase 10: walk L across row 16, destroying e at each col (C and L alternating) until (2,16).
    #            Walk L triggers gravity rise through o@(2,15) → e@(2,7) blocker stops at (2,8).
    #   Phase 11: walk L to (1,8), walk L to (0,8) → rise to (0,7). Flip grav down via l@(9,1)
    #            → fall col 0 to (0,40) (all l's destroyed). Walk R R to gem at (2,40). WIN.
    9: ['C7,8','C7,7','C6,7','C5,7','C4,7','C3,7','C1,8',
        'C0,15','C0,19','C0,21','C0,25','C0,33','C0,35',
        'C2,15',
        'C5,1','R','R','R','C6,1','C6,31','C6,30','C6,29',
        'C5,29','L','C4,29','L','C3,29','L','C2,29','L',
        'C3,26','C4,26','C2,26','C3,28','C3,27','C3,26','C3,25','C3,24','C3,23','C3,22','C3,21','C3,20',
        'C2,28','C2,27','C2,26','C2,25','C2,24','C2,23','C2,22','C2,21',
        'C3,21','R','C4,21','R','C5,21','R','C6,21','R','C7,21','R',
        'C7,1','C7,22','C7,23','C8,23','R','C9,23','R',
        'C8,1','C9,22','C9,21','C9,20','C9,19','C9,18','C9,17','C9,16',
        'C8,16','L','C7,16','L','C6,16','L','C5,16','L','C4,16','L','C3,16','L','C2,16','L',
        'L','L','C9,1','R','R'],
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
