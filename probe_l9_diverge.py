"""Parity check: drive a deliberate multi-click sequence on L9 and compare
sim v2 vs engine at every step. Exercises kind-1 + kind-1 → kind-2 enemy merge
and kind-2 enemy chase behavior, which L1-L8 never did."""
import importlib.util, json
from arcengine import GameAction, ActionInput
from solutions.su15_sim_v2 import (
    click as sim_click, is_won, initial_state_from_engine,
    SPRITE_SIZE, ENEMY_W, ENEMY_H,
)

spec = importlib.util.spec_from_file_location('su15', 'environment_files/su15/4c352900/su15.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with open('solutions/su15_solutions.json') as f:
    sols = json.load(f)


def engine_fruits(g):
    out = []
    for s in g.current_level.get_sprites_by_tag('fruit'):
        try:
            k = int(s.name)
        except ValueError:
            k = -1
        out.append((k, s.x, s.y))
    return tuple(sorted(out))


def engine_enemies(g):
    out = []
    all_tags = g.current_level.get_all_tags()
    for tag, ek in (('enemy', 1), ('enemy2', 2), ('enemy3', 3)):
        if tag not in all_tags:
            continue
        for s in g.current_level.get_sprites_by_tag(tag):
            out.append((ek, s.x, s.y))
    return tuple(sorted(out))


def sim_enemies_kxy(state):
    return tuple(sorted((e[0], e[1], e[2]) for e in state[1]))


def replay(label, clicks):
    print(f"\n=== {label} ===")
    g = mod.Su15()
    for prev in range(8):
        for (cx, cy) in sols[str(prev)]:
            g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
    assert g._current_level_index == 8

    state, goal_rects, fspec, espec = initial_state_from_engine(8, sols)
    print(f"  init: fruits={tuple(sorted(state[0]))}  enemies={sim_enemies_kxy(state)}")
    assert tuple(sorted(state[0])) == engine_fruits(g), "initial fruit mismatch"
    assert sim_enemies_kxy(state) == engine_enemies(g), "initial enemy mismatch"

    for i, (cx, cy) in enumerate(clicks):
        new_state, info = sim_click(state, cx, cy)
        g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))

        sim_f = tuple(sorted(new_state[0]))
        sim_e = sim_enemies_kxy(new_state)
        eng_f = engine_fruits(g)
        eng_e = engine_enemies(g)
        ok = (sim_f == eng_f) and (sim_e == eng_e)

        marker = "OK" if ok else "DIVERGE"
        print(f"  click {i+1:2d} ({cx:2d},{cy:2d}) info={info} {marker}")
        if not ok:
            print(f"    sim fruits:  {sim_f}")
            print(f"    eng fruits:  {eng_f}")
            print(f"    sim enemies: {sim_e}")
            print(f"    eng enemies: {eng_e}")
            return False

        state = new_state
        if g._current_level_index > 8:
            print(f"    engine WIN @ click {i+1}")
            return True

    return True


# Sequence 1: produce kind-2 enemy via left pair merge, then continue some chase clicks
seq1 = [(16, 14), (20, 18), (24, 22), (30, 40)]
replay("Seq 1: left pair merge + chase", seq1)

# Sequence 2: merge fruits, then merge left enemies, then produce a kind-2 and move it
seq2 = [(17, 54), (16, 14), (30, 50), (38, 51)]
replay("Seq 2: fruit merge + enemy merge + chase near kind-5", seq2)

# Sequence 3: two separate kind-2 enemies — merge left pair + right pair
# Right pair needs 2-3 setup clicks since their initial distance > vacuum radius.
# Start by vacuuming each right enemy toward the other iteratively.
seq3 = [(16, 14), (52, 15), (52, 25), (52, 22)]
replay("Seq 3: left merge + right pair convergence attempt", seq3)
