"""RE86 solution — verified L1-L4.

RE86 (re86-4e57566e): Sprite-positioning puzzle.
- 3 sprite shapes: cross (+), diamond (◇/X), frame (□)
- ACTION1-4 = UDLR by 3px, ACTION5 = cycle active sprite
- Sprites pick up colors from swatches when arms overlap
- Frame/diamond sprites with `nogegkgqgd` tag morph dimensions on collision with `miqpqafylc` triggers
- Win: overlay sprites on canvas, match background pixels (excluding -1, 4)

Baselines: [28, 38, 198, 57, 84, 117, 328, 221]
Verified L1-L4: 145 actions vs 321 baseline (55% improvement).
"""
import importlib.util, sys
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('re86', 'environment_files/re86/4e57566e/re86.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


# Verified solutions (L1-L4)
SOLUTIONS = {
    # L1: 20 actions (baseline 28)
    # 9-cross to (24,48): 7 UP + 4 RIGHT
    # SWITCH to b-cross
    # b-cross to (9,15): 6 UP + 2 LEFT
    1: ['ACTION1']*7 + ['ACTION4']*4 + ['ACTION5'] + ['ACTION1']*6 + ['ACTION3']*2,

    # L2: 36 actions (baseline 38)
    # X-shape (12, ACTIVE) to (48,18): 10 DOWN + 3 LEFT
    # SWITCH to diamond (13)
    # Diamond to (12,21): 6 UP + 6 LEFT
    # SWITCH to cross (9)
    # Cross to (48,27): 2 DOWN + 7 LEFT
    2: ['ACTION2']*10 + ['ACTION3']*3 + ['ACTION5'] + ['ACTION1']*6 + ['ACTION3']*6 + ['ACTION5'] + ['ACTION2']*2 + ['ACTION3']*7,

    # L3: 47 actions (baseline 198)
    # Line (8) to (6,27): 13 UP + 1 LEFT (covers targets 0,1)
    # SWITCH to diamond (8)
    # Diamond to (30,18): 6 UP + 9 LEFT (covers targets 3,4,7)
    # SWITCH to X-shape (8)
    # X-shape to (24,42): 8 UP + 8 RIGHT (covers targets 2,5,6)
    3: ['ACTION1']*13 + ['ACTION3'] + ['ACTION5'] + ['ACTION1']*6 + ['ACTION3']*9 + ['ACTION5'] + ['ACTION1']*8 + ['ACTION4']*8,

    # L4: 42 actions (baseline 57)
    # Cross 0 (6→12) to (30,15): 8 LEFT + 5 UP (pick up color 12) + 3 DOWN + 5 LEFT
    # SWITCH to X-shape
    # X-shape (10→14) to (30,39): 8 DOWN + 6 RIGHT (pick up color 14) + 5 UP + 1 LEFT
    4: ['ACTION3']*8 + ['ACTION1']*5 + ['ACTION2']*3 + ['ACTION3']*5 + ['ACTION5'] + ['ACTION2']*8 + ['ACTION4']*6 + ['ACTION1']*5 + ['ACTION3'],

    # L6: 47 actions (baseline 117)
    # Cross 0 (frame, active) → (45,30,10,28) covers all 4 c11 targets via morphing
    #   20 moves: 2U + 2R + 1D + 2R + 2D + 6R + 1U + 1R + 1U + 2R
    # Cross 1 (cross +) → covers all 4 c9 targets via arm shifts through trigger
    #   26 moves: 5D + 2L + 1U + 1L + 2D + 1L + 6U + 8L
    # Insight: morph trigger shifts cross 1's arm position within sprite (not just frame morphing)
    6: ['ACTION1', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION1', 'ACTION4', 'ACTION1', 'ACTION4', 'ACTION4',
        'ACTION5',
        'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION1', 'ACTION3', 'ACTION2', 'ACTION2', 'ACTION3', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3'],

    # L5: 77 actions (baseline 84)
    # Sprite assignment:
    # - X-shape (active, ldkpywfara) → color 9 → (15,30): covers (6,21), (6,39) on diagonals
    # - Cross 2 (large +) → color 9 → (51,33): covers (45,33), (51,24), (51,45), (60,33)
    # - Diamond (nogegkgqgd) → color 8 → (36,51): covers (27,51), (33,57), (36,42), (42,54) on outline
    # X-shape: 5D + 5L (color 9) + 7R + 14U → (15, 30) [31 moves]
    # SWITCH to cross 2
    # Cross 2: 7D + 11L (color 9) + 1U + 4R → (51, 33) [23 moves]
    # SWITCH to diamond
    # Diamond: 10D + 7R (color 8) + 4U → (36, 51) [21 moves]
    5: ['ACTION2']*5 + ['ACTION3']*5 + ['ACTION4']*7 + ['ACTION1']*14 +
       ['ACTION5'] +
       ['ACTION2']*7 + ['ACTION3']*11 + ['ACTION1'] + ['ACTION4']*4 +
       ['ACTION5'] +
       ['ACTION2']*10 + ['ACTION4']*7 + ['ACTION1']*4,

    # L7: 98 actions (baseline 328) — 70% reduction
    # Three sprites, three color groups:
    # - A (19x19 cross, active) → color 11 → 3 c11 targets via arm shifts (32 moves)
    # - B (13x13 frame) → color 9 → 2 c9 targets via 19×7 morph (28 moves)
    # - C (37x19 wide +) → color 8 → 4 c8 targets via arm shifts (36 moves)
    # Key insight: C's 37-wide horizontal arm is the ONLY sprite that spans cols 3..36,
    # required to cover (3,15) and (36,15). Arm shifts via morph trigger add flexibility.
    7: (['ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION3', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2'] +
        ['ACTION5'] +
        ['ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4'] +
        ['ACTION5'] +
        ['ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION2', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION1', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION2']),

    # L8: 155 actions (baseline 221) — 30% reduction
    # Two nogegkgqgd frames, each morphs to cover 4 targets:
    # - Frame A (active, color 12→6) → 16×10 at (6,45) covers 4 c6 corners
    # - Frame B (color 10→11) → 7×19 at (9,39) covers 4 c11 corners
    # Challenge: navigating past y=28 swatch row without color contamination;
    # requires careful path through narrow gaps and re-morphing via triggers.
    8: (['ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3'] +
        ['ACTION5'] +
        ['ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION2', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3']),
}


def verify():
    """Verify all known solutions locally."""
    g = mod.Re86()
    g.set_level(0)
    total = 0
    for level in range(1, max(SOLUTIONS) + 1):
        if level not in SOLUTIONS:
            print(f'L{level}: not yet solved')
            break
        actions = SOLUTIONS[level]
        for a in actions:
            g.perform_action(ActionInput(id=getattr(GameAction, a)))
        state = g._state.name
        lvl_idx = g._current_level_index
        success = lvl_idx > level - 1 or state == "WIN"
        marker = "✓" if success else "✗"
        print(f'  {marker} L{level}: {len(actions)} actions, state={state}, level_idx={lvl_idx}')
        total += len(actions)
        if not success:
            print(f'    FAILED to advance')
            return False

    print(f'\nTotal: {total} actions')
    return True


def verify_api():
    """Verify with arc_agi API."""
    import arc_agi
    arcade = arc_agi.Arcade()
    env = arcade.make("re86-4e57566e", render_mode=None)
    env.reset()
    total = 0
    for level in sorted(SOLUTIONS):
        for a in SOLUTIONS[level]:
            result = env.step(getattr(GameAction, a))
            total += 1
        print(f'  L{level}: {len(SOLUTIONS[level])} actions, levels_completed={result.levels_completed}')
    print(f'\nTotal: {total}, State: {result.state}')


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'api':
        verify_api()
    else:
        verify()
