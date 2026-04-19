"""R11L: dig into feqwz object."""
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


def full_dump(obj, label, depth=0, seen=None):
    if seen is None:
        seen = set()
    obj_id = id(obj)
    if obj_id in seen:
        return
    seen.add(obj_id)
    indent = "  " * depth
    if depth > 3:
        return
    for a in sorted(dir(obj)):
        if a.startswith('_'):
            continue
        try:
            v = getattr(obj, a)
        except Exception:
            continue
        if callable(v):
            continue
        if isinstance(v, (int, bool, str, float)) and not isinstance(v, type):
            print(f"{indent}{a}: {v!r}")
        elif hasattr(v, 'x') and hasattr(v, 'y'):
            name = getattr(v, 'name', '?')
            print(f"{indent}{a}: sprite at ({v.x},{v.y}) name={name}")
        elif isinstance(v, list):
            if v:
                print(f"{indent}{a}: list len={len(v)}")
                for i, item in enumerate(v[:5]):
                    print(f"{indent}  [{i}] {type(item).__name__}")
                    if hasattr(item, 'x'):
                        name = getattr(item, 'name', '?')
                        print(f"{indent}      at ({item.x},{item.y}) name={name}")
        elif isinstance(v, dict):
            if v:
                print(f"{indent}{a}: dict len={len(v)}")
                for k, v2 in list(v.items())[:5]:
                    print(f"{indent}  [{k}] {type(v2).__name__}")


def main():
    g = fresh()
    print("=== Full game attrs ===")
    full_dump(g, "g")

    print(f"\n=== feqwz.imhgqwengg ===")
    for i, item in enumerate(g.feqwz.imhgqwengg):
        print(f"[{i}] {type(item).__name__}")
        if hasattr(item, 'x'):
            print(f"    at ({item.x},{item.y})")
        for a in sorted(dir(item)):
            if a.startswith('_') or callable(getattr(item, a, None)):
                continue
            try:
                v = getattr(item, a)
                if isinstance(v, (int, bool, str, float)) and not isinstance(v, type):
                    print(f"    {a}: {v!r}")
                elif hasattr(v, 'x'):
                    print(f"    {a}: sprite at ({v.x},{v.y})")
                elif isinstance(v, (list, tuple, dict)):
                    print(f"    {a}: {type(v).__name__} len={len(v)}")
            except:
                pass


if __name__ == "__main__":
    main()
