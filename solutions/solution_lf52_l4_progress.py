"""LF52 L4 progress — 19-action sequence that reaches deepest known state.

This is NOT a win; it's a mapped exploration frontier.

Reaches: 3 pieces at world (30, 54), (30, 78), (48, 42) [LOADED h2 at the arrow marker].
A2x2 further descends loaded h2 to (48, 54). Then pieces at col 30 remain unreachable.

KEY DISCOVERIES:
- 6 pieces → 4 pieces via 9-action opener
- 4 pieces → 3 pieces via full 15-action sequence (loads second vehicle h2@72,42)
- Loaded h2@72,42 driven via A3x4 to kraubslpehi-< marker at (48, 42)
- A2 mechanic: vertical move for the specific vehicle that reached (48, 42)
- Kraubslpehi goal markers form a rail path: (48, 42) left-arrow + (48, 48) up-arrow → (24, 18) main

BLOCKERS:
- Col-30 pieces at world (30, 54) and (30, 78) NEVER produce click hints across all tested states
- Engine says pieces are "clickable" but viewport click rejects them
- No path found to transport loaded h2@(48, 54) horizontally to col 30
- A1/A2 only works for specific vehicle at specific positions (caps quickly)

Usage:
    uv run python solutions/solution_lf52_l4_progress.py
"""

# 9-action opener (6 → 4 pieces)
OPENER = [
    ('A', 3),
    ('C', (13, 25), (25, 25)),
    ('C', (25, 25), (37, 25)),
    ('C', (37, 25), (49, 25)),
    ('A', 4), ('A', 4), ('A', 4), ('A', 4),
    ('C', (19, 25), (31, 25)),
]

# 15-action sequence (6 → 3 pieces, ends with loaded h2@72,42)
FIFTEEN = [
    ('C', (13, 25), (25, 25)),
    ('C', (25, 25), (37, 25)),
    ('A', 3),
    ('C', (37, 25), (49, 25)),
    ('A', 4), ('A', 4), ('A', 4), ('A', 4),
    ('C', (19, 25), (31, 25)),
    ('C', (31, 25), (31, 37)),
    ('C', (31, 37), (31, 49)),
    ('C', (49, 25), (49, 37)),
    ('C', (49, 37), (49, 49)),
    ('C', (49, 49), (37, 49)),
    ('C', (37, 49), (25, 49)),
]

# 19-action sequence: adds A3×4 to drive loaded h2 to arrow marker (48, 42)
NINETEEN = FIFTEEN + [('A', 3)] * 4

# 21-action sequence: A2×2 descends loaded h2 to (48, 54)
TWENTY_ONE = NINETEEN + [('A', 2), ('A', 2)]


def run(sequence, label):
    import sys
    sys.path.insert(0, '/Users/kairos/Projects/arc-see')
    from lf52_tool import LF52
    from collections import defaultdict

    g = LF52(up_to_level=4, verbose=False)
    for step in sequence:
        if step[0] == 'C':
            g.click(*step[1])
            g.click(*step[2])
        else:
            g.action(step[1])
    sm = defaultdict(list)
    for item in g.env._game.ikhhdzfmarl._sorted_cache:
        _, sp, _ = item
        sm[getattr(sp, 'name', '')].append((sp.x, sp.y))
    print(f'{label}: lvl={g.level()} foz={sorted(sm["fozwvlovdui"])}')


def main():
    run(OPENER, '9-action opener')
    run(FIFTEEN, '15-action seq')
    run(NINETEEN, '19-action seq')
    run(TWENTY_ONE, '21-action seq')


if __name__ == '__main__':
    main()
