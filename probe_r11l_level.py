"""R11L: inspect current_level for goal info; test leg movement constraints."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'r11l', 'environment_files/r11l/aa269680/r11l.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fresh(level=0):
    g = mod.R11l()
    g.set_level(level)
    return g


def click(g, x, y):
    g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': x, 'y': y}))


def main():
    g = fresh()
    print(f"current_level: {g.current_level}")
    print(f"type: {type(g.current_level).__name__}")
    print(f"\nAttrs of current_level:")
    for a in sorted(dir(g.current_level)):
        if a.startswith('_'):
            continue
        try:
            v = getattr(g.current_level, a)
            if callable(v):
                continue
            print(f"  {a}: {type(v).__name__}", end="")
            if isinstance(v, (int, bool, str, float)) and not isinstance(v, type):
                print(f" = {v!r}")
            elif hasattr(v, 'x'):
                print(f" at ({v.x},{v.y})")
            elif isinstance(v, (list, tuple, dict)):
                print(f" len={len(v)}")
            else:
                print()
        except Exception as e:
            print(f"  {a}: ERROR {e}")

    # Also check feqwz — non-trivial type
    print(f"\nfeqwz: {g.feqwz}, type={type(g.feqwz).__name__}")
    for a in sorted(dir(g.feqwz)):
        if a.startswith('_') or callable(getattr(g.feqwz, a, None)):
            continue
        try:
            v = getattr(g.feqwz, a)
            if isinstance(v, (int, bool, str, float)) and not isinstance(v, type):
                print(f"  {a}: {v!r}")
            elif hasattr(v, 'x'):
                print(f"  {a}: sprite at ({v.x},{v.y})")
            elif isinstance(v, (list, tuple, dict)):
                print(f"  {a}: len={len(v)}")
            else:
                print(f"  {a}: {type(v).__name__}")
        except:
            pass


if __name__ == "__main__":
    main()
