"""LF52 L6 solution — 55 actions, found via BFS simulator.

L6 introduces: red piece (fozwvlovdui_red). Win at foz count == 2.

Strategy:
1. Chain red piece (2, 2) down through Panel A to (6, 6) (end of row 6 track before t-junction).
2. Drive v1 along row 6 and Panel B pivots to consume pieces (15, 2) area.
3. Cascade pieces through Panel C into Panel D via col 25/23 tracks.
4. Final state: red piece + 1 regular piece.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

SOLUTION_STR = "A2 A2 C(2, 2)D C(2, 3)D C(2, 4)D C(2, 5)D C(1, 7)R C(3, 8)U C(2, 6)R C(3, 6)R C(4, 6)R C(5, 6)R C(6, 6)R A4 A4 A1 A4 A4 A4 A4 A4 A1 A4 A4 A1 A1 C(14, 4)U C(14, 2)R C(17, 4)U C(16, 2)R C(17, 2)R C(18, 2)R C(19, 2)R C(20, 2)R C(21, 2)R C(22, 2)R C(23, 2)R C(24, 2)R A2 A2 C(26, 2)D C(26, 4)L A2 A2 A3 A3 A1 A1 C(24, 4)L A2 A2 C(22, 4)D C(23, 6)L C(22, 6)L C(20, 6)D"


def parse_solution():
    """Parse the space-separated solution string into steps."""
    tokens = SOLUTION_STR.split()
    steps = []
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t.startswith('A'):
            steps.append(('A', int(t[1:])))
            i += 1
        elif t.startswith('C('):
            # e.g., "C(2," then "2)D"
            # Find the closing paren
            full = t
            while ')' not in full:
                i += 1
                full += ' ' + tokens[i]
            # full = "C(2, 2)D"
            paren_end = full.index(')')
            coords = full[2:paren_end]
            sx, sy = [int(v.strip()) for v in coords.split(',')]
            direction_char = full[paren_end+1:]
            direction = {'U': (0, -1), 'D': (0, 1), 'L': (-1, 0), 'R': (1, 0)}[direction_char]
            steps.append(('C', (sx, sy), direction))
            i += 1
        else:
            i += 1
    return steps


def run():
    from lf52_tool import LF52
    from arcengine import GameAction

    g = LF52(up_to_level=1, verbose=False)
    # Skip to L6
    for _ in range(5):
        g.env._game.set_level(g.env._game._current_level_index + 1)
    g.env._game.on_set_level(g.env._game.current_level)
    obs = g.env.step(GameAction.ACTION6, data={'x': 0, 'y': 0})

    def foz_total():
        return sum(1 for item in g.env._game.ikhhdzfmarl._sorted_cache if getattr(item[1], 'name', '').startswith('fozwvlovdui'))

    steps = parse_solution()
    print(f'Parsed {len(steps)} steps')
    print(f'Init: foz={foz_total()}, level={g.env._game._current_level_index}')

    for i, step in enumerate(steps):
        if step[0] == 'A':
            a = step[1]
            obs = g.env.step(getattr(GameAction, f'ACTION{a}'))
        else:
            _, (sx, sy), (dx, dy) = step
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            g.env.step(GameAction.ACTION6, data={'x': sx*6+3+ox, 'y': sy*6+3+oy})
            ox, oy = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
            obs = g.env.step(GameAction.ACTION6, data={'x': (sx+2*dx)*6+3+ox, 'y': (sy+2*dy)*6+3+oy})
        if i < 10 or i >= len(steps) - 5 or foz_total() != 8 + (0 if i == 0 else 0):
            pass  # comment out prints for speed
    print(f'After {len(steps)} steps: foz={foz_total()}, level_index={g.env._game._current_level_index}, levels_completed={obs.levels_completed}, state={obs.state.name}')


if __name__ == '__main__':
    run()
