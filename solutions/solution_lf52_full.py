"""LF52 complete solve: L1 + L2 + L3 as MCP-ready action list.

L1 (8 actions, baseline 24): straightforward peg-solitaire chain.
L2 (35 actions, baseline 81): transition-as-vehicle mechanic discovered 2026-04-14.
L3 (46 actions, baseline 74): world shifts = viewport tracking (cracked 2026-04-14).

Total: 89 actions vs baseline 179 (50% under).

To execute on an MCP-connected ARC-AGI session, feed each step to arc-see step tool:
  ('C', (x1,y1), (x2,y2)) → 2 clicks: ACTION6 x=x1 y=y1, then ACTION6 x=x2 y=y2
  ('A', n)                → ACTIONn

Current MCP state after restart should be L1 init (levels_completed=0).
"""

LF52_FULL_SOLVE = [
    # ---------- L1 (8 clicks) ----------
    ('C', (18, 19), (30, 19)),
    ('C', (30, 19), (42, 19)),
    ('C', (42, 19), (42, 31)),
    ('C', (42, 31), (42, 43)),

    # ---------- L2 (35 actions) ----------
    ('C', (14, 16), (26, 16)),
    ('C', (26, 16), (38, 16)),
    ('A', 4), ('A', 4), ('A', 4), ('A', 4),
    ('A', 1), ('A', 1), ('A', 1), ('A', 3),
    ('C', (38, 16), (50, 16)),
    ('A', 4),
    ('A', 2), ('A', 2), ('A', 2),
    ('A', 3), ('A', 3), ('A', 3), ('A', 3),
    ('A', 3), ('A', 3), ('A', 3), ('A', 3),
    ('A', 2), ('A', 2), ('A', 2),
    ('A', 4), ('A', 4), ('A', 4), ('A', 4),
    ('C', (38, 52), (50, 52)),

    # ---------- L3 (46 actions) ----------
    ('C', (13, 13), (13, 25)),
    ('C', (13, 25), (25, 25)),
    ('C', (25, 25), (25, 13)),
    ('A', 3),
    ('C', (25, 13), (37, 13)),
    ('A', 4), ('A', 4),
    ('C', (62, 19), (51, 19)),
    ('C', (62, 31), (51, 31)),
    ('A', 4),
    ('C', (31, 13), (43, 13)),
    ('C', (43, 13), (43, 25)),
    ('C', (43, 25), (43, 37)),
    ('C', (43, 37), (43, 49)),
    ('A', 1), ('A', 1), ('A', 4), ('A', 4), ('A', 2), ('A', 2), ('A', 4),
    ('C', (49, 49), (38, 49)),
    ('A', 3), ('A', 1), ('A', 1), ('A', 3), ('A', 3), ('A', 2), ('A', 2), ('A', 3), ('A', 3),
    ('C', (29, 47), (19, 49)),
    ('C', (11, 47), (25, 49)),
]


def count_steps():
    n = 0
    for s in LF52_FULL_SOLVE:
        n += 2 if s[0] == 'C' else 1
    return n


if __name__ == '__main__':
    import sys
    sys.path.insert(0, '/Users/kairos/Projects/arc-see')
    from lf52_tool import LF52

    # Verify full solve against local game engine
    g = LF52(up_to_level=1)  # Fresh L1 start
    print(f'L1 init: lvl={g.obs.levels_completed}')
    for s in LF52_FULL_SOLVE:
        if s[0] == 'C':
            g.click(*s[1]); g.click(*s[2])
        else:
            g.action(s[1])
    print(f'Final: lvl={g.obs.levels_completed}, state={g.obs.state.name}')
    print(f'Total actions: {count_steps()}')
    assert g.obs.levels_completed >= 3, 'L3 not solved'
    print('OK — L1+L2+L3 all solved')
