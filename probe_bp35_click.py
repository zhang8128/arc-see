"""BP35: figure out click mechanic (ACTION6 with coords)."""
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
    # First, see what ActionInput accepts
    g = fresh()
    print(f"ActionInput fields: {g.action.model_fields}")

    # Try with x, y directly
    for x, y in [(18, 138), (0, 0), (32, 32)]:
        g = fresh()
        try:
            ai = ActionInput(id=GameAction.ACTION6, x=x, y=y)
            print(f"\nAI({x},{y}): {ai}")
            g.perform_action(ai)
            eng = g.oztjzzyqoek
            print(f"  state={g._state.name} score={g.hbqwwgceeqp} player=({eng.twdpowducb.x},{eng.twdpowducb.y})")
        except Exception as e:
            print(f"  error: {type(e).__name__}: {e}")

    # Show sprite layout
    g = fresh()
    eng = g.oztjzzyqoek
    print(f"\n=== kiopdubfvza entities (30) ===")
    for key in list(eng.kiopdubfvza.keys())[:30]:
        v = eng.kiopdubfvza[key]
        x = getattr(v, 'x', '?')
        y = getattr(v, 'y', '?')
        tn = type(v).__name__
        print(f"  {key}: {tn} at ({x},{y})")


if __name__ == "__main__":
    main()
