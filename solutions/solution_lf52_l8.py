"""LF52 L8 solution — 47 moves from L8 init. Found via BFS.
Final chain: reg1 UP from (8, 8) consumes reg2 at (8, 7) — both 'fozwvlovdui'.
"""

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)

SOLUTION = [
    ('A', 3), ('A', 3), ('A', 1), ('A', 1), ('A', 1), ('A', 1), ('A', 3), ('A', 4),
    ('C', 'blue2', U, (4, 7)),
    ('C', 'blue1', U, (4, 6)),
    ('C', 'blue2', U, (4, 5)),
    ('C', 'blue4', L, (8, 11)),
    ('C', 'blue3', L, (7, 11)),
    ('C', 'blue4', L, (6, 11)),
    ('C', 'blue3', L, (5, 11)),
    ('C', 'reg1', R, (1, 3)),
    ('C', 'reg1', R, (3, 3)),
    ('C', 'blue2', D, (4, 3)),
    ('C', 'reg1', R, (5, 3)),
    ('C', 'reg1', D, (7, 3)),
    ('C', 'reg1', L, (7, 5)),
    ('C', 'reg1', L, (5, 5)),
    ('C', 'reg1', L, (3, 5)),
    ('A', 3), ('A', 2), ('A', 2), ('A', 2), ('A', 2), ('A', 4), ('A', 4), ('A', 4), ('A', 2), ('A', 3), ('A', 3),
    ('C', 'reg1', D, (3, 10)),
    ('A', 4), ('A', 4), ('A', 4), ('A', 4),
    ('C', 'blue3', R, (3, 11)),
    ('C', 'blue4', R, (4, 11)),
    ('C', 'blue3', R, (5, 11)),
    ('C', 'reg1', U, (7, 12)),
    ('A', 1), ('A', 4), ('A', 1),
    ('C', 'reg1', U, (8, 8)),  # Consumes reg2 at (8, 7). WIN.
]


def click_chain(g, src, direction):
    vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    sx = src[0] * 6 + 3 + vp[0]
    sy = src[1] * 6 + 3 + vp[1]
    g.click(sx, sy)
    vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    tx = (src[0] + 2 * direction[0]) * 6 + 3 + vp[0]
    ty = (src[1] + 2 * direction[1]) * 6 + 3 + vp[1]
    g.click(tx, ty)


def apply_solution(g):
    for op in SOLUTION:
        if op[0] == 'A':
            g.action(op[1])
        else:
            _, pid, d, src = op
            click_chain(g, src, d)
