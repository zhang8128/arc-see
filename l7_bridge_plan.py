"""Test a specific bridge plan: use red at (14,3) as pivot to move reg1
through col 14 into col 16 via DGX(15,5) or DGX(15,6).

Plan:
  1. Get reg1 loaded on vehicle at (14, 2).
  2. Get red to (14, 3).
  3. Chain reg1 (14,2) DOWN via red(14,3) pivot to (14, 4).
  4. Chain red (14,3) DOWN via reg1(14,4) pivot to (14, 5).
  5. Chain reg1 (14,4) DOWN via red(14,5) pivot to (14, 6).
  6. Chain reg1 (14,6) R via DGX(15,6) to (16, 6).

Validate each step is feasible in isolation (synthetic state) before searching
for the achievable path.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
from dataclasses import replace
from l7_sim import load_init, Sim

U, D, L, R = (0, -1), (0, 1), (-1, 0), (1, 0)
DN = {U:'U',D:'D',L:'L',R:'R'}


def dump(s, label):
    print(f'{label}: pieces={s.pieces}')


def test_step(s, pid, d, expected_new_pos):
    opts = s.chain_options(pid)
    ok = d in opts
    print(f'  chain {pid} {DN[d]}: valid={ok}, options={[DN[x] for x in opts]}')
    if ok:
        s2 = s.do_chain(pid, d)
        got = s2.pieces[pid] if pid in s2.pieces else None
        print(f'    {pid} moved to {got} (expected {expected_new_pos})')
        return s2
    return s


if __name__ == '__main__':
    s0 = load_init()
    # Seed a hypothetical state: reg1 at (14, 2) (with vehicle), red at (14, 3), reg2 at (22, 6).
    # Keep initial vehicles + add a vehicle at (14, 2) ... actually V14 already there.
    pieces = tuple(sorted([('reg1', (14, 2)), ('reg2', (22, 6)), ('red', (14, 3))]))
    s = replace(s0, piece_pos=pieces)
    dump(s, 'Hypothetical seed')
    # Ensure V14 at (14, 2). Check vehicle_pos:
    print(f'  vehicles={s.vehicle_pos}')
    print(f'  (14,2) sprites: {s.cell_sprites((14,2))}')
    print(f'  (14,3) sprites: {s.cell_sprites((14,3))}')
    print(f'  (14,4) sprites: {s.cell_sprites((14,4))}')
    print()

    # Step 3: chain reg1 (14,2) DOWN via red pivot (14,3) to (14,4)
    print('Step 3: reg1 (14,2) DOWN')
    s = test_step(s, 'reg1', D, (14, 4))
    dump(s, '  after')
    print()

    # Step 4: chain red (14,3) DOWN via reg1 pivot (14,4) to (14,5)
    print('Step 4: red (14,3) DOWN')
    s = test_step(s, 'red', D, (14, 5))
    dump(s, '  after')
    print()

    # Step 5: chain reg1 (14,4) DOWN via red (14,5) to (14, 6)
    print('Step 5: reg1 (14,4) DOWN')
    s = test_step(s, 'reg1', D, (14, 6))
    dump(s, '  after')
    print()

    # Step 6: chain reg1 (14,6) RIGHT via DGX(15,6) to (16, 6)
    print('Step 6: reg1 (14,6) RIGHT')
    s = test_step(s, 'reg1', R, (16, 6))
    dump(s, '  after')
    print()

    # Step 7: chain reg1 (16,6) RIGHT via DGX(17,6) to (18, 6)
    print('Step 7: reg1 (16,6) RIGHT')
    s = test_step(s, 'reg1', R, (18, 6))
    dump(s, '  after')
    print()

    # Step 8: reg1 (18, 6) RIGHT — pivot (19,6) empty — should fail
    print('Step 8: reg1 (18,6) RIGHT — probably fails without pivot')
    s = test_step(s, 'reg1', R, None)
    dump(s, '  after')
    print()

    # Try DOWN: (18, 6) → (18, 8). Pivot (18, 7) empty.
    print('Step 8 alt: reg1 (18,6) DOWN')
    s = test_step(s, 'reg1', D, None)
    print()

    # Hmm — need to get reg1 to (22, 5) eventually. From (18, 6):
    # - R via (19,6) pivot: empty, no foz/dgx. Invalid unless red dragged.
    # - UP via (18, 5)? Target (18, 4) track-up valid if vehicle there. Source (18, 6) — (18,5) plain hup.
    #   Actually wait, chain from (18, 6) UP: target (18, 4), pivot (18, 5). (18,5) = hup only.
    # We'd need red at (18, 5) as pivot. Or DGX. DGX at (18, 5) requires vehicle — no track at (18,5). Permanent no.
    # So red at (18, 5) is the bridge. Red currently at (14, 5). Can red chain further east?
    print('Can red at (14,5) chain R?')
    s_check = replace(s0, piece_pos=tuple(sorted([('reg1', (16, 6)), ('reg2', (22, 6)), ('red', (14, 5))])))
    opts = [DN[x] for x in s_check.chain_options('red')]
    print(f'  red options: {opts}')
    # R: pivot (15, 5) DGX → valid. Target (16, 5) hup → valid. YES red can reach (16, 5).
    # Then red at (16, 5) R: pivot (17, 5) DGX → valid. Target (18, 5) hup → valid.
    # Then red at (18, 5) R: pivot (19, 5) empty → invalid. Need foz/dgx there.
    # DGX can be at (19, 5)? (19, 5) no track (row 5 pos 19 = ' '). No vehicle. No DGX drag.
    # Hmm (19, 5) permanent empty → no pivot.
    # R from (18, 5) DEAD END.
    #
    # But wait — red at (18,5) DOWN: target (18,7) empty → invalid.
    # red at (18,5) UP: pivot (18,4) track-up (vehicle possible, no static foz/dgx). Need DGX or foz there.
    # (18, 4) is track — vehicle can be there. DGX mobile → can drag DGX to (18, 4). Then chain valid.
    # Target (18,3): track-up + vehicle + initial DGX. len=3 → invalid. Unless DGX dragged away.
    print()
    print('So chain from red at (18, 5) is limited. The bridge ends here.')
