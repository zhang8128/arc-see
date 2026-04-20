"""LF52 complete solution — all 10 levels.

L1-L6 replay uses hardcoded click/A-action sequences baked into
`lf52_tool.LF52(up_to_level=7)`. L7-L10 are inlined below.

L7: 2-phase solve (chains 1-8 via fixed pixel clicks; bridge plan via
    grid-coord chains) — ~130 ops.
L8: BFS-found chain sequence — 47 ops. Final chain consumes reg2.
L9: Chain cascade across row 2 + col-21 descent + row-5 merge — 56 ops.
L10: 3-phase decomposition (load reg1 on V, drive to (2,6), blue-shuffle
     + reg2 consume) — 41 ops.

Run: `uv run python solutions/solution_lf52.py`  (~1.3s end-to-end).
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
DIR_A = {U: 1, D: 2, L: 3, R: 4}


# ======================================================================
# Shared helper: chain-via-click with viewport-aware pixel conversion.
# ======================================================================

def _click_chain(g, src_grid, direction):
    vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    sx = src_grid[0] * 6 + 3 + vp[0]
    sy = src_grid[1] * 6 + 3 + vp[1]
    g.click(sx, sy)
    vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    tx = (src_grid[0] + 2 * direction[0]) * 6 + 3 + vp[0]
    ty = (src_grid[1] + 2 * direction[1]) * 6 + 3 + vp[1]
    g.click(tx, ty)


# ======================================================================
# L7 — chains 1-8 (fixed-pixel clicks) + bridge plan (grid chains).
# ======================================================================

L7_PHASE_A = [
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

L7_BRIDGE = [
    ('C', R, (9, 8)),
    ('A', 1), ('A', 3), ('A', 3), ('A', 1), ('A', 1), ('A', 4),
    ('A', 1), ('A', 1), ('A', 4), ('A', 4), ('A', 4),
    ('C', R, (12, 3)),
    ('A', 3), ('A', 3), ('A', 3), ('A', 2), ('A', 2), ('A', 4), ('A', 4), ('A', 2),
    ('C', U, (11, 8)),
    ('A', 1), ('A', 3), ('A', 3), ('A', 1), ('A', 1), ('A', 4), ('A', 4),
    ('A', 1), ('A', 1), ('A', 4), ('A', 4), ('A', 4), ('A', 2),
    ('C', D, (14, 2)),
    ('C', D, (14, 3)),
    ('C', D, (14, 4)),
    ('C', R, (14, 6)),
    ('C', R, (16, 6)),
    ('C', R, (14, 5)),
    ('C', R, (16, 5)),
    ('A', 2), ('A', 4), ('A', 2), ('A', 2), ('A', 3), ('A', 3), ('A', 3), ('A', 2), ('A', 2),
    ('C', U, (18, 6)),
    ('A', 1), ('A', 1), ('A', 4), ('A', 2), ('A', 4), ('A', 4), ('A', 4), ('A', 2),
    ('C', D, (22, 3)),
    ('A', 1), ('A', 3), ('A', 1), ('A', 3), ('A', 3), ('A', 2), ('A', 4), ('A', 2), ('A', 2),
    ('C', U, (22, 6)),  # WIN L7
]


def _apply_l7(g):
    for op in L7_PHASE_A:
        if op[0] == 'A':
            g.action(op[1])
        else:
            g.click(op[1], op[2])
    for op in L7_BRIDGE:
        if op[0] == 'A':
            g.action(op[1])
        else:
            _, direction, src = op
            _click_chain(g, src, direction)


# ======================================================================
# L8 — BFS-derived 47-op sequence.
# ======================================================================

L8_SOLUTION = [
    ('A', 3), ('A', 3), ('A', 1), ('A', 1), ('A', 1), ('A', 1), ('A', 3), ('A', 4),
    ('C', U, (4, 7)),
    ('C', U, (4, 6)),
    ('C', U, (4, 5)),
    ('C', L, (8, 11)),
    ('C', L, (7, 11)),
    ('C', L, (6, 11)),
    ('C', L, (5, 11)),
    ('C', R, (1, 3)),
    ('C', R, (3, 3)),
    ('C', D, (4, 3)),
    ('C', R, (5, 3)),
    ('C', D, (7, 3)),
    ('C', L, (7, 5)),
    ('C', L, (5, 5)),
    ('C', L, (3, 5)),
    ('A', 3), ('A', 2), ('A', 2), ('A', 2), ('A', 2), ('A', 4), ('A', 4), ('A', 4), ('A', 2), ('A', 3), ('A', 3),
    ('C', D, (3, 10)),
    ('A', 4), ('A', 4), ('A', 4), ('A', 4),
    ('C', R, (3, 11)),
    ('C', R, (4, 11)),
    ('C', R, (5, 11)),
    ('C', U, (7, 12)),
    ('A', 1), ('A', 4), ('A', 1),
    ('C', U, (8, 8)),  # WIN L8
]


def _apply_l8(g):
    for op in L8_SOLUTION:
        if op[0] == 'A':
            g.action(op[1])
        else:
            _, direction, src = op
            _click_chain(g, src, direction)


# ======================================================================
# L9 — chain cascade + row-5 merge.
# ======================================================================

L9_SOLUTION = [
    ('C', L, (21, 2)),
    ('C', L, (20, 2)),
    ('C', L, (19, 2)),
    ('C', L, (18, 2)),
    ('C', L, (17, 2)),
    ('C', L, (16, 2)),
    ('C', L, (15, 2)),
    ('C', L, (14, 2)),
    ('C', L, (13, 2)),
    ('C', U, (3, 7)),
    ('C', D, (11, 1)),
    ('C', R, (11, 2)),
    ('C', R, (12, 2)),
    ('C', R, (11, 3)),
    ('C', U, (13, 3)),
    ('C', R, (13, 2)),
    ('C', R, (14, 2)),
    ('C', R, (15, 2)),
    ('C', R, (16, 2)),
    ('C', R, (13, 1)),
    ('C', R, (15, 1)),
    ('C', D, (17, 1)),
    ('C', R, (17, 2)),
    ('C', R, (18, 2)),
    ('C', R, (19, 2)),
    ('C', R, (17, 3)),
    ('C', R, (19, 3)),
    ('C', D, (21, 2)),
    ('C', D, (21, 3)),
    ('C', R, (2, 6)),
    ('C', U, (3, 6)),
    ('C', U, (3, 5)),
    ('C', U, (3, 4)),
    ('C', R, (3, 2)),
    ('C', D, (5, 2)),
    ('C', D, (5, 3)),
    ('C', D, (5, 4)),
    ('C', D, (5, 5)),
    ('C', L, (6, 7)),
    ('C', U, (5, 7)),
    ('C', U, (4, 7)),
    ('C', R, (4, 5)),
    ('A', 4), ('A', 4), ('A', 4), ('A', 4), ('A', 4), ('A', 4), ('A', 4),
    ('A', 4), ('A', 4), ('A', 4), ('A', 4), ('A', 4), ('A', 4), ('A', 4),
    ('C', R, (20, 5)),  # WIN L9
]


def _apply_l9(g):
    for op in L9_SOLUTION:
        if op[0] == 'A':
            g.action(op[1])
        else:
            _, direction, src = op
            _click_chain(g, src, direction)


# ======================================================================
# L10 — 3-phase: load reg1 on V, drive to (2,6), consume reg2 via
# chain choreography. Uses an in-process sim to resolve click positions
# by piece ID (since phase-3 chains target specific pieces that move
# around during the sequence).
# ======================================================================

L10_PLAN = [
    # Phase 1: load reg1 on V at (4, 2)
    ('A', U), ('A', U), ('A', U), ('A', U),
    ('A', U), ('A', U), ('A', U), ('A', U),
    ('A', R),
    ('A', L),
    ('A', D),
    ('A', L), ('A', L), ('A', L),
    ('C', 'reg1', D),
    # Phase 2: drive V+reg1 to (2, 6)
    ('A', L),
    ('A', U),
    ('A', L), ('A', L),
    ('C', 'reg1', L),
    ('A', D), ('A', D), ('A', D), ('A', D), ('A', D),
    ('A', R), ('A', R),
    # Phase 3: blue-shuffle + reg2 consume
    ('C', 'blue2', L),
    ('C', 'blue1', L),
    ('C', 'blue1', D),
    ('C', 'blue3', D),
    ('C', 'blue1', R),
    ('C', 'blue5', R),
    ('C', 'blue3', R),
    ('C', 'blue4', D),
    ('C', 'blue5', R),
    ('C', 'reg2', U),
    ('C', 'reg2', L),
    ('C', 'blue1', L),
    ('C', 'reg2', L),
    ('C', 'reg1', D),  # consumes reg2 → WIN L10
]


def _bootstrap_l10_sim(g):
    """Build an l7_sim.Sim from live engine state — used for L10 only."""
    from l7_sim import Sim

    ik = g.env._game.ikhhdzfmarl
    grid = ik.hncnfaqaddg
    W, H = grid.ksfoftduxiu, grid.kfiapdsgfly

    static = {}
    piece_pos = {}
    vehicle_pos = []
    dgx_pos = []

    for x in range(W):
        for y in range(H):
            names = [s.name for s in grid.ijpoqzvnjt(x, y)]
            if names:
                static_names = tuple(
                    n for n in names
                    if 'fozwvlovdui' not in n
                    and n != 'hupkpseyuim2'
                    and n != 'dgxfozncuiz'
                )
                if static_names:
                    static[(x, y)] = static_names

    reg_count = 0
    blue_count = 0
    for s in grid.xpnsbxlatu:
        n = s.name
        pos = tuple(s.chahdtpdoz)
        if n == 'fozwvlovdui':
            reg_count += 1
            piece_pos[f'reg{reg_count}'] = pos
        elif n == 'fozwvlovdui_red':
            piece_pos['red'] = pos
        elif n == 'fozwvlovdui_blue':
            blue_count += 1
            piece_pos[f'blue{blue_count}'] = pos
        elif n == 'hupkpseyuim2':
            vehicle_pos.append(pos)
        elif n == 'dgxfozncuiz':
            dgx_pos.append(pos)

    return Sim(
        static_cells=static,
        grid_w=W,
        grid_h=H,
        piece_pos=tuple(sorted(piece_pos.items())),
        vehicle_pos=tuple(sorted(vehicle_pos)),
        dgx_pos=tuple(sorted(dgx_pos)),
    )


def _apply_l10(g):
    sim = _bootstrap_l10_sim(g)
    for op in L10_PLAN:
        if op[0] == 'A':
            g.action(DIR_A[op[1]])
            sim = sim.do_action(op[1])
        else:
            _, pid, direction = op
            src = dict(sim.piece_pos)[pid]
            _click_chain(g, src, direction)
            sim = sim.do_chain(pid, direction)


# ======================================================================
# Orchestrator.
# ======================================================================

def solve(verbose=True):
    from lf52_tool import LF52

    g = LF52(up_to_level=7, verbose=False)
    if verbose:
        print(f'L1-L6 replay: levels_completed={g.level()}')

    for level, apply in [(7, _apply_l7), (8, _apply_l8), (9, _apply_l9), (10, _apply_l10)]:
        apply(g)
        if verbose:
            print(f'After L{level}: levels_completed={g.level()} state={g.obs.state.name}')
    return g


if __name__ == '__main__':
    import time
    t = time.time()
    g = solve()
    print(f'\nTotal runtime: {time.time()-t:.2f}s')
    if g.obs.state.name == 'WIN' and g.obs.levels_completed >= 10:
        print('*** LF52 FULLY SOLVED (25/25 complete) ***')
    else:
        print(f'!!! Unexpected final state: {g.obs.state.name} levels={g.obs.levels_completed}')
