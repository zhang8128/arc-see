"""LF52 L4 partial solve (45 actions) — does NOT win L4 yet.

Works with lf52_tool.py (reset_to_l4 after L1+L2+L3 auto-replay).

State progression:
- Start L4: 3 e-pieces (main row B tiles 1 and 6; sub-panel tile 1)
- After 45 actions: big expanded world, loaded bottom vehicle, still lvl=3

Key mechanics discovered:
- Click e (green select) if adjacent filled (f or e)
- Click red hint to execute peg-jump
- Jumping INTO vehicle c-interior LOADS it → triggers world expansion (+3 color-7)
- Loaded e click + red hint UNLOADS, chain-absorbs adjacent e's along slide path
- A3/A4 move the bottom empty vehicle (not the loaded one) by 6 cols
- 2 A4's after first load trigger second expansion (+6 color-7 total)
- Horizontal jumps work when ANOTHER e can serve as pivot (not just f)

Unsolved: what is the L4 WIN condition? Candidates:
- Reduce to 1 e-piece total (we're at 1 whole + partials)
- Cover all f-containers with e-pieces
- Get specific e-piece to specific target location
- Fill a specific vehicle multiple times

Usage:
    uv run python solutions/solution_lf52_l4_partial.py
"""

L4_PARTIAL = [
    # Phase 1: consolidate main panel row B (4 actions)
    ('C', (13, 25), (25, 25)),  # e1 jump e3 via f2
    ('C', (25, 25), (37, 25)),  # e3 jump e5 via f4

    # Phase 2: move vehicle, load first piece into top vehicle (3 actions + 2 clicks)
    ('A', 3),
    ('C', (37, 25), (49, 25)),  # slide-merge e5+e6 into top vehicle → LOADS + expands

    # Phase 3: expand viewport with A4×4 (4 actions)
    ('A', 4), ('A', 4), ('A', 4), ('A', 4),

    # Phase 4: unload loaded vehicle — absorbs middle e, lands at (31,25) (2 clicks)
    ('C', (19, 25), (31, 25)),  # unload → 2 pieces at (31,25), (49,25)

    # Phase 5: both pieces down-jump through mid-f and bottom-f (4 pairs = 8 clicks)
    ('C', (31, 25), (31, 37)),  # e jump down via mid f
    ('C', (49, 25), (49, 37)),
    ('C', (31, 37), (31, 49)),  # jump down via bottom f to bottom row
    ('C', (49, 37), (49, 49)),

    # Phase 6: merge + load bottom vehicle (2 pairs = 4 clicks)
    ('C', (49, 49), (37, 49)),  # e2 left-jump via f at (43,49) to (37,49)
    ('C', (37, 49), (25, 49)),  # e2 left-jump over e1 as pivot into bot vehicle → LOADS + expands more
]


def count_steps():
    n = 0
    for s in L4_PARTIAL:
        n += 2 if s[0] == 'C' else 1
    return n


def run_and_report():
    import sys
    sys.path.insert(0, '/Users/kairos/Projects/arc-see')
    from lf52_tool import LF52
    import numpy as np

    g = LF52(up_to_level=4)
    print(f'Start L4: lvl={g.obs.levels_completed}, e-count={(g.pixels()==14).sum()}, 7={(g.pixels()==7).sum()}')
    for s in L4_PARTIAL:
        if s[0] == 'C':
            g.click(*s[1])
            g.click(*s[2])
        else:
            g.action(s[1])
    pix = g.pixels()
    print(f'After {count_steps()} actions: lvl={g.obs.levels_completed}, state={g.obs.state.name}')
    print(f'  e-count={(pix==14).sum()}, 7={(pix==7).sum()}, f={(pix==15).sum()}')


if __name__ == '__main__':
    run_and_report()
