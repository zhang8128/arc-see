"""BP35: try sequences of actions, understand the click mechanic."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'bp35', 'environment_files/bp35/0a0ad940/bp35.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fresh(level=0):
    g = mod.Bp35()
    g.set_level(level)
    return g


def main():
    # What are available actions? [3, 4, 6, 7] — so ACTION3, ACTION4, ACTION6, ACTION7
    # ACTION6 might be click
    g = fresh()
    print(f"Initial state: {g._state.name}, score: {g.hbqwwgceeqp}, win_score: {g.win_score}")
    print(f"Actions: {g.available_actions}")

    # Find a visible player — likely twdpowducb
    eng = g.oztjzzyqoek
    print(f"\nEntity player? twdpowducb: {eng.twdpowducb}")
    for a in ['x', 'y', 'width', 'height']:
        print(f"  twdpowducb.{a} = {getattr(eng.twdpowducb, a, None)}")

    # Actions 3, 4, 7 — try each and record score/state
    for action_name in ['ACTION3', 'ACTION4', 'ACTION7']:
        g = fresh()
        g.perform_action(ActionInput(id=getattr(GameAction, action_name)))
        print(f"\n{action_name}: state={g._state.name} score={g.hbqwwgceeqp} player_pos={(eng.twdpowducb.x, eng.twdpowducb.y)}")
        # Check what moved
        eng2 = g.oztjzzyqoek
        print(f"  player now: ({eng2.twdpowducb.x}, {eng2.twdpowducb.y})")

    # Try ACTION6 (click) with various coordinates
    print("\n=== ACTION6 click tests ===")
    for x, y in [(0, 0), (32, 32), (18, 138), (20, 100)]:
        g = fresh()
        try:
            g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': x, 'y': y}))
            print(f"  click({x},{y}): state={g._state.name} score={g.hbqwwgceeqp}")
        except Exception as e:
            print(f"  click({x},{y}): error {e}")

    # Try building the ActionInput with click properly
    g = fresh()
    try:
        ai = ActionInput(id=GameAction.ACTION6, x=18, y=138)
        g.perform_action(ai)
        print(f"\nclick via ActionInput(x=18,y=138): state={g._state.name} score={g.hbqwwgceeqp}")
    except Exception as e:
        print(f"  error: {e}")


if __name__ == "__main__":
    main()
