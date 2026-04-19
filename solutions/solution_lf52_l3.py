"""LF52 Level 3 solution. 46 actions vs baseline 74 (38% reduction).

Key insight: world shifts via loaded trans reveal hidden pieces. After loading both
transitions in sequence and navigating through corridors, a final 2-piece merge completes
the level.

Requires L1 (8 actions) + L2 (35 actions) executed first.
"""

# Solve steps: ('C', (x1,y1), (x2,y2)) = click piece then hint.  ('A', n) = ACTION n.
L3_SOLVE = [
    # M1, M2, M3 — panel-A consolidation via P6/P5 corridors
    ('C', (13, 13), (13, 25)),   # P1 + P4 → (13, 25)
    ('C', (13, 25), (25, 25)),   # merged + P6 → (25, 25) rightward
    ('C', (25, 25), (25, 13)),   # merged + P5 → (25, 13) upward
    # Load top trans with merged piece (absorbs P2 en route)
    ('A', 3),                     # move both trans left 6 cols
    ('C', (25, 13), (37, 13)),   # slide merged into top trans (loaded)
    # Shift viewport right to reveal right panel
    ('A', 4), ('A', 4),
    # Consume 2 right-edge pieces via peg-solitaire
    ('C', (62, 19), (51, 19)),
    ('C', (62, 31), (51, 31)),
    # Shift once more, then merge loaded trans right
    ('A', 4),
    ('C', (31, 13), (43, 13)),   # loaded trans + (37,13) → (43, 13)
    # Col-43 chain: vertical cascade to bottom panel
    ('C', (43, 13), (43, 25)),
    ('C', (43, 25), (43, 37)),
    ('C', (43, 37), (43, 49)),
    # Reposition bot trans to init (x=36) — enables bot-trans load
    ('A', 1), ('A', 1), ('A', 4), ('A', 4), ('A', 2), ('A', 2), ('A', 4),
    # Load bot trans (absorbs col-43-chain-end piece + P8 shifted)
    ('C', (49, 49), (38, 49)),
    # Navigate loaded bot trans to reveal bottom-left pieces
    ('A', 3), ('A', 1), ('A', 1), ('A', 3), ('A', 3), ('A', 2), ('A', 2), ('A', 3), ('A', 3),
    # Final 2-piece merges — consolidates to win
    ('C', (29, 47), (19, 49)),   # loaded trans + 1 piece → (19, 49)
    ('C', (11, 47), (25, 49)),   # merges last two pieces → WIN L3
]


def apply(env_step, step):
    """Apply one step to a callable env_step(action_name, data=None)."""
    if step[0] == 'C':
        env_step('ACTION6', data={'x': step[1][0], 'y': step[1][1]})
        env_step('ACTION6', data={'x': step[2][0], 'y': step[2][1]})
    elif step[0] == 'A':
        env_step(f'ACTION{step[1]}')


if __name__ == '__main__':
    # Verify against local engine
    import sys
    sys.path.insert(0, '/Users/kairos/Projects/arc-see')
    from lf52_tool import LF52

    g = LF52(up_to_level=3)
    print(f'L3 init: lvl={g.obs.levels_completed}')
    for step in L3_SOLVE:
        if step[0] == 'C':
            g.click(*step[1]); g.click(*step[2])
        else:
            g.action(step[1])
    print(f'After L3 solve: lvl={g.obs.levels_completed}, state={g.obs.state.name}')
    assert g.obs.levels_completed >= 3, 'L3 not solved'
    print('OK — L3 solved')
