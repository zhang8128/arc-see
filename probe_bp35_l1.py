"""BP35 L1: entity dump, action exploration."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'bp35', 'environment_files/bp35/0a0ad940/bp35.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def make(level=0):
    # Find the class — common naming is capitalized module name
    klass = None
    for name in dir(mod):
        obj = getattr(mod, name)
        if isinstance(obj, type) and name.lower().startswith('bp35'):
            klass = obj
            break
    if klass is None:
        # Fallback: find any class with 'set_level' method
        for name in dir(mod):
            obj = getattr(mod, name)
            if isinstance(obj, type):
                try:
                    inst = obj()
                    if hasattr(inst, 'set_level'):
                        klass = obj
                        break
                except Exception:
                    pass
    print(f"Found game class: {klass}")
    g = klass()
    g.set_level(level)
    return g


def main():
    g = make(0)
    print(f"\nL1 state: {g._state.name}, level_idx: {g._current_level_index}")
    # Check for typical attributes
    for attr in ['vgwycxsxjz', 'eng', 'engine', 'level', 'state']:
        if hasattr(g, attr):
            v = getattr(g, attr)
            print(f"  g.{attr} = {type(v).__name__}")

    # Dump top-level attrs
    print("\nTop-level attributes:")
    for a in sorted(dir(g)):
        if a.startswith('_'):
            continue
        try:
            v = getattr(g, a)
        except Exception:
            continue
        if not callable(v):
            print(f"  {a} = {type(v).__name__}")

    # Try to find entity lists — scan the engine
    eng_attr = None
    for a in sorted(dir(g)):
        if a.startswith('_'):
            continue
        try:
            v = getattr(g, a)
            if hasattr(v, '__dict__') and len(dir(v)) > 20:
                # Probably the engine
                if eng_attr is None or a in ('vgwycxsxjz', 'eng', 'engine'):
                    eng_attr = a
        except Exception:
            pass

    if eng_attr:
        eng = getattr(g, eng_attr)
        print(f"\nEngine via g.{eng_attr}:")
        for a in sorted(dir(eng)):
            if a.startswith('_'):
                continue
            try:
                v = getattr(eng, a)
                if isinstance(v, list):
                    if v:
                        tn = set(type(x).__name__ for x in v)
                        print(f"  {a}: list[{len(v)}] {tn}")
                elif isinstance(v, dict):
                    if v:
                        print(f"  {a}: dict[{len(v)}]")
                elif isinstance(v, (int, bool)) and not isinstance(v, type):
                    print(f"  {a}: {v}")
                elif hasattr(v, 'x') and hasattr(v, 'y'):
                    print(f"  {a}: sprite at ({v.x},{v.y}) type={type(v).__name__}")
            except Exception:
                pass


if __name__ == "__main__":
    main()
