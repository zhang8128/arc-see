"""LF52 L7 solution — full from L7 init.

Phase A: verified chains 1-8 (click-based, fixed pixel coords per viewport).
Phase B: Bridge plan — red off V-M via DGX(13, 3), reg1 on V-M via DGX(11, 7),
         col-14 leapfrog, east bridges via DGXs (15, *) and (17, *).
Phase C: Final consumption — reg1 to (22, 5), reg2 U consumes reg1.
"""

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)


# Phase A: clicks and A-actions using screen-pixel coords (from verified harness).
PHASE_A = [
    # chain1
    ('A', 3), ('A', 3), ('A', 1), ('A', 1), ('A', 3), ('A', 3), ('A', 3),
    ('CLICK', 6, 12), ('CLICK', 6, 24),
    # chain2
    ('A', 4), ('A', 4), ('A', 4), ('A', 2), ('A', 2), ('A', 3), ('A', 3), ('A', 2),
    ('CLICK', 13, 44), ('CLICK', 13, 55),
    # load_lb
    ('A', 1), ('A', 4), ('A', 4), ('A', 1), ('A', 1), ('A', 4), ('A', 4), ('A', 4),
    ('CLICK', 42, 12), ('CLICK', 42, 24),
    # deliver_lb
    ('A', 3), ('A', 3), ('A', 3), ('A', 2), ('A', 2), ('A', 4), ('A', 4), ('A', 4), ('A', 2),
    ('CLICK', 43, 44), ('CLICK', 43, 55),
    # return_to_left
    ('A', 1), ('A', 3), ('A', 3), ('A', 3), ('A', 1), ('A', 1), ('A', 3), ('A', 3), ('A', 3),
    ('A', 4), ('A', 4), ('A', 4), ('A', 2), ('A', 2), ('A', 3), ('A', 3), ('A', 3), ('A', 2),
    # chain3..8
    ('CLICK', 13, 55), ('CLICK', 25, 55),
    ('CLICK', 25, 55), ('CLICK', 37, 55),
    ('CLICK', 37, 55), ('CLICK', 47, 55),
    ('CLICK', 43, 55), ('CLICK', 55, 55),
    ('CLICK', 5, 55), ('CLICK', 17, 55),
    ('A', 2), ('A', 3), ('A', 2), ('A', 2), ('A', 4), ('A', 4), ('A', 2),
    ('CLICK', 11, 55), ('CLICK', 23, 55),
]


# Phase B + C: bridge plan and final consumption (grid-coord chains, viewport-aware).
# Each op: ('A', action_num) or ('C', piece_id, direction, source_grid_pos).
SOLUTION_BRIDGE = [
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
    """Execute chain via two clicks, computing pixel coords from current viewport."""
    vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    sx = src[0] * 6 + 3 + vp[0]
    sy = src[1] * 6 + 3 + vp[1]
    g.click(sx, sy)
    vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    tx = (src[0] + 2 * direction[0]) * 6 + 3 + vp[0]
    ty = (src[1] + 2 * direction[1]) * 6 + 3 + vp[1]
    g.click(tx, ty)


def apply_phase_a(g):
    for op in PHASE_A:
        if op[0] == 'A':
            g.action(op[1])
        else:
            g.click(op[1], op[2])


def apply_solution(g):
    """Apply full L7 solution from L7 init state."""
    apply_phase_a(g)
    for op in SOLUTION_BRIDGE:
        if op[0] == 'A':
            g.action(op[1])
        else:
            _, pid, d, src = op
            click_chain(g, src, d)
