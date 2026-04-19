"""Plan v3:
1. Verified chain 1-8 → at_chain9 state.
2. Chain reg1 R (9,8) → (11, 8). reg1 at (11, 8). [chain 9]
3. Drive V-M with red from (10, 8) to (12, 3).
4. Chain red R (12, 3) → (14, 3) via DGX(13, 3). red at (14, 3). V-M (12, 3) empty.
5. Drive V-M empty from (12, 3) to (11, 6).
6. Chain reg1 U (11, 8) → (11, 6) via DGX(11, 7). reg1 loaded on V-M.
7. Drive V-M with reg1 to (14, 2).
8. Chain reg1 D (14, 2) → (14, 4) via red(14, 3) pivot. reg1 (14, 4).
9. Chain red D (14, 3) → (14, 5) via reg1(14, 4) pivot. red (14, 5).
10. Chain reg1 D (14, 4) → (14, 6) via red(14, 5) pivot. reg1 (14, 6).
11. Chain reg1 R (14, 6) → (16, 6) via DGX(15, 6). reg1 (16, 6). [possibly scroll 2 if x=16 target]
12. Continue east to reach (22, 5) area.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from l7_sim import load_init
from l7_search_deep import at_chain9

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
A_DIR = {1: U, 2: D, 3: L, 4: R}
DN = {U:'U',D:'D',L:'L',R:'R'}


def show(s, lbl):
    print(f'[{lbl}] pieces={s.pieces}')


def apply_chain(s, pid, d, lbl):
    if pid not in s.pieces:
        print(f'  FAIL {lbl}: {pid} missing')
        return s, False
    opts = s.chain_options(pid)
    if d not in opts:
        print(f'  FAIL {lbl}: chain {pid} {DN[d]}. opts={[DN[x] for x in opts]}, at {s.pieces[pid]}')
        return s, False
    s2 = s.do_chain(pid, d)
    print(f'  OK {lbl}: {pid} {DN[d]} {s.pieces[pid]} → {s2.pieces[pid] if pid in s2.pieces else "consumed"}')
    return s2, True


def apply_a(s, actions):
    for a in actions:
        s = s.do_action(A_DIR[a])
    return s


def where_veh_m(s):
    # V-M is in M-component. Find it.
    m_cells = {(8,5),(8,6),(8,7),(9,3),(9,4),(9,5),(9,7),(10,3),(10,5),(10,7),(10,8),(11,1),(11,2),(11,3),(11,5),(11,6),(12,1),(12,3),(13,1),(14,1),(14,2)}
    for v in s.vehicle_pos:
        if v in m_cells:
            return v
    return None


if __name__ == '__main__':
    s = at_chain9()
    show(s, 'at_chain9')
    print(f'  V-M at: {where_veh_m(s)}')

    # Step 2: chain 9
    s, ok = apply_chain(s, 'reg1', R, 'chain9')
    if not ok: sys.exit()
    show(s, 'after chain 9')

    # Step 3: drive V-M with red to (12, 3). V-M should be at (10, 8) carrying red.
    # Path: (10,8) → (10,7) → (9,7) → (8,7) → (8,6) → (8,5) → (9,5) → (9,4) → (9,3) → (10,3) → (11,3) → (12,3)
    drive = [1, 3, 3, 1, 1, 4, 1, 1, 4, 4, 4]
    s = apply_a(s, drive)
    print(f'  After drive: V-M at {where_veh_m(s)}, red at {s.pieces.get("red")}')

    # Step 4: chain red R (12, 3) → (14, 3) via DGX(13, 3)
    s, ok = apply_chain(s, 'red', R, 'red to (14,3)')
    if not ok: sys.exit()
    show(s, 'after red to 14,3')

    # Step 5: drive V-M empty from (12, 3) to (11, 6)
    # Path: (12, 3) → (11, 3) → (10, 3) → (9, 3) → (9, 4) → (9, 5) → (10, 5) → (11, 5) → (11, 6)
    drive2 = [3, 3, 3, 2, 2, 4, 4, 2]
    s = apply_a(s, drive2)
    print(f'  After drive: V-M at {where_veh_m(s)}')

    # Step 6: chain reg1 U (11, 8) → (11, 6) via DGX(11, 7)
    s, ok = apply_chain(s, 'reg1', U, 'reg1 to (11,6)')
    if not ok: sys.exit()
    show(s, 'after reg1 to 11,6')

    # Step 7: drive V-M with reg1 to (14, 2)
    # Path: (11, 6) → (11, 5) → (10, 5) → (9, 5) → (9, 4) → (9, 3) → (10, 3) → (11, 3) → (11, 2) → (11, 1) → (12, 1) → (13, 1) → (14, 1) → (14, 2)
    drive3 = [1, 3, 3, 1, 1, 4, 4, 1, 1, 4, 4, 4, 2]
    s = apply_a(s, drive3)
    print(f'  After drive: V-M at {where_veh_m(s)}, reg1 at {s.pieces.get("reg1")}')

    # Step 8: chain reg1 D (14, 2) → (14, 4) via red(14, 3) pivot
    s, ok = apply_chain(s, 'reg1', D, 'reg1 to (14,4)')
    if not ok: sys.exit()
    show(s, 'after reg1 to 14,4')

    # Step 9: chain red D (14, 3) → (14, 5) via reg1(14, 4) pivot
    s, ok = apply_chain(s, 'red', D, 'red to (14,5)')
    if not ok: sys.exit()

    # Step 10: chain reg1 D (14, 4) → (14, 6) via red(14, 5) pivot
    s, ok = apply_chain(s, 'reg1', D, 'reg1 to (14,6)')
    if not ok: sys.exit()

    # Step 11: chain reg1 R (14, 6) → (16, 6) via DGX(15, 6)
    s, ok = apply_chain(s, 'reg1', R, 'reg1 to (16,6)')
    if not ok: sys.exit()
    show(s, 'after reg1 to 16,6')

    # Step 12: chain reg1 R (16, 6) → (18, 6) via DGX(17, 6)
    s, ok = apply_chain(s, 'reg1', R, 'reg1 to (18,6)')
    if not ok: sys.exit()

    # Step 13: chain red R (14, 5) → (16, 5) via DGX(15, 5)
    s, ok = apply_chain(s, 'red', R, 'red to (16,5)')
    if not ok: sys.exit()

    # Step 14: chain red R (16, 5) → (18, 5) via DGX(17, 5)
    s, ok = apply_chain(s, 'red', R, 'red to (18,5)')
    if not ok: sys.exit()
    show(s, 'after red to (18,5)')

    # Step 15: chain reg1 UP (18, 6) → (18, 4) via red(18, 5) pivot
    # Target (18, 4): track-up + (vehicle?). Need vehicle at (18, 4).
    # Initially R-component vehicles are scattered. After all my A-actions, where are they?
    print(f'  vehicles: {s.vehicle_pos}')
    print(f'  mobile DGX: {sorted(set(s.dgx_pos) & set(s.vehicle_pos))}')
    print(f'  reg1 options at {s.pieces["reg1"]}: {[DN[x] for x in s.chain_options("reg1")]}')

    # Need R-vehicle at (18, 4). Currently R-vehicles at (18, 0), (19, 0), (20, 0), (21, 1).
    # Drive one to (18, 4): path (18, 0) → (17, 0) → (17, 1) → (17, 2) → (18, 2) → (18, 3) → (18, 4)
    # A-sequence: A3, A2, A2, A4, A2, A2
    print('Driving R-vehicle to (18, 4)...')
    drive_r = [3, 2, 2, 4, 2, 2]
    s = apply_a(s, drive_r)
    print(f'  After drive: vehicles={s.vehicle_pos}')
    print(f'  DGX all: {sorted(s.dgx_pos)}')
    print(f'  cell (18, 4): {s.cell_sprites((18, 4))}')
    print(f'  cell (18, 5): {s.cell_sprites((18, 5))}')
    print(f'  cell (18, 6): {s.cell_sprites((18, 6))}')
    print(f'  reg1 options: {[DN[x] for x in s.chain_options("reg1")]}')

    # Now try reg1 UP
    s, ok = apply_chain(s, 'reg1', U, 'reg1 UP to (18, 4)')
    if not ok: sys.exit()
    show(s, 'after reg1 UP to (18, 4)')

    # Step 17: drive R-vehicle (with reg1 loaded) to (22, 3) then (22, 4) and further
    # From (18, 4), want to get reg1 to (22, 3) via row 2 path.
    # Path: (18, 4) → (18, 3) → (18, 2) → (19, 2) → (20, 2) → (21, 2) → (22, 2) → (22, 3)
    drive_east = [1, 1, 4, 4, 4, 4, 2]
    s = apply_a(s, drive_east)
    print(f'  After drive east: reg1 at {s.pieces.get("reg1")}, vehicles={s.vehicle_pos}')
    print(f'  mobile DGX: {sorted(set(s.dgx_pos) & set(s.vehicle_pos))}')
    print(f'  (22, 4) state: {s.cell_sprites((22, 4))}')
    print(f'  reg1 options: {[DN[x] for x in s.chain_options("reg1")] if "reg1" in s.pieces else "?"}')

    # Final chain: reg1 D (22, 3) → (22, 5) via DGX-at-(22, 4) pivot
    if s.pieces.get('reg1') == (22, 3):
        s, ok = apply_chain(s, 'reg1', D, 'reg1 D to (22, 5)')
        if ok:
            show(s, 'reg1 at (22, 5)!!!!')
            # Now chain reg2 UP via reg1 pivot to (22, 4) for consumption
            if (22, 4) in s.vehicle_pos and (22, 4) not in s.dgx_pos:
                s, ok = apply_chain(s, 'reg2', U, 'WIN? reg2 UP')
                if ok:
                    show(s, 'POST WIN')
    print(f'  final foz_count: {s.foz_count()}')
