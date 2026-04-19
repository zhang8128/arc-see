"""LF52 L10 solution — 41 actions from L10 init.

Discovered via 3-phase BFS/A* (sim validated against engine):
  Phase 1 (15): load reg1 onto V at (4, 2) via blue pivot at (4, 1),
    using train-top blue carried across row 1 to (4, 1).
  Phase 2 (12): drive V+reg1 to (2, 6) via a mid-route blue-swap
    (reg1 unloaded at (0, 1) onto another V, then col-0 descent).
  Phase 3 (14): blue choreography to bring reg2 to (2, 7) adjacent to
    V+reg1 at (2, 6). Final chain: reg1 D via reg2 pivot → consume reg2.
    ddaguepwkt = 12 - 10 - 1 = 1 → WIN.

The chain ops are encoded in grid-coords; the helper at
solutions/solution_lf52_l7.py exposes `click_chain(g, src, direction)`
which converts grid → pixel via viewport offset.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
DIR_A = {U: 1, D: 2, L: 3, R: 4}


# Full 41-action plan.  Ops: ('A', dir) or ('C', piece_id, dir).
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
    # === Phase 3: blue-shuffle + reg2 to (2, 7) + final consume ===
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


def _sim_find_piece_grid(sim, pid_logical, iter_state):
    """Map logical piece_id ('reg1'/'reg2'/'blueN') to its current grid cell
    AND return the right sprite-name for engine click dispatch.

    Sim piece IDs are fixed (reg1/reg2, blue1..blue10). In the engine,
    pieces don't have these IDs — the click handler `rozmjeilxc` just
    finds the topmost fozwvlovdui* sprite at the clicked tile. So we
    locate by position: take the sim's current position for `pid_logical`
    and click there.
    """
    pieces = dict(iter_state.piece_pos)
    return pieces[pid_logical]


def apply_solution(g):
    """Apply L10 solution to a live `lf52_tool.LF52` game at L10 init.
    Returns (levels_completed, score)."""
    from l7_sim import load_init

    sim = load_init('/tmp/l10_init.json')

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
            src = _sim_find_piece_grid(sim, pid, sim)
            click_chain(src, direction)
            sim = sim.do_chain(pid, direction)
    return g


if __name__ == '__main__':
    # Prepare engine at L10 init and verify
    from l10_workspace import make_l10_game
    g = make_l10_game()
    ik = g.env._game.ikhhdzfmarl
    print(f'Start: level={ik.whtqurkphir}, levels_completed={g.obs.levels_completed}')
    apply_solution(g)
    print(f'After: level={ik.whtqurkphir}, levels_completed={g.obs.levels_completed}, state={g.obs.state.name}')
    grid = ik.hncnfaqaddg
    foz = [(s.name, tuple(s.chahdtpdoz)) for s in grid.xpnsbxlatu if 'fozwvlovdui' in s.name]
    print(f'foz remaining: {foz}')
    if g.obs.levels_completed >= 10 or g.obs.state.name == 'WIN':
        print('\n*** L10 SOLVED! ***')
    else:
        print(f'\nL10 not yet complete. state={g.obs.state.name}')
