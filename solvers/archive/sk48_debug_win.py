#!/usr/bin/env python3
"""Debug: Why env doesn't report WIN for L1."""

import arc_agi
from arcengine import GameAction, GameState
import sys

sys.path.insert(0, 'environment_files/sk48/41055498')
from sk48 import Sk48
from arcengine.enums import ActionInput

GA = {'U': GameAction.ACTION1, 'D': GameAction.ACTION2, 'L': GameAction.ACTION3, 'R': GameAction.ACTION4}
sol = "UUURRRRLDDRLUR"

# Direct engine
g = Sk48()
def act(g, action):
    ai = ActionInput(id=action, data={})
    g.perform_action(ai)
    for _ in range(500):
        if g.is_action_complete: break
        g.step()

for c in sol:
    act(g, GA[c])
    g.gvtmoopqgy()
    if g.lgdrixfno >= 0 or g._current_level_index > 0:
        print(f"Direct: step '{c}' → lgdrixfno={g.lgdrixfno}, level={g._current_level_index}")

# Env
arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)
obs = env.reset()

# Access game inside env
# Find game object in env
g2 = None
for attr_name in ['_game', 'game', '_env']:
    if hasattr(env, attr_name):
        g2 = getattr(env, attr_name)
        break
if g2 is None:
    # Try nested
    for wrapper_name in ['env', '_env', 'wrapper']:
        wrapper = getattr(env, wrapper_name, None)
        if wrapper:
            for attr_name in ['_game', 'game']:
                if hasattr(wrapper, attr_name):
                    g2 = getattr(wrapper, attr_name)
                    break
        if g2: break
if g2 is None:
    print(f"Can't find game. Env attrs: {[a for a in dir(env) if not a.startswith('__')]}")
    import sys; sys.exit(1)
print(f"Found game via: {type(g2).__name__}")

for i, c in enumerate(sol):
    obs = env.step(GA[c], data={})
    g2.gvtmoopqgy()
    level = g2._current_level_index
    lgd = g2.lgdrixfno
    print(f"Env step {i+1} ({c}): state={obs.state.name}, g_level={level}, lgd={lgd}, remaining={g2.qiercdohl}")
    if obs.state == GameState.WIN:
        break
    if level > 0:
        print("  Game advanced to next level!")
        break

# After L1 in direct, try one more action and see if env catches up
print(f"\nFinal env obs state: {obs.state.name}")
print(f"Game level: {g2._current_level_index}")
