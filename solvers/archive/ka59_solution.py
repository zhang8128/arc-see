"""KA59 full solution — submit via arc_agi API.

Known solutions:
  L1: 11 actions (BFS)
  L2: 50 actions (push chain)
  L3: 33 actions (BFS)
  L4: 49 actions (setup+BFS)
  L5: 20 actions (wrap+momentum)
  L6: 45 actions (BFS)
  L7: TBD (baseline 326)
"""
import sys
import copy
import importlib.util
import arc_agi
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('ka59', 'environment_files/ka59/9f096b4a/ka59.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

U, D, L, R = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
CLICK = GameAction.ACTION6
sys.stdout.reconfigure(line_buffering=True)


def click_piece(g, name):
    """Get click data for a piece by name."""
    for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
        if s.name == name:
            gx, gy = s.x + s.width // 2, s.y + s.height // 2
            sc, ox, oy = g.camera._calculate_scale_and_offset()
            return {'x': int(gx * sc + ox), 'y': int(gy * sc + oy)}
    return None


def solve_l1(g):
    """L1: 11 actions. R R R L D L L L C(43,31) U R."""
    for d in [R, R, R, L, D, L, L, L]:
        g.perform_action(ActionInput(id=d, data={}))
    # Click on the pushed piece (display coords from BFS)
    g.perform_action(ActionInput(id=CLICK, data={'x': 43, 'y': 31}))
    for d in [U, R]:
        g.perform_action(ActionInput(id=d, data={}))
    return 11


def solve_l2(g):
    """L2: ~50 actions. Push chain."""
    total = 0
    NAMES = {0: 'cisjjwiopp', 1: 'peoafdrnua', 2: 'pomlugyufe', 3: 'sfcitxooao'}

    def sel(idx):
        nonlocal total
        cd = click_piece(g, NAMES[idx])
        if cd:
            g.perform_action(ActionInput(id=CLICK, data=cd))
            total += 1

    def m(d, n=1):
        nonlocal total
        for _ in range(n):
            g.perform_action(ActionInput(id=d, data={}))
            total += 1

    # Phase 1: P0 left to divider
    m(L, 1)  # P0: 33→30

    # Phase 2: P1 pushes P0 LEFT
    sel(1)
    m(U, 1)  # P1: 45→42
    m(L, 4)  # P1 pushes P0 at 4th L

    # Phase 3: P0 UP to boundary
    sel(0)
    m(U, 4)  # P0: 42→30

    # Phase 4: P1 LEFT to divider
    sel(1)
    m(L, 1)  # P1: 33→30

    # Phase 5: P3 pushes P1 LEFT
    sel(3)
    m(D, 3)  # P3: 33→42
    m(L, 2)  # P3 pushes P1

    # Phase 6: P1 UP to push pos, then push P0 UP
    sel(1)
    m(U, 2)  # P1: 42→36
    m(U, 1)  # P1 pushes P0 UP

    # Phase 7: Route P0 to (9,9)
    sel(0)
    p0 = g.ascpmvdpwj
    m(L, (p0.x - 9) // 3)
    m(U, (p0.y - 9) // 3)

    # Phase 8: Route P1 to (6,42)
    sel(1)
    p1 = g.ascpmvdpwj
    m(L, (p1.x - 6) // 3)
    m(D, (42 - p1.y) // 3)

    # Phase 9: Route P2 to (51,51)
    sel(2)
    p2 = g.ascpmvdpwj
    m(R, (51 - p2.x) // 3)
    m(U, (p2.y - 51) // 3)

    # Phase 10: Route P3 to (54,39)
    sel(3)
    p3 = g.ascpmvdpwj
    m(R, (54 - p3.x) // 3)
    m(U, (p3.y - 39) // 3)

    return total


def solve_l3(g):
    """L3: 33 actions (BFS solution)."""
    path = "DRRRRDLDDLLLLLLDDLLLLLLLDRUURRRRR"
    for ch in path:
        d = {'U': U, 'D': D, 'L': L, 'R': R}[ch]
        g.perform_action(ActionInput(id=d, data={}))
    return len(path)


def solve_l5(g):
    """L5: 20 actions. U*12 R*7 D*1."""
    total = 0
    for _ in range(12):
        g.perform_action(ActionInput(id=U, data={}))
        total += 1
    for _ in range(7):
        g.perform_action(ActionInput(id=R, data={}))
        total += 1
    g.perform_action(ActionInput(id=D, data={}))
    total += 1
    return total


def solve_l4(g):
    """L4: 49 actions. Setup(19) + BFS path(30).

    Replay the exact verified sequence from the standalone test.
    Both pieces are named 'pomlugyufe', so click by position not name.
    """
    total = 0
    sc, ox, oy = g.camera._calculate_scale_and_offset()

    def click_at_game_pos(gx, gy):
        """Click at game coordinates."""
        nonlocal total
        dx = int(gx * sc + ox)
        dy = int(gy * sc + oy)
        g.perform_action(ActionInput(id=CLICK, data={'x': dx, 'y': dy}))
        total += 1

    def m(d, n=1):
        nonlocal total
        for _ in range(n):
            g.perform_action(ActionInput(id=d, data={}))
            total += 1

    # P0 starts at (15,24) [SELECTED], P1 at (24,27), E at (15,45)
    # Setup: DD C1 LLL D C0 LLLLL RRRRRR
    m(D, 2)  # P0: (15,24)→(15,30)

    # Click P1 at (24,27) — use center of P1 (3x3 piece at 24,27)
    click_at_game_pos(24 + 1, 27 + 1)  # Click P1 center

    m(L, 3)  # P1: (24,27)→(15,27)
    m(D, 1)  # P1 pushes P0 DOWN across divider

    # Click P0 — now at (15,45) in bottom section
    click_at_game_pos(15 + 1, 45 + 1)  # Click P0 center

    m(L, 5)  # P0: (15,45)→(0,45)
    m(R, 6)  # P0 pushes enemy RIGHT at R[6]

    # BFS path: DD RRRRR UU R C(21,33) D RRRRR UUUUU R U DD RRRR
    m(D, 2)
    m(R, 5)
    m(U, 2)
    m(R, 1)

    # Click — from BFS: C(21,33). This is display coordinates.
    g.perform_action(ActionInput(id=CLICK, data={'x': 21, 'y': 33}))
    total += 1

    m(D, 1)
    m(R, 5)
    m(U, 5)
    m(R, 1)
    m(U, 1)
    m(D, 2)
    m(R, 4)

    return total


def solve_l6(g):
    """L6: 45 actions (BFS solution)."""
    path = "ULLUULLLLLLLUUULLLLLLLUDDRRRRRDDDRURRRRRRRUUR"
    for ch in path:
        d = {'U': U, 'D': D, 'L': L, 'R': R}[ch]
        g.perform_action(ActionInput(id=d, data={}))
    return len(path)


def solve_l7(g):
    """L7: 116 actions. Enemy push + return path + routing."""
    total = 0

    def do(a):
        nonlocal total
        g.perform_action(a)
        total += 1

    def fsel(idx):
        s = sorted(g.current_level.get_sprites_by_tag('xlfuqjygey'),
                    key=lambda s2: s2.name)[idx]
        sc2, ox2, oy2 = g.camera._calculate_scale_and_offset()
        do(ActionInput(id=CLICK, data={
            'x': int((s.x + s.width // 2) * sc2 + ox2),
            'y': int((s.y + s.height // 2) * sc2 + oy2)}))

    def m(d, n=1):
        for _ in range(n):
            do(ActionInput(id=d, data={}))

    # Phase 1-4: Enemy push (78 acts)
    m(L, 4); m(U, 4); fsel(1)
    m(U, 3); m(R, 3); m(U, 6)
    m(L, 11); m(U, 4); m(L, 10); m(U, 5); m(R, 10); m(D, 1)
    for ch in 'DDDLLLLLDDDRRRRD':
        do(ActionInput(id={'U': U, 'D': D, 'L': L, 'R': R}[ch], data={}))

    # Phase 5: Return path (20 acts)
    m(D, 2); m(R, 8); m(U, 3); m(R, 5)
    fsel(0); m(D, 1); m(L, 1); fsel(1); m(D, 1)

    # Phase 6: P0 to (27,45)
    fsel(0); m(D, 1); m(L, 5); m(D, 1)

    # Phase 7: P1 to (24,24)
    fsel(1); m(L, 5); m(D, 1)

    return total


def verify_local():
    """Verify all known solutions locally."""
    baselines = [39, 175, 86, 47, 21, 132, 326]
    solvers = {
        0: ('L1', solve_l1),
        1: ('L2', solve_l2),
        2: ('L3', solve_l3),
        3: ('L4', solve_l4),
        4: ('L5', solve_l5),
        5: ('L6', solve_l6),
        6: ('L7', solve_l7),
    }

    for level_idx in sorted(solvers.keys()):
        name, solver = solvers[level_idx]
        g = mod.Ka59()
        g.set_level(level_idx)
        n = solver(g)
        # L7 is the last level — check _state instead of _current_level_index
        if level_idx == 6:
            won = str(g._state) == "GameState.WIN"
        else:
            won = g._current_level_index > level_idx
        status = "✓ WIN" if won else "✗ FAIL"
        print(f"  {name}: {n} actions (baseline {baselines[level_idx]}) {status}")


if __name__ == '__main__':
    if '--verify' in sys.argv:
        print("Verifying known solutions locally...")
        verify_local()
    else:
        print("Run with --verify to test locally")
