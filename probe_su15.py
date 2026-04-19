"""Validate pure-Python sim against the engine on L1 and L2."""
import importlib.util
from arcengine import GameAction, ActionInput
from solutions.su15_sim import click as sim_click, is_won, initial_state_from_engine, SPRITE_SIZE

spec = importlib.util.spec_from_file_location('su15', 'environment_files/su15/4c352900/su15.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def engine_fruits(g):
    out = []
    for s in g.current_level.get_sprites_by_tag('fruit'):
        try:
            k = int(s.name)
        except ValueError:
            k = -1
        out.append((k, s.x, s.y))
    return tuple(sorted(out))


def compare(level_idx, click_seq, label):
    print(f"\n=== {label}: L{level_idx + 1} ===")
    # Engine
    g = mod.Su15(); g.set_level(level_idx)
    # Sim
    sim_fruits, goal_rect, gspec = initial_state_from_engine(level_idx)

    eng = engine_fruits(g)
    sim = tuple(sorted(sim_fruits))
    print(f"  init engine: {eng}")
    print(f"  init sim:    {sim}")
    if eng != sim:
        print("  INIT MISMATCH")
        return False

    for i, (cx, cy) in enumerate(click_seq):
        g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': cx, 'y': cy}))
        sim_fruits, info = sim_click(sim_fruits, cx, cy)

        eng = engine_fruits(g)
        sim_sorted = tuple(sorted(sim_fruits))
        eng_won = g._current_level_index > level_idx or g._state.name == "WIN"
        sim_won = is_won(sim_fruits, goal_rect, gspec)

        if eng != sim_sorted or eng_won != sim_won:
            print(f"  MISMATCH at click {i+1} ({cx},{cy}) info={info}")
            print(f"    engine: {eng} won={eng_won}")
            print(f"    sim:    {sim_sorted} won={sim_won}")
            return False
        else:
            print(f"  click {i+1} ({cx},{cy}) info={info} ✓ (n={len(eng)} won={eng_won})")
            if eng_won:
                print(f"  WIN @ click {i+1}")
                return True
    print(f"  end: {len(eng)} fruits, eng_won={eng_won}, sim_won={sim_won}")
    return eng == sim_sorted


# L1 — manual delivery
l1_clicks = [(10, 52), (16, 45), (22, 38), (28, 31), (34, 24), (40, 17), (44, 10)]
compare(0, l1_clicks, "L1 manual delivery")

# L2 — 4 merges
l2_merges = [(39, 38), (17, 39), (15, 56), (48, 55)]
compare(1, l2_merges, "L2 first 4 merges")
