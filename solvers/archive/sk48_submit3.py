#!/usr/bin/env python3
"""SK48 — Debug env vs direct engine."""

import arc_agi
from arcengine import GameAction, GameState
from arcengine.enums import ActionInput
import sys

sys.path.insert(0, 'environment_files/sk48/41055498')
from sk48 import Sk48

# Test 1: Direct engine
print("=== Direct Engine ===")
g = Sk48()

def act(g, action, data=None):
    ai = ActionInput(id=action, data=data or {})
    g.perform_action(ai)
    for _ in range(500):
        if g.is_action_complete: break
        g.step()

sol = "UUURRRRLDDRLUR"
GA = {'U': GameAction.ACTION1, 'D': GameAction.ACTION2, 'L': GameAction.ACTION3, 'R': GameAction.ACTION4}

for c in sol:
    act(g, GA[c])

g.gvtmoopqgy()
print(f"Direct: lgdrixfno={g.lgdrixfno}, level={g._current_level_index}")
if g.lgdrixfno >= 0:
    print("Direct: L1 WON!")
else:
    print("Direct: L1 not won")

# Test 2: Arc AGI env
print("\n=== Arc AGI Env ===")
arcade = arc_agi.Arcade()
env = arcade.make("sk48-41055498", render_mode=None)
obs = env.reset()

# Check env internals
print(f"Env type: {type(env).__name__}")
print(f"Env dir: {[a for a in dir(env) if not a.startswith('_')]}")

for c in sol:
    obs = env.step(GA[c])

print(f"Env state: {obs.state.name}")

# Check if the env uses a different game instance
if hasattr(env, '_game'):
    g2 = env._game
    print(f"Env game type: {type(g2).__name__}")
elif hasattr(env, 'env'):
    print(f"Env inner: {type(env.env).__name__}")
    if hasattr(env.env, '_game'):
        g2 = env.env._game
        print(f"Inner game type: {type(g2).__name__}")

# Try ACTION5 which the env might need but direct doesn't have
print(f"\nEnv action space: {[a.name for a in env.action_space]}")

# Maybe the env solution needs ACTION5?
print(f"\nDoes env have ACTION5? {'ACTION5' in [a.name for a in env.action_space]}")
