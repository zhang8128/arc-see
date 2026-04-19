"""R11L L2: run the arc-see lenses on L2 frame and see what they reveal.

Bypass the MCP server — directly import the lens classes and run them on
the L2 frame. This mimics what `perceive()` would do.
"""
import numpy as np
import arc_agi
from arcengine import GameAction

# Import arc_see lenses
from arc_see.session import GameSession


def main():
    arcade = arc_agi.Arcade()
    env = arcade.make("r11l-aa269680", render_mode=None)

    # Get to L2
    env.reset()
    L1 = [(36, 13), (26, 61), (42, 30)]
    for cx, cy in L1:
        env.step(GameAction.ACTION6, data={"x": cx, "y": cy})

    # Create a GameSession and run perceive()
    session = GameSession(env)

    # session.reset() will reset the env, but we want to keep L2 state.
    # Instead, just grab the current frame and manually feed it.
    obs = env.step(GameAction.ACTION6, data={"x": 10, "y": 10})  # sacrifice 1 click to get frame
    g = np.array(obs.frame[-1], dtype=np.int64)
    session.frames = [g]
    session.last_state = obs.state
    session.turn_count = 1
    session._cells_changed_history = []

    annotations = session.composer.perceive(g, [])
    session.annotations = annotations

    # Print lens summaries
    for name, ann in annotations.items():
        if hasattr(ann, '__dict__'):
            print(f"\n=== {name} ===")
            # Try to get interesting attributes
            for attr in ['labels', 'regions', 'mask', 'goals', 'mechanics', 'count', 'values']:
                if hasattr(ann, attr):
                    v = getattr(ann, attr)
                    if v is not None:
                        r = repr(v)
                        if len(r) > 300:
                            r = r[:300] + "..."
                        print(f"  {attr}: {r}")

    # Format perception (text output like MCP)
    print("\n===== perceive() full output =====")
    formatted = session._format_perception(annotations, g)
    print(formatted[:3000])


if __name__ == "__main__":
    main()
