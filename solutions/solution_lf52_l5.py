"""LF52 L5 solution — 67 actions, found via BFS simulator.

Strategy: Route piece (1, 3) through Panel #2 → Panel #4 (via v2's dgx pivot at col 4
and v3's dgx pivot at col 17) and into Panel #7 where it chain-consumes piece (16, 8)
as pivot. Final piece ends at (14, 8). All 5 consumable pieces (1, 3), (6, 3), (11, 3),
(18, 4), (19, 0) are consumed along the way as pivots for the traveling piece.

Architecture: The two disconnected tracks can't bridge vehicles, but PIECES can traverse
between tracks via panel cells when loaded-vehicle pivots are positioned at the right
track cells. Vehicle 3's dgx (carried from P cell) is the ONLY mobile pivot on Track #1.

Usage:
    uv run python solutions/solution_lf52_l5.py
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

# 67-action solution found via l5_sim BFS.
# Format: 'A<n>' for ACTION<n>, 'C(x, y)D' for chain at piece grid (x, y) direction D.
SOLUTION = [
    'A4', 'A4', 'A4',           # v1 → (4,0) T (v2 blocked at (7,0))
    'A3',                        # v2 (7,0) tries left blocked, v3 (20,1) → (19,1)... actually v1 ←
    'A2', 'A2', 'A2',
    'A3', 'A3',
    'A2', 'A2', 'A2',
    'A4', 'A4',
    'A2',
    'A4',
    'A1',
    'A3', 'A3', 'A3', 'A3', 'A3',
    # Setup complete
    ('C', (1, 3), (1, 0)),       # (1,3) → (3,3) via dgx (2,3)
    ('C', (3, 3), (1, 0)),       # (3,3) → (5,3) via v2's dgx at (4,3)
    'A1', 'A1',
    ('C', (5, 3), (1, 0)),       # (5,3) → (7,3)=loaded v1, consuming (6,3)
    'A1',
    'A4', 'A4', 'A4',
    'A2',
    ('C', (10, 3), (1, 0)),      # (10,3) loaded → (12,3), consuming (11,3)
    ('C', (12, 3), (1, 0)),      # (12,3) → (14,3) via v3's dgx at (13,3)
    'A1', 'A1',
    'A4', 'A4', 'A4', 'A4',
    'A2', 'A2',
    ('C', (14, 3), (1, 0)),      # (14,3) → (16,3) via static pivot (15,3)
    ('C', (16, 3), (1, 0)),      # (16,3) → (18,3) via v3's dgx at (17,3)
    'A1', 'A1',
    'A4',
    ('C', (18, 4), (0, -1)),     # (18,4) consumes itself via chain UP over (18,3) piece → (18,2)
    ('C', (18, 2), (0, -1)),     # (18,2) → (18,0) via v3's dgx at (18,1)
    'A3', 'A3', 'A3',
    ('C', (19, 0), (-1, 0)),     # (19,0) → (17,0) via (18,0) piece-pivot (CONSUMES (18,0))
    ('C', (17, 0), (-1, 0)),     # (17,0) → (15,0) via dgx (16,0)
    ('C', (15, 0), (0, 1)),      # (15,0) → (15,2) via v3's dgx at (15,1)
    'A3', 'A3',
    'A2', 'A2', 'A2', 'A2',
    'A4', 'A4',
    ('C', (15, 2), (0, 1)),      # (15,2) → (15,4) via dgx (15,3)
    ('C', (15, 4), (0, 1)),      # (15,4) → (15,6) via v3's dgx at (15,5)
    ('C', (15, 6), (0, 1)),      # (15,6) → (15,8) via dgx (15,7)
    ('C', (16, 8), (-1, 0)),     # (16,8) → (14,8) via (15,8) piece-pivot (CONSUMES (15,8)). WIN!
]


def run():
    from lf52_tool import LF52
    from arcengine import GameAction

    g = LF52(up_to_level=1, verbose=False)
    g.env._game.set_level(4)
    g.env._game.on_set_level(g.env._game.current_level)
    g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})

    for i, step in enumerate(SOLUTION):
        if isinstance(step, str):
            a = int(step[1:])
            g.env.step(getattr(GameAction, f'ACTION{a}'))
        else:
            kind, src, direction = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            sx, sy = src
            dx, dy = direction
            # Click piece
            g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            # Click dest
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            dest_x = (sx + 2*dx)*6 + 3 + ox
            dest_y = (sy + 2*dy)*6 + 3 + oy
            obs = g.env.step(GameAction.ACTION6, data={'x': dest_x, 'y': dest_y})

        foz = sum(1 for item in g.env._game.ikhhdzfmarl._sorted_cache if getattr(item[1], 'name', '') == 'fozwvlovdui')
        if i >= len(SOLUTION) - 10 or i < 5:
            print(f'Step {i+1:3d} {step}: foz={foz}')
    print(f'Final foz: {foz}, state: {g.env._game._state.name if hasattr(g.env._game, "_state") else "?"}')
    print(f'level: {g.env._game._current_level_index}')


if __name__ == '__main__':
    run()
