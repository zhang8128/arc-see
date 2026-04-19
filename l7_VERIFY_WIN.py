"""Execute the full win sequence on the REAL engine and verify L7 completion."""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from lf52_tool import LF52
from arcengine import GameAction

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_NUM = {U: 1, D: 2, L: 3, R: 4}


# Bridge plan ops (from chain-9 state onward)
# chain-9 state = reg1 (9, 8), red (10, 8) V-M, reg2 (22, 6)
BRIDGE = [
    ('C', 'reg1', R, (9, 8)),   # chain 9: reg1 (9, 8) → (11, 8)
    ('A', 1), ('A', 3), ('A', 3), ('A', 1), ('A', 1), ('A', 4), ('A', 1), ('A', 1), ('A', 4), ('A', 4), ('A', 4),  # V-M+red drive to (12, 3)
    ('C', 'red', R, (12, 3)),   # red (12, 3) → (14, 3)
    ('A', 3), ('A', 3), ('A', 3), ('A', 2), ('A', 2), ('A', 4), ('A', 4), ('A', 2),  # V-M empty drive to (11, 6)
    ('C', 'reg1', U, (11, 8)),  # reg1 (11, 8) → (11, 6) loads on V-M
    ('A', 1), ('A', 3), ('A', 3), ('A', 1), ('A', 1), ('A', 4), ('A', 4), ('A', 1), ('A', 1), ('A', 4), ('A', 4), ('A', 4), ('A', 2),  # V-M drive to (14, 2)
    ('C', 'reg1', D, (14, 2)),  # reg1 (14, 2) → (14, 4) via red(14, 3) pivot
    ('C', 'red', D, (14, 3)),   # red (14, 3) → (14, 5) via reg1(14, 4) pivot
    ('C', 'reg1', D, (14, 4)),  # reg1 (14, 4) → (14, 6) via red(14, 5) pivot
    ('C', 'reg1', R, (14, 6)),  # reg1 → (16, 6) via DGX(15, 6)
    ('C', 'reg1', R, (16, 6)),  # reg1 → (18, 6) via DGX(17, 6)
    ('C', 'red', R, (14, 5)),   # red → (16, 5) via DGX(15, 5)
    ('C', 'red', R, (16, 5)),   # red → (18, 5) via DGX(17, 5)
]


# Stage 1-3 A-actions and chains (from sim solver output, with piece positions at time of chain)
# S1: A2, A4, A2, A2, A3, A3, A3, A2, A2, C reg1 U
# S2: A1, A1, A4, A2, A4, A4, A4, A2, C reg1 D
# S3: A1, A3, A1, A3, A3, A2, A4, A2, A2, C reg2 U
POST = [
    # Stage 1
    ('A', 2), ('A', 4), ('A', 2), ('A', 2), ('A', 3), ('A', 3), ('A', 3), ('A', 2), ('A', 2),
    ('C', 'reg1', U, (18, 6)),
    # Stage 2
    ('A', 1), ('A', 1), ('A', 4), ('A', 2), ('A', 4), ('A', 4), ('A', 4), ('A', 2),
    ('C', 'reg1', D, (22, 3)),  # reg1 (22, 3) → (22, 5) via DGX(22, 4) pivot
    # Stage 3
    ('A', 1), ('A', 3), ('A', 1), ('A', 3), ('A', 3), ('A', 2), ('A', 4), ('A', 2), ('A', 2),
    ('C', 'reg2', U, (22, 6)),  # WIN
]


def click_chain(g, src, d):
    """Execute chain: click src piece, click target indicator. Engine uses pixel coords."""
    vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    sx = src[0] * 6 + 3 + vp[0]
    sy = src[1] * 6 + 3 + vp[1]
    g.click(sx, sy)
    # After click, vp may have changed (if chain triggered scroll)
    vp = tuple(g.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)
    tx = (src[0] + 2*d[0]) * 6 + 3 + vp[0]
    ty = (src[1] + 2*d[1]) * 6 + 3 + vp[1]
    g.click(tx, ty)


def run():
    g = LF52(up_to_level=7, verbose=False)
    # Apply verified chain 1-8 via harness — actually LF52 up_to_level=7 replays L1-L6,
    # lands at L7 init. I need to get to chain-8 state. Use l7_harness.
    from l7_harness import L7Harness
    h = L7Harness(verbose=False)
    h.restore_to('chain8')
    g = h._base  # underlying LF52

    print('At chain-8 state:')
    ik = g.env._game.ikhhdzfmarl
    print(f'  foz: {[(s.name, tuple(s.chahdtpdoz)) for s in ik.hncnfaqaddg.xpnsbxlatu if "fozwvlovdui" in s.name]}')
    print(f'  vp: {tuple(ik.hncnfaqaddg.cdpcbbnfdp)}')

    # Now apply bridge + post-bridge
    for i, op in enumerate(BRIDGE + POST):
        kind = op[0]
        if kind == 'A':
            g.action(op[1])
        elif kind == 'C':
            pid, d, src = op[1], op[2], op[3]
            click_chain(g, src, d)
        # Check state
        ik = g.env._game.ikhhdzfmarl
        foz_count = len(ik.hncnfaqaddg.ndtvadsrqf('fozwvlovdui'))
        if i % 10 == 0 or foz_count < 3:
            print(f'  step {i}: op={op}, foz_count={foz_count}, state={g.state_name()}, levels={g.level()}')
        if foz_count < 3:
            print(f'=== FOZ COUNT DROPPED! ===')
            print(f'  iajuzrgttrv (win): {ik.iajuzrgttrv}')
            print(f'  levels_completed: {g.level()}')
            print(f'  state: {g.state_name()}')
    # Final state
    ik = g.env._game.ikhhdzfmarl
    print()
    print(f'FINAL:')
    print(f'  levels_completed: {g.level()}')
    print(f'  state: {g.state_name()}')
    print(f'  foz pieces: {[(s.name, tuple(s.chahdtpdoz)) for s in ik.hncnfaqaddg.xpnsbxlatu if "fozwvlovdui" in s.name]}')
    print(f'  iajuzrgttrv: {ik.iajuzrgttrv}')


if __name__ == '__main__':
    run()
