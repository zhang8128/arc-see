#!/usr/bin/env python3
"""S5I5 initial probe — understand game basics."""
import importlib.util, copy, numpy as np
from arcengine import GameAction, ActionInput, GameState

spec = importlib.util.spec_from_file_location('s5i5', 'environment_files/s5i5/a48e4b1d/s5i5.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

g = mod.S5i5()
print(f"Game class: {type(g).__name__}")
print(f"Available actions: {g._available_actions}")
print(f"Num levels: {len(g._levels)}")
print(f"State: {g._state.name}")

# Check each level's baseline
BASELINES = [19, 57, 85, 203, 82, 30, 76, 56]
for i in range(len(g._levels)):
    g2 = mod.S5i5()
    g2.set_level(i)
    print(f"\n=== Level {i+1} (baseline {BASELINES[i]}) ===")

    # Get pixels
    frame = g2.get_pixels(0, 0, 64, 64)
    unique_colors = sorted(set(int(v) for v in np.unique(frame) if v >= 0))
    print(f"  Colors: {unique_colors}")
    print(f"  Non-empty pixels: {np.sum(frame >= 0)}")

    # List sprites
    sprites = g2.current_level.get_sprites()
    print(f"  Sprites: {len(sprites)}")
    for s in sprites[:15]:
        tags = list(s.tags) if hasattr(s, 'tags') else []
        print(f"    {s.name:30s} pos=({s.x},{s.y}) size={s.width}x{s.height} tags={tags}")
    if len(sprites) > 15:
        print(f"    ... and {len(sprites)-15} more")

    # Try each action to see what's available
    for action_id in g2._available_actions:
        ga = getattr(GameAction, f"ACTION{action_id}")
        g3 = copy.deepcopy(g2)
        try:
            g3.perform_action(ActionInput(id=ga, data={}))
            frame2 = g3.get_pixels(0, 0, 64, 64)
            diff = np.sum(frame != frame2)
            state = g3._state.name
            lvl = g3._current_level_index
            print(f"  ACTION{action_id}: {diff} pixels changed, state={state}, level_idx={lvl}")
        except Exception as e:
            print(f"  ACTION{action_id}: ERROR {e}")

    # Try click at various positions
    if 6 in g2._available_actions:
        click_results = []
        for x in range(0, 64, 8):
            for y in range(0, 64, 8):
                g3 = copy.deepcopy(g2)
                try:
                    g3.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': x, 'y': y}))
                    frame2 = g3.get_pixels(0, 0, 64, 64)
                    diff = np.sum(frame != frame2)
                    if diff > 0:
                        click_results.append((x, y, diff, g3._state.name))
                except:
                    pass
        print(f"  Clicks with effects: {len(click_results)} / {64} positions tested")
        for x, y, diff, state in click_results[:10]:
            print(f"    click({x},{y}): {diff} px changed, state={state}")

    if i >= 1:  # Only probe L1-L2 in detail
        break
