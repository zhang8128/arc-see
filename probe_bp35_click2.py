"""BP35: click with data dict."""
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


def status(g):
    eng = g.oztjzzyqoek
    p = eng.twdpowducb
    return (g._state.name, g.hbqwwgceeqp, (p.x, p.y))


def main():
    # click on various positions
    for x, y in [(0, 0), (32, 32), (18, 138), (18, 100), (18, 60), (0, 60)]:
        g = fresh()
        try:
            ai = ActionInput(id=GameAction.ACTION6, data={'x': x, 'y': y})
            g.perform_action(ai)
            print(f"click({x},{y}): {status(g)}")
        except Exception as e:
            print(f"click({x},{y}): error {type(e).__name__}: {e}")

    # Now try a sequence of clicks
    print("\n--- Clicking multiple times at (18, 100) ---")
    g = fresh()
    for i in range(5):
        try:
            g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': 18, 'y': 100}))
            print(f"  click {i+1}: {status(g)}")
        except Exception as e:
            print(f"  click {i+1}: error {e}")
            break

    # Fun experiment: scan y=60 to 140 at x=18 to find where clicks matter
    print("\n--- Scanning y at x=18 ---")
    for y in range(60, 145, 5):
        g = fresh()
        try:
            g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': 18, 'y': y}))
            s = status(g)
            eng = g.oztjzzyqoek
            print(f"  y={y}: {s}")
        except Exception as e:
            pass

    # Scan x at y=138 (player row)
    print("\n--- Scanning x at y=138 ---")
    for x in range(0, 64, 3):
        g = fresh()
        try:
            g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': x, 'y': 138}))
            s = status(g)
            print(f"  x={x}: {s}")
        except Exception as e:
            pass


if __name__ == "__main__":
    main()
