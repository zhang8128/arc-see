"""G50T: inspect grid_size, afbbgvkpip.xmdjbwrpmv sprite, and try to find a move-validator."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def dump_sprite(s, tag):
    print(f"\n--- {tag} ({type(s).__name__}) ---")
    for name in sorted(dir(s)):
        if name.startswith('_'):
            continue
        try:
            v = getattr(s, name)
        except Exception:
            continue
        if callable(v):
            continue
        if isinstance(v, (int, float, bool, str)):
            print(f"  {name}: {v!r}")
        elif isinstance(v, (list, tuple)):
            print(f"  {name}: {type(v).__name__} len={len(v)} first5={list(v)[:5]!r}")
        elif v is None:
            print(f"  {name}: None")
        else:
            print(f"  {name}: <{type(v).__name__}>")


def main():
    g = mod.G50t()
    g.set_level(0)

    # 1. grid_size
    lvl = g.current_level
    print(f"current_level.grid_size = {lvl.grid_size}")
    print(f"type = {type(lvl.grid_size)}")

    # 2. afbbgvkpip.xmdjbwrpmv — the "base sprite"
    afb = g.vgwycxsxjz.afbbgvkpip
    inner = afb.xmdjbwrpmv
    dump_sprite(inner, "afbbgvkpip.xmdjbwrpmv")

    # 3. Does the inner sprite have pixel data?
    if hasattr(inner, 'pixels'):
        px = inner.pixels
        print(f"\ninner.pixels type: {type(px).__name__}")
        try:
            print(f"  len: {len(px)}")
            print(f"  shape: {getattr(px, 'shape', '?')}")
        except Exception:
            pass

    # 4. Look at ALL attrs of afbbgvkpip.xmdjbwrpmv recursively
    print("\n=== Walk afbbgvkpip.xmdjbwrpmv deeply ===")
    for name in sorted(dir(inner)):
        if name.startswith('_'):
            continue
        try:
            v = getattr(inner, name)
        except Exception:
            continue
        if callable(v):
            continue
        if not isinstance(v, (int, float, bool, str, list, tuple, type(None))):
            print(f"  {name}: {type(v).__name__}")
            # Go one level deeper
            if hasattr(v, '__dict__') or hasattr(v, '__slots__'):
                for sub in sorted(dir(v)):
                    if sub.startswith('_'):
                        continue
                    try:
                        sv = getattr(v, sub)
                    except Exception:
                        continue
                    if callable(sv):
                        continue
                    if isinstance(sv, (int, float, bool, str)):
                        print(f"    .{sub} = {sv!r}")

    # 5. Try dumping the PLAYER sprite's xmdjbwrpmv
    p = g.vgwycxsxjz.dzxunlkwxt
    if hasattr(p, 'xmdjbwrpmv'):
        dump_sprite(p.xmdjbwrpmv, "player.xmdjbwrpmv")

    # 6. Hmm the level has grid_size — what is it?
    try:
        print(f"\ngrid_size[0]={lvl.grid_size[0]} [1]={lvl.grid_size[1]}")
    except Exception as e:
        print(f"grid_size access error: {e}")

    # 7. The game has a perform_action that does collision checks.
    # Let's find the method and its source file — is the player allowed into pixel-walkable cells?
    # Check player.current_level or .game refs
    print(f"\nPlayer current_level: {getattr(p, 'current_level', None)}")


if __name__ == "__main__":
    main()
