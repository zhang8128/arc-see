"""G50T: list all sprites in L1 via current_level.sprites (if accessible)."""
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
    lvl = g.current_level

    # Try various attrs to find the sprite list
    print("=== Level attrs ===")
    for name in sorted(dir(lvl)):
        if name.startswith('_'):
            continue
        try:
            v = getattr(lvl, name)
            if callable(v):
                continue
            print(f"  {name}: {type(v).__name__}", end='')
            if isinstance(v, (list, tuple)):
                print(f" len={len(v)}")
                for i, item in enumerate(v[:20]):
                    print(f"    [{i}] {type(item).__name__} "
                          f"name={getattr(item, 'name', '?')} "
                          f"pos=({getattr(item, 'x', '?')},{getattr(item, 'y', '?')}) "
                          f"tags={list(getattr(item, 'tags', []))}")
            else:
                print(f" = {v}")
        except Exception as e:
            print(f"  {name}: ERR {e}")

    # Dump _sprites with details
    print(f"\n=== lvl._sprites ({len(lvl._sprites)} sprites) ===")
    for i, s in enumerate(lvl._sprites):
        name = getattr(s, 'name', '?')
        x = getattr(s, 'x', '?')
        y = getattr(s, 'y', '?')
        w = getattr(s, 'width', '?')
        h = getattr(s, 'height', '?')
        tags = list(getattr(s, 'tags', []))
        layer = getattr(s, 'layer', '?')
        vis = getattr(s, 'is_visible', '?')
        coll = getattr(s, 'is_collidable', '?')
        print(f"  [{i}] name={name} pos=({x},{y}) size={w}x{h} layer={layer} vis={vis} coll={coll} tags={tags}")


if __name__ == "__main__":
    main()
