"""G50T: enumerate available actions and test boundaries."""
import copy
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main():
    g = mod.G50t()
    g.set_level(0)

    # List all GameAction enum members
    print("=== All GameAction values ===")
    for name in dir(GameAction):
        if not name.startswith('_'):
            val = getattr(GameAction, name)
            print(f"  {name}: {val}")

    # What methods does g have?
    print("\n=== g methods related to action/available ===")
    for name in dir(g):
        if 'action' in name.lower() or 'available' in name.lower():
            v = getattr(g, name)
            print(f"  g.{name}: {v}")

    # Try every action from start, including ones we haven't
    print("\n=== Try every GameAction from start ===")
    all_actions = [a for a in dir(GameAction) if a.startswith('ACTION')]
    for a in sorted(all_actions):
        g2 = copy.deepcopy(g)
        try:
            g2.perform_action(ActionInput(id=getattr(GameAction, a)))
            p = g2.vgwycxsxjz.dzxunlkwxt
            print(f"  {a}: player=({p.x},{p.y}) state={g2._state.name}")
        except Exception as e:
            print(f"  {a}: EXCEPTION {type(e).__name__}: {e}")

    # Also try RESET and any other enum
    for other in ['RESET', 'CLICK', 'NONE']:
        if hasattr(GameAction, other):
            g2 = copy.deepcopy(g)
            try:
                g2.perform_action(ActionInput(id=getattr(GameAction, other)))
                p = g2.vgwycxsxjz.dzxunlkwxt
                print(f"  {other}: player=({p.x},{p.y}) state={g2._state.name}")
            except Exception as e:
                print(f"  {other}: EXCEPTION {e}")

    # Try ACTION6 with data (click semantics)
    g2 = copy.deepcopy(g)
    try:
        g2.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': 42, 'y': 48}))
        print(f"\n  ACTION6(42,48): OK state={g2._state.name}")
    except Exception as e:
        print(f"\n  ACTION6(42,48): EXCEPTION {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
