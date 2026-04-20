"""LF52 L10 solution — 41 actions from L10 init.

Discovered via 3-phase BFS/A* (sim validated against engine):
  Phase 1 (15): load reg1 onto V at (4, 2) via blue pivot at (4, 1),
    using train-top blue carried across row 1 to (4, 1).
  Phase 2 (12): drive V+reg1 to (2, 6) via a mid-route blue-swap
    (reg1 unloaded at (0, 1) onto another V, then col-0 descent).
  Phase 3 (14): blue choreography to bring reg2 to (2, 7) adjacent to
    V+reg1 at (2, 6). Final chain: reg1 D via reg2 pivot → consume reg2.
    ddaguepwkt = 12 - 10 - 1 = 1 → WIN.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
DIR_A = {U: 1, D: 2, L: 3, R: 4}


# PLAN uses sim piece IDs (stable through the run). A runtime sim tracks
# where each piece is, so click coordinates can be resolved at click time.
PLAN = [
    # === Phase 1: load reg1 on V at (4, 2) ===
    ('A', U), ('A', U), ('A', U), ('A', U),
    ('A', U), ('A', U), ('A', U), ('A', U),
    ('A', R),
    ('A', L),
    ('A', D),
    ('A', L), ('A', L), ('A', L),
    ('C', 'reg1', D),
    # === Phase 2: drive V+reg1 to (2, 6) ===
    ('A', L),
    ('A', U),
    ('A', L), ('A', L),
    ('C', 'reg1', L),
    ('A', D), ('A', D), ('A', D), ('A', D), ('A', D),
    ('A', R), ('A', R),
    # === Phase 3: blue-shuffle + reg2 consume ===
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
    ('C', 'reg1', D),  # consume reg2 → WIN
]


def _bootstrap_sim(g):
    """Build a sim Sim instance from the current live engine state (no json needed)."""
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


def apply_solution(g):
    """Apply L10 plan to a live lf52_tool.LF52 game at L10 init."""
    sim = _bootstrap_sim(g)

    def click_chain(src_grid, direction):
        vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
        sx = src_grid[0] * 6 + 3 + vp[0]
        sy = src_grid[1] * 6 + 3 + vp[1]
        g.click(sx, sy)
        vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
        tx = (src_grid[0] + 2 * direction[0]) * 6 + 3 + vp[0]
        ty = (src_grid[1] + 2 * direction[1]) * 6 + 3 + vp[1]
        g.click(tx, ty)

    for op in PLAN:
        if op[0] == 'A':
            g.action(DIR_A[op[1]])
            sim = sim.do_action(op[1])
        else:  # 'C'
            _, pid, direction = op
            src = dict(sim.piece_pos)[pid]
            click_chain(src, direction)
            sim = sim.do_chain(pid, direction)
    return g


if __name__ == '__main__':
    from lf52_tool import LF52
    from solutions.solution_lf52_l7 import apply_solution as a7
    from solutions.solution_lf52_l8 import apply_solution as a8
    from solutions.solution_lf52_l9 import apply_solution as a9

    g = LF52(up_to_level=7, verbose=False)
    a7(g); a8(g); a9(g)
    print(f'L10 init: level={g.env._game.ikhhdzfmarl.whtqurkphir}, completed={g.obs.levels_completed}')
    apply_solution(g)
    print(f'After L10: completed={g.obs.levels_completed}, state={g.obs.state.name}')
    assert g.obs.levels_completed >= 10 and g.obs.state.name == 'WIN', 'L10 not solved'
    print('*** L10 SOLVED ***')
