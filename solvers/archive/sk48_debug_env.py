#!/usr/bin/env python3
"""Debug: compare env.step vs direct engine action by action."""

import arc_agi
from arcengine import GameAction, GameState
from arcengine.enums import ActionInput
import numpy as np
import sys

sys.path.insert(0, 'environment_files/sk48/41055498')
from sk48 import Sk48

GA = {'U': GameAction.ACTION1, 'D': GameAction.ACTION2, 'L': GameAction.ACTION3, 'R': GameAction.ACTION4}

# Direct engine
g = Sk48()
def act_direct(action):
    ai = ActionInput(id=action, data={})
    g.perform_action(ai)
    for _ in range(500):
        if g.is_action_complete: break
        g.step()

# Env
arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)
obs = env.reset()

sol = "UUURRRRLDDRLUR"

for i, c in enumerate(sol):
    # Direct
    act_direct(GA[c])
    # Env
    obs = env.step(GA[c], data={})
    print(f"Step {i+1} ({c}): env={obs.state.name}, direct_level={g._current_level_index}, remaining={g.qiercdohl}")

    if obs.state == GameState.WIN:
        print(f"  ENV WIN at step {i+1}!")
        break

    if g._current_level_index > 0:
        print(f"  DIRECT level advanced to {g._current_level_index}!")
        break

print(f"\nFinal: env_state={obs.state.name}, g_level={g._current_level_index}")
