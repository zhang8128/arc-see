"""G50T solution — L1 verified.

G50T (g50t-5849a774): Time-loop maze puzzle.
- 7 levels, keyboard-only (UDLR + ACTION5), step = 6 pixels.
- ACTION5 is NOT "reset" — it's **record-and-replay**:
  - Undoes all moves back to start (player teleports to spawn)
  - Saves the undone move list as a "ghost" (rloltuowth entity) that auto-replays
  - Spawns a new player clone at start
  - Every subsequent player move advances every ghost by `ghost.path[move_index]`
  - When a ghost's path runs out, it stays put forever
  - Max ghosts per level = `len(drofvwhbxb)` = 2 in L1. After using all slots, ghosts
    wipe and the counter resets.
- Ghosts fire triggers (hamay) just like the player — so a ghost can hold down a
  switch while the new player walks through the opened door.
- Win condition (safkknjslo): `player.x == goal.x + 1 AND player.y == goal.y + 1`.
- Collision is single-point (player center, `hziczfhrxn`/`prtgxvhmth`) against
  the maze sprite — NOT bounding-box.

Baselines: [51, 175, 86, 52, 96, 48, 67] — total 575.
L1 verified: 17 actions vs 51 baseline (67% improvement).
L2 verified: 31 actions vs 175 baseline (82% improvement).
L3 verified: 64 actions vs 86 baseline (26% improvement).
L4 verified: 31 actions vs 52 baseline (40% improvement).
L5 verified: 52 actions vs 96 baseline (46% improvement).
L6 verified: 49 actions vs 48 baseline (+1 action, level completed).
L7 verified: 43 actions vs 67 baseline (36% improvement).

NEW MECHANIC (L5): latched switches TOGGLE on each press. L3's "latch is
permanent" was wrong — actually each press flips the latch state. Path
parity matters: each latched switch must be touched an odd number of total
times (across all ghost replays and the live player) to end in the shifted
state. This drastically complicates ghost-path design.

NEW MECHANIC (L3): latched doors. Some doors (dpdubazedr=True) stay shifted
permanently after the first switch-press. The latch is recorded on the door
itself (dijhfchobv on the uwxkstolmf entity). ACTION5 resets the latch — so
latched state is tied to ghost replays, not persistent between ghost saves.

NEW MECHANIC (L4): teleporter pairs (ulhhdeoyok entities). Two matched
teleporters appear in the hamayflsib list alongside normal switches. Stepping
onto one teleports the entity to the other. BUT the teleport only activates
when BOTH switches on the level are held simultaneously. So L4 needs two
ghosts (one per switch) + live player stepping onto ulhh[2] → teleport to
ulhh[3] → walk to goal.
"""
import importlib.util, sys
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('g50t', 'environment_files/g50t/5849a774/g50t.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


# Verified solutions
SOLUTIONS = {
    # L1: 17 actions (baseline 51)
    # Goal at (42, 48) → win requires player at (43, 49).
    # Reachable area without mechanics = 12 tiles; bottom-right is cut off by
    # uwx at (13, 37). Stepping on hamay at (37, 7) shifts uwx to (19, 37), but
    # only while something stands on it.
    #
    # Solution: walk to the trigger first to record the path, use ACTION5 to save
    # that path as a ghost. The new player then walks south; the ghost replays
    # its 4 right-moves to reach (37, 7) on move 4. On move 5+ the ghost has no
    # more recorded moves and stays put holding the switch, so uwx stays shifted.
    # New player walks through the now-open door to (43, 49).
    1: ['ACTION4'] * 4           # walk old player to (37, 7) → path recorded
       + ['ACTION5']              # save path as ghost, new player at (13, 7)
       + ['ACTION2'] * 7          # new player south, ghost replays R×4 then stays on (37,7)
       + ['ACTION4'] * 5,         # new player east through the opened door to (43, 49) = WIN

    # L2: 31 actions (baseline 175)
    # Two-ghost chain. 3 ghost slots available. Two switches, two doors.
    # Switch[1]=(37,25) controls door[1] (shifts (37,49)→(37,43)).
    # Switch[0]=(13,37) controls door[0] (shifts (13,19)→(13,25)).
    # Neither switch alone opens a path to the goal (25,19). We need BOTH
    # switches held simultaneously — hence two stationary ghosts.
    #
    # Phase A: walk to switch[1], save ghost A with path [L,L].
    # Phase B: walk to switch[0] (12 moves), save ghost B with that 12-move path.
    # Phase C: walk live player toward (7,19) — during these 12 moves, ghost B
    #          replays its 12-move path and ends frozen on switch[0], ghost A
    #          is already frozen on switch[1] (finished its path in move 2).
    # Phase D: both doors now held open. Walk RRR from (7,19) → (25,19) = WIN.
    2: ['ACTION3', 'ACTION3',                                    # LL → switch[1]
        'ACTION5',                                               # save ghost A
        'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2',              # DDDD → (49,49)
        'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3',              # LLLL → (25,49)
        'ACTION1', 'ACTION1',                                    # UU → (25,37)
        'ACTION3', 'ACTION3',                                    # LL → (13,37) switch[0]
        'ACTION5',                                               # save ghost B
        'ACTION1', 'ACTION1', 'ACTION1',                         # UUU → (49,7)
        'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3',              # LLLL
        'ACTION3', 'ACTION3', 'ACTION3',                         # LLL → (7,7)
        'ACTION2', 'ACTION2',                                    # DD → (7,19)
        # 12 live moves done → ghost B frozen on switch[0], door[0] open
        'ACTION4', 'ACTION4', 'ACTION4'],                        # RRR → (25,19) WIN

    # L3: 64 actions (baseline 86)
    # 3 switches, 3 doors, player at (7,19), goal at (18,18) → win at (19,19).
    # - switch[2] at (31,19) LATCHES door[2] (dpdubazedr=True): (49,19)→(43,19)
    #   permanently while that ghost/player remains pressing.
    # - switch[1] at (37,31) holds door[0]: (37,49)→(37,43)
    # - switch[0] at (19,49) holds door[1]: (19,31)→(19,37) — this is what
    #   opens (19,31), the corridor tile needed to reach the goal.
    # All three shifts are required simultaneously to reach the goal.
    #
    # Phase A: walk UURRRRDDDDR → (37,31)=switch[1]; ACTION5 saves ghost A
    # Phase B: walk UURRRRRRRDDDDDDDLLLLL → (19,49)=switch[0]; ACTION5 saves ghost B
    # Phase C: 30 live moves. Ghost A replays (freezes on sw1 by move 11),
    #          ghost B replays (freezes on sw0 by move 21). After move 21 all
    #          doors in winning configuration; walk to (19,19) through (19,31).
    3: (  # Phase A: walk to switch[1] + ACTION5
        ['ACTION1', 'ACTION1', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4',
         'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION4', 'ACTION5']
        # Phase B: walk to switch[0] + ACTION5 (path through switch[2] to latch door[2])
        + ['ACTION1', 'ACTION1',
           'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4',
           'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2',
           'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3',
           'ACTION5']
        # Phase C: 30 live moves. Up to (7,7), right to (49,7), down to (49,49),
        # left to (7,49), up to (7,31), right through (19,31) [door[1] shift],
        # up to (19,19) = WIN.
        + (['ACTION1'] * 2          # UU     → (7,7)
           + ['ACTION4'] * 7         # RRRRRRR → (49,7)
           + ['ACTION2'] * 7         # DDDDDDD → (49,49)
           + ['ACTION3'] * 7         # LLLLLLL → (7,49)
           + ['ACTION1'] * 3         # UUU    → (7,31)
           + ['ACTION4'] * 2         # RR     → (19,31)
           + ['ACTION1'] * 2)        # UU     → (19,19) WIN
    ),

    # L4: 31 actions (baseline 52)
    # New mechanic: ulhhdeoyok teleporter pair at (25,37) and (25,49).
    # Only activates when both switches (sw[0]=(49,25), sw[1]=(31,25)) are held.
    # Door[0] at (7,25) rot=270 is only moved by sw[1].
    # Plan: 2 ghosts, one per switch, then step on ulhh[2] while both held
    # to teleport to ulhh[3], then walk left to (7,49) = WIN.
    #
    # Phase A: DDRRUURRDDD → (49,25)=sw[0]; ACTION5 saves ghost A (11 moves)
    # Phase B: DDRD → (31,25)=sw[1]; ACTION5 saves ghost B (4 moves)
    # Phase C: 14 live moves
    #   - ghost A replays 11-move path → frozen on sw[0] by live move 11
    #   - ghost B replays 4-move path → frozen on sw[1] by live move 4
    #   - live player route: LLL DDDDD RRR [teleport] LLL
    #     (25,7) → (7,7) → (7,37) → ... → (19,37) → R on ulhh[2] → (25,49)
    #     → LLL → (7,49) = WIN
    4: (
        # Phase A
        ['ACTION2', 'ACTION2', 'ACTION4', 'ACTION4', 'ACTION1', 'ACTION1',
         'ACTION4', 'ACTION4', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION5']
        # Phase B
        + ['ACTION2', 'ACTION2', 'ACTION4', 'ACTION2', 'ACTION5']
        # Phase C: LLL DDDDD RRR LLL
        + ['ACTION3', 'ACTION3', 'ACTION3',                  # LLL → (7,7)
           'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2',  # DDDDD → (7,37)
           'ACTION4', 'ACTION4', 'ACTION4',                  # RRR → (25,37)=ulhh[2]
                                                              # → teleport to (25,49)
           'ACTION3', 'ACTION3', 'ACTION3']                  # LLL → (7,49) WIN
    ),

    # L5: 52 actions (baseline 96)
    # Grid expanded (x ∈ [1, 55], y ∈ [7, 55]).
    # 4 switches + 2 teleporters + 3 doors (2 natively latched-but-toggling).
    # - sw[0] (55, 25) transient, NO direct door effect — gates teleport
    # - sw[1] (19, 37) transient → door[0] (19,55)→(19,49) — gates teleport(?)
    # - sw[2] (19, 25) toggle latch → door[1] (37,25)→(31,25)
    # - sw[3] (1, 7)   toggle latch → door[2] (19, 7)→(13, 7)
    # - ulhh[4] (43, 37) ↔ ulhh[5] (43, 49) teleporter pair
    #
    # KEY INSIGHT: latches TOGGLE per press. Ghost paths must leave total
    # press counts on sw[2], sw[3] at ODD values to finish with latched doors.
    #
    # Phase A: walk UDDRRRUURRRRRRDDD → (55,25)=sw[0]; ACTION5 saves ghost A
    #   - Ghost A's recorded path presses sw[3] 1× (latch on) and sw[0] 1×
    # Phase B: walk DDDRRRD → (19,37)=sw[1]; ACTION5 saves ghost B
    #   - Ghost B's path presses sw[1] 1×, never touches sw[2] or sw[3]
    # Phase C: 26 live moves that:
    #   - include one sw[2] press (walk through (19,25)) → latch door[1]
    #   - end on ulhh[4]=(43,37) which teleports to (43,49), then walk to goal
    5: (
        # Phase A: U D D R R R U U R R R R R R D D D + ACTION5
        ['ACTION1', 'ACTION2', 'ACTION2',
         'ACTION4', 'ACTION4', 'ACTION4',
         'ACTION1', 'ACTION1',
         'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4', 'ACTION4',
         'ACTION2', 'ACTION2', 'ACTION2',
         'ACTION5']
        # Phase B: D D D R R R D + ACTION5
        + ['ACTION2', 'ACTION2', 'ACTION2',
           'ACTION4', 'ACTION4', 'ACTION4',
           'ACTION2',
           'ACTION5']
        # Phase C: D R R R D U U U R R R D D D D D R L D L L L L L U U
        + ['ACTION2',                                              # D
           'ACTION4', 'ACTION4', 'ACTION4',                        # RRR
           'ACTION2',                                              # D → sw[2] (latch on)
           'ACTION1', 'ACTION1', 'ACTION1',                        # UUU
           'ACTION4', 'ACTION4', 'ACTION4',                        # RRR
           'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2',  # DDDDD
           'ACTION4',                                              # R → ulhh[4]
           'ACTION3',                                              # L (teleported)
           'ACTION2',                                              # D
           'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3',  # LLLLL
           'ACTION1', 'ACTION1']                                   # UU → WIN
    ),

    # L6: 49 actions (baseline 48 — one action over, level completed)
    # 5 switches (all lqtxaumfed), 5 doors. Player starts (55,31), goal (42,48).
    # Plan: 2 ghosts hold sw[1]=(31,25) and sw[0]=(43,25). Their held doors
    # [0], [1] open the top row. Phase C threads through the opened maze.
    6: (
        # Phase A: LLULL (walk to sw[1]) + ACTION5
        ['ACTION3', 'ACTION3', 'ACTION1', 'ACTION3', 'ACTION3', 'ACTION5']
        # Phase B: LLU (walk to sw[0]) + ACTION5
        + ['ACTION3', 'ACTION3', 'ACTION1', 'ACTION5']
        # Phase C: LLDLLLLUULLLDDDDDRRUDLLUUUUURRRDDRRDDRR
        + ['ACTION3', 'ACTION3', 'ACTION2',
           'ACTION3', 'ACTION3', 'ACTION3', 'ACTION3',
           'ACTION1', 'ACTION1',
           'ACTION3', 'ACTION3', 'ACTION3',
           'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2',
           'ACTION4', 'ACTION4',
           'ACTION1', 'ACTION2',
           'ACTION3', 'ACTION3',
           'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1',
           'ACTION4', 'ACTION4', 'ACTION4',
           'ACTION2', 'ACTION2',
           'ACTION4', 'ACTION4',
           'ACTION2', 'ACTION2',
           'ACTION4', 'ACTION4']
    ),

    # L7: 43 actions (baseline 67)
    # 4 switches + 4 teleporters (pair A: ulhh[4,5], pair B: ulhh[6,7]) + 2 doors.
    # sw[2] press latches door[1] AND activates pair A teleporter.
    # sw[3] shifts door[0] (top row opens) AND latches door[1] (via transit).
    # Ghost A holds sw[3] → door[0] shifted → sw[1] reachable.
    # Ghost B holds sw[1] → ??? → pair B teleporter activates → step to WIN.
    #
    # Phase A: DDLRUULLUU (teleport-chain to sw[3]) + ACTION5 = 11 actions
    # Phase B: DDRRUUUULUURRR (walk to sw[1]) + ACTION5 = 15 actions
    # Phase C: DDRRUUUURRDDDDLLL (walk to ulhh[6], teleport to ulhh[7], LLL to WIN)
    7: (
        # Phase A: D D L R U U L L U U + ACTION5
        ['ACTION2', 'ACTION2', 'ACTION3', 'ACTION4', 'ACTION1', 'ACTION1',
         'ACTION3', 'ACTION3', 'ACTION1', 'ACTION1', 'ACTION5']
        # Phase B: D D R R U U U U L U U R R R + ACTION5
        + ['ACTION2', 'ACTION2', 'ACTION4', 'ACTION4',
           'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1',
           'ACTION3',
           'ACTION1', 'ACTION1',
           'ACTION4', 'ACTION4', 'ACTION4', 'ACTION5']
        # Phase C: D D R R U U U U R R D D D D L L L
        + ['ACTION2', 'ACTION2', 'ACTION4', 'ACTION4',
           'ACTION1', 'ACTION1', 'ACTION1', 'ACTION1',
           'ACTION4', 'ACTION4',
           'ACTION2', 'ACTION2', 'ACTION2', 'ACTION2',
           'ACTION3', 'ACTION3', 'ACTION3']
    ),
}


def verify():
    """Verify known solutions locally against the engine."""
    g = mod.G50t()
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


if __name__ == "__main__":
    verify()
