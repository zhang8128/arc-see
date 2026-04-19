"""BP35 L1: dive into the game engine."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'bp35', 'environment_files/bp35/0a0ad940/bp35.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def main():
    g = mod.Bp35()
    g.set_level(0)

    print(f"State: {g._state.name}, level_idx: {g._current_level_index}")
    print(f"Available actions: {g.available_actions}")

    # Try all actions to see what moves the player or changes state
    for action_name in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4', 'ACTION5', 'ACTION6']:
        if hasattr(GameAction, action_name):
            print(f"\n-- Trying {action_name} --")
            g = mod.Bp35()
            g.set_level(0)
            try:
                g.perform_action(ActionInput(id=getattr(GameAction, action_name)))
                print(f"  state: {g._state.name}")
                print(f"  score: {g.hbqwwgceeqp}")
            except Exception as e:
                print(f"  error: {e}")

    # Explore the main engine object
    print("\n=== oztjzzyqoek (game engine?) ===")
    g = mod.Bp35()
    g.set_level(0)
    eng = g.oztjzzyqoek
    print(f"Type: {type(eng).__name__}")
    for a in sorted(dir(eng)):
        if a.startswith('_'):
            continue
        try:
            v = getattr(eng, a)
        except Exception:
            continue
        if callable(v):
            continue
        if isinstance(v, list):
            if v:
                tn = set(type(x).__name__ for x in v)
                print(f"  {a}: list[{len(v)}] {tn}")
        elif isinstance(v, dict):
            if v:
                print(f"  {a}: dict[{len(v)}]")
        elif isinstance(v, (int, bool, str, float)) and not isinstance(v, type):
            print(f"  {a}: {v!r}")
        elif hasattr(v, 'x') and hasattr(v, 'y'):
            print(f"  {a}: sprite at ({v.x},{v.y}) type={type(v).__name__}")
        else:
            print(f"  {a}: {type(v).__name__}")


if __name__ == "__main__":
    main()
