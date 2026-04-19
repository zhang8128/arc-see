"""LF52 L4 solution — 34 moves vs baseline 86.

Key insight: multi-vehicle coordination.
- 3 sub-vehicles (hupkpseyuim2) at world (48,18), (48,66), (72,42).
- All move together via A3/A4 but hit different walls at different times.
- Middle vehicle rail: at (48, 42), A2 activates for vertical rail movement.
- Load main-vehicle → world expand → load middle-vehicle → transfer to sub-vehicle.
- Then use sub-vehicle + f-pivots to chain-merge sub-panel isolated pieces.

The unlock:
1. OPENER chains consume main-panel pieces, load main vehicle, world-expand.
2. FIFTEEN chains set up middle vehicle at (72, 42) loaded.
3. A3 × 4 drives loaded middle to rail marker (48, 42).
4. A2 × 2 descends rail to (48, 54).
5. A4 × 3 aligns sub-vehicle at (48, 66) directly below middle.
6. Chain middle → sub via f@(48, 60) pivot.
7. Drive sub to (36, 66) — where f@(36, 60) and f@(36, 72) both flank it.
8. Up-chain (36, 66) → (36, 54). Left-chain absorbs (30, 54).
9. Scroll viewport, re-select piece at (24, 54).
10. Down-chain to (24, 66), down-chain to (24, 78), right-chain absorbs (30, 78).
11. Win — 1 piece remains.

Total L4 moves: 34.
"""
from lf52_tool import LF52


# Each tuple: ('A', n) for A-action, ('C', (x, y)) for click
L4_SOLVE = [
    # FIFTEEN (15 moves expressed as 25 atomic clicks + A-actions)
    ('C', (13, 25)), ('C', (25, 25)),  # B[1] -> B[3]
    ('C', (25, 25)), ('C', (37, 25)),  # B[3] -> B[5]
    ('A', 3),                           # align for load
    ('C', (37, 25)), ('C', (49, 25)),  # B[5] + B[6] -> vehicle load
    ('A', 4), ('A', 4), ('A', 4), ('A', 4),  # drive loaded, world expands
    ('C', (19, 25)), ('C', (31, 25)),  # chain consume (72, 18)
    ('C', (31, 25)), ('C', (31, 37)),  # chain down via col 78
    ('C', (31, 37)), ('C', (31, 49)),
    ('C', (49, 25)), ('C', (49, 37)),  # chain down via col 96
    ('C', (49, 37)), ('C', (49, 49)),
    ('C', (49, 49)), ('C', (37, 49)),  # merge left
    ('C', (37, 49)), ('C', (25, 49)),  # final merge, loads middle vehicle at (72, 42)

    # Rail navigation: middle (72, 42) -> (48, 42) -> (48, 48) -> (48, 54)
    ('A', 3), ('A', 3), ('A', 3), ('A', 3),  # drive middle to rail (48, 42)
    ('A', 2), ('A', 2),                       # descend rail to (48, 54)
    ('A', 4), ('A', 4), ('A', 4),             # align sub at (48, 66)

    # Transfer middle -> sub via f@(48, 60) pivot
    ('C', (40, 20)), ('C', (40, 31)),

    # Drive loaded sub left to (36, 66) — flanked by f@(36, 60) and f@(36, 72)
    ('A', 3), ('A', 3),

    # Up chain: (36, 66) -> (36, 54) via f@(36, 60)
    ('C', (28, 29)), ('C', (27, 19)),
    # Left chain: (36, 54) -> (24, 54) absorbing (30, 54) pivot
    ('C', (28, 17)), ('C', (15, 19)),

    # Scroll viewport to bring piece back in view
    ('A', 3), ('A', 3),

    # Down chain: (24, 54) -> (24, 66) loads sub again via f@(24, 60)
    ('C', (16, 17)), ('C', (15, 31)),
    # Down chain: (24, 66) -> (24, 78) via f@(24, 72)
    ('C', (16, 29)), ('C', (15, 43)),
    # Right chain: (24, 78) -> (36, 78) absorbing (30, 78) — WIN
    ('C', (16, 41)), ('C', (27, 43)),
]


def run():
    g = LF52(up_to_level=4, verbose=False)
    for i, step in enumerate(L4_SOLVE):
        if step[0] == 'C':
            g.click(*step[1])
        else:
            g.action(step[1])
    level = g.obs.levels_completed if g.obs else g.env._game._current_level_index
    print(f'L4 solve complete. Level now: {level}')
    return g


if __name__ == '__main__':
    run()
