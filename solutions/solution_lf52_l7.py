"""LF52 L7 solution — ~77 moves from chain-8 state.

Strategy:
1. Chain 9: reg1 R (9, 8) → (11, 8) via red(10, 8) pivot.
2. Bridge: DGX(13, 3) lets red chain off V-M at (12, 3).
   Then reg1 loads on V-M via DGX(11, 7), drives to (14, 2).
   Col-14 leapfrog ladder establishes foz at (14, 3)-(14, 6).
   Static DGXs (15, *), (17, *) bridge reg1 to (18, 6) and red to (18, 5).
3. Stage 1: R-vehicle shuffle so non-DGX V at (18, 4). Chain reg1 U
   (18, 6) → (18, 4) via red pivot. reg1 loaded.
4. Stage 2: drive V-reg1 to (22, 3). Chain reg1 D → (22, 5) via
   DGX-at-(22, 4) pivot.
5. Stage 3: shuffle R-vehicles so (22, 4) has V without DGX. Chain
   reg2 U via reg1(22, 5) pivot → reg1 consumed. WIN.
"""

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)


# Each op: ('A', action_num) or ('C', piece_id, direction, source_grid_pos).
# source_grid_pos is used to compute click screen coords dynamically (accounting for viewport).
SOLUTION = [
    # === Bridge plan (from chain-8 state) ===
    ('C', 'reg1', R, (9, 8)),
    # V-M with red drives (10, 8) → (12, 3)
    ('A', 1), ('A', 3), ('A', 3), ('A', 1), ('A', 1), ('A', 4),
    ('A', 1), ('A', 1), ('A', 4), ('A', 4), ('A', 4),
    ('C', 'red', R, (12, 3)),
    # V-M empty drives (12, 3) → (11, 6)
    ('A', 3), ('A', 3), ('A', 3), ('A', 2), ('A', 2), ('A', 4), ('A', 4), ('A', 2),
    ('C', 'reg1', U, (11, 8)),
    # V-M with reg1 drives (11, 6) → (14, 2)
    ('A', 1), ('A', 3), ('A', 3), ('A', 1), ('A', 1), ('A', 4), ('A', 4),
    ('A', 1), ('A', 1), ('A', 4), ('A', 4), ('A', 4), ('A', 2),
    # Col 14 ladder
    ('C', 'reg1', D, (14, 2)),
    ('C', 'red', D, (14, 3)),
    ('C', 'reg1', D, (14, 4)),
    # East bridges
    ('C', 'reg1', R, (14, 6)),
    ('C', 'reg1', R, (16, 6)),
    ('C', 'red', R, (14, 5)),
    ('C', 'red', R, (16, 5)),
    # === Stage 1: arrange V at (18, 4) no DGX, load reg1 ===
    ('A', 2), ('A', 4), ('A', 2), ('A', 2), ('A', 3), ('A', 3), ('A', 3), ('A', 2), ('A', 2),
    ('C', 'reg1', U, (18, 6)),
    # === Stage 2: drive V-reg1 to (22, 3), chain to (22, 5) ===
    ('A', 1), ('A', 1), ('A', 4), ('A', 2), ('A', 4), ('A', 4), ('A', 4), ('A', 2),
    ('C', 'reg1', D, (22, 3)),
    # === Stage 3: shuffle for DGX-free (22, 4), consume reg1 ===
    ('A', 1), ('A', 3), ('A', 1), ('A', 3), ('A', 3), ('A', 2), ('A', 4), ('A', 2), ('A', 2),
    ('C', 'reg2', U, (22, 6)),  # WIN
]


def click_chain(g, src, direction):
    """Execute a chain via two clicks, accounting for dynamic viewport."""
    vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    sx = src[0] * 6 + 3 + vp[0]
    sy = src[1] * 6 + 3 + vp[1]
    g.click(sx, sy)
    # Target click uses possibly-new viewport (if first click triggered scroll — unlikely mid-chain)
    vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    tx = (src[0] + 2 * direction[0]) * 6 + 3 + vp[0]
    ty = (src[1] + 2 * direction[1]) * 6 + 3 + vp[1]
    g.click(tx, ty)


def apply_solution(g):
    """Apply the L7 solution to a game `g` at chain-8 state."""
    for op in SOLUTION:
        if op[0] == 'A':
            g.action(op[1])
        else:
            _, pid, d, src = op
            click_chain(g, src, d)
