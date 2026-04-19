"""G50T L2: dump entity positions, hunt for new entity types.

Usage: uv run python probe_g50t_l2.py [level_index]
  level_index: 0-based (so L2 = 1). Default 1.
"""
import importlib.util
import sys

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


# Known entity list / single-ref names from L1 exploration
KNOWN_LISTS = ['drofvwhbxb', 'hamayflsib', 'uwxkstolmf', 'rloltuowth', 'kgvnkyaimw']
KNOWN_SINGLES = ['whftgckbcu', 'afbbgvkpip', 'dzxunlkwxt', 'zmqoxwsfgh']
# Suspected but never-seen
MYSTERY = ['crfcpstubm', 'umziwqcvfy', 'hyztgkifvb', 'tddbvyfbvq', 'alyzsfkumg']


def attrs_of(obj):
    """Return list of (name, value) for non-callable, non-dunder attrs."""
    out = []
    for a in sorted(dir(obj)):
        if a.startswith('_'):
            continue
        try:
            v = getattr(obj, a)
        except Exception:
            continue
        if callable(v):
            continue
        out.append((a, v))
    return out


def dump_entity(ent, indent='    '):
    """Print all meaningful attrs on an entity."""
    for a, v in attrs_of(ent):
        if a in ('x', 'y'):
            continue
        if isinstance(v, (int, float, bool, str)):
            print(f"{indent}{a} = {v!r}")
        elif isinstance(v, (list, tuple)):
            if v:
                print(f"{indent}{a} = <{type(v).__name__} len={len(v)}>")
        elif v is None:
            pass
        else:
            tn = type(v).__name__
            # skip heavyweight engine objects but show small ones
            if tn in ('int', 'float', 'str', 'bool'):
                print(f"{indent}{a} = {v!r}")


def dump_list(eng, name):
    items = getattr(eng, name, None)
    if items is None:
        return
    if not isinstance(items, list):
        print(f"\n  {name}: <not a list, type={type(items).__name__}>")
        return
    print(f"\n  {name}: {len(items)} items")
    for i, item in enumerate(items):
        tname = type(item).__name__
        x = getattr(item, 'x', '?')
        y = getattr(item, 'y', '?')
        tag = getattr(item, 'yqcbupelnm', None) or getattr(item, 'tag', None)
        print(f"    [{i}] {tname} x={x} y={y}" + (f" tag={tag}" if tag else ""))
        dump_entity(item, indent='        ')


def dump_single(eng, name):
    ent = getattr(eng, name, None)
    if ent is None:
        return
    tname = type(ent).__name__
    x = getattr(ent, 'x', '?')
    y = getattr(ent, 'y', '?')
    print(f"\n  {name}: {tname} x={x} y={y}")
    dump_entity(ent, indent='      ')


def scan_for_new_entities(eng):
    """Walk every attr on engine, report ones containing sprites we don't know."""
    print("\n=== Full engine attribute scan (sprites, lists) ===")
    for name in sorted(dir(eng)):
        if name.startswith('_'):
            continue
        try:
            v = getattr(eng, name)
        except Exception:
            continue
        if callable(v):
            continue
        if isinstance(v, list):
            if v:
                tnames = set(type(x).__name__ for x in v)
                print(f"  {name}: list[{len(v)}] types={tnames}")
        elif isinstance(v, dict):
            if v:
                print(f"  {name}: dict[{len(v)}] sample_keys={list(v.keys())[:3]}")
        elif hasattr(v, 'x') and hasattr(v, 'y'):
            print(f"  {name}: {type(v).__name__} at ({v.x},{v.y})")


def main():
    level = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    g = mod.G50t()
    g.set_level(level)
    eng = g.vgwycxsxjz
    p = eng.dzxunlkwxt
    print(f"=== G50T level_index={level} (displayed as L{level+1}) ===")
    print(f"Player starts at ({p.x}, {p.y})")
    goal = getattr(eng, 'whftgckbcu', None)
    if goal:
        print(f"Goal at ({goal.x}, {goal.y}) -> win requires player ({goal.x+1}, {goal.y+1})")

    # Known lists
    for name in KNOWN_LISTS:
        dump_list(eng, name)

    # Known singles
    for name in KNOWN_SINGLES:
        dump_single(eng, name)

    # Mystery entity names
    print("\n=== Mystery entity slots ===")
    for name in MYSTERY:
        v = getattr(eng, name, None)
        if v is None:
            print(f"  {name}: None/missing")
            continue
        if isinstance(v, list):
            print(f"  {name}: list len={len(v)}")
            if v:
                dump_list(eng, name)
        else:
            print(f"  {name}: {type(v).__name__}")
            dump_single(eng, name)

    # Full scan for anything we missed
    scan_for_new_entities(eng)

    # Engine scalars
    print("\n=== Engine-level int/bool scalars ===")
    for name in sorted(dir(eng)):
        if name.startswith('_'):
            continue
        try:
            v = getattr(eng, name)
        except Exception:
            continue
        if isinstance(v, (int, bool)) and not isinstance(v, type):
            print(f"  {name}: {v}")


if __name__ == "__main__":
    main()
