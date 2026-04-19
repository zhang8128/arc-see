"""G50T L1: dump entity positions in the engine lists."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def dump_list(eng, name):
    items = getattr(eng, name, [])
    print(f"\n  {name}: {len(items)} items")
    for i, item in enumerate(items):
        tname = type(item).__name__
        x = getattr(item, 'x', '?')
        y = getattr(item, 'y', '?')
        print(f"    [{i}] {tname} x={x} y={y}")
        # Show all int/bool attrs of the entity
        for a in sorted(dir(item)):
            if a.startswith('_') or a in ('x', 'y'):
                continue
            try:
                v = getattr(item, a)
            except Exception:
                continue
            if callable(v):
                continue
            if isinstance(v, (int, bool, str)) and not isinstance(v, bool):
                print(f"        {a} = {v!r}")
            elif isinstance(v, bool):
                print(f"        {a} = {v!r}")


def dump_single(eng, name):
    ent = getattr(eng, name, None)
    if ent is None:
        print(f"\n  {name}: None")
        return
    tname = type(ent).__name__
    x = getattr(ent, 'x', '?')
    y = getattr(ent, 'y', '?')
    print(f"\n  {name}: {tname} x={x} y={y}")
    for a in sorted(dir(ent)):
        if a.startswith('_') or a in ('x', 'y') or callable(getattr(ent, a, None)):
            continue
        try:
            v = getattr(ent, a)
        except Exception:
            continue
        if isinstance(v, (int, bool, str)):
            print(f"      {a} = {v!r}")


def main():
    g = mod.G50t()
    g.set_level(0)
    eng = g.vgwycxsxjz
    print(f"=== G50T L1 engine entities ===")
    print(f"Player starts at ({g.vgwycxsxjz.dzxunlkwxt.x}, {g.vgwycxsxjz.dzxunlkwxt.y})")

    # The three lists
    dump_list(eng, 'drofvwhbxb')
    dump_list(eng, 'hamayflsib')
    dump_list(eng, 'uwxkstolmf')

    # The single refs
    dump_single(eng, 'whftgckbcu')
    dump_single(eng, 'afbbgvkpip')
    dump_single(eng, 'dzxunlkwxt')
    dump_single(eng, 'zmqoxwsfgh')

    # All engine int/bool attrs
    print("\n=== Engine-level int/bool attrs ===")
    for name in sorted(dir(eng)):
        if name.startswith('_'):
            continue
        try:
            v = getattr(eng, name)
        except Exception:
            continue
        if isinstance(v, (int, bool)):
            print(f"  {name}: {v}")


if __name__ == "__main__":
    main()
