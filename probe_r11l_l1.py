"""R11L L1: entity dump and click exploration."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'r11l', 'environment_files/r11l/aa269680/r11l.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def find_game_class():
    for name in dir(mod):
        obj = getattr(mod, name)
        if isinstance(obj, type) and 'r11l' in name.lower():
            return obj
    return None


def fresh(level=0):
    cls = find_game_class()
    g = cls()
    g.set_level(level)
    return g


def main():
    g = fresh()
    print(f"State: {g._state.name}")
    for attr in ('available_actions', 'hbqwwgceeqp', 'win_score', 'game_id'):
        if hasattr(g, attr):
            print(f"  {attr}: {getattr(g, attr)}")

    # Find the engine
    print("\nTop-level attrs:")
    for a in sorted(dir(g)):
        if a.startswith('_'):
            continue
        try:
            v = getattr(g, a)
        except Exception:
            continue
        if callable(v):
            continue
        print(f"  {a}: {type(v).__name__}")

    # Find main engine
    for a in dir(g):
        if a.startswith('_'):
            continue
        try:
            v = getattr(g, a)
            if hasattr(v, '__dict__') and not callable(v):
                attrs = [x for x in dir(v) if not x.startswith('_')]
                if len(attrs) > 15:
                    print(f"\nPossible engine g.{a}: {type(v).__name__} with {len(attrs)} attrs")
        except Exception:
            pass


if __name__ == "__main__":
    main()
