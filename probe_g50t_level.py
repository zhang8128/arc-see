"""G50T: deep inspection of current_level and afbbgvkpip to find hidden walls/sprites."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def dump_attrs(obj, tag, skip=()):
    print(f"\n=== {tag} ({type(obj).__name__}) ===")
    for name in sorted(dir(obj)):
        if name.startswith('_') or name in skip:
            continue
        try:
            v = getattr(obj, name)
        except Exception as e:
            print(f"  {name}: ERR {e}")
            continue
        if callable(v):
            continue
        if isinstance(v, (int, float, bool, str)):
            print(f"  {name}: {v!r}")
        elif isinstance(v, (list, tuple)):
            print(f"  {name}: {type(v).__name__} len={len(v)}")
            if len(v) <= 30:
                for i, item in enumerate(v):
                    print(f"    [{i}] {type(item).__name__} "
                          f"x={getattr(item, 'x', '?')} "
                          f"y={getattr(item, 'y', '?')}")
        elif v is None:
            print(f"  {name}: None")
        else:
            print(f"  {name}: <{type(v).__name__}>")


def main():
    g = mod.G50t()
    g.set_level(0)

    lvl = g.current_level
    dump_attrs(lvl, 'current_level', skip=('game',))

    # Any get_sprites_by_tag method?
    if hasattr(lvl, 'get_sprites_by_tag'):
        print("\n=== get_sprites_by_tag probes ===")
        for tag in ['wall', 'walls', 'door', 'trigger', 'goal', 'player',
                    'tile', 'map', 'maze', 'obstacle', 'enemy', 'key',
                    'item', 'collectible', 'spawn', 'entity']:
            try:
                sprites = lvl.get_sprites_by_tag(tag)
                if sprites:
                    print(f"  tag '{tag}': {len(sprites)} sprites")
                    for s in sprites[:5]:
                        print(f"    {type(s).__name__} x={s.x} y={s.y}")
            except Exception as e:
                pass

    # Also inspect the afbbgvkpip maze-layer sprite
    afb = g.vgwycxsxjz.afbbgvkpip
    dump_attrs(afb, 'afbbgvkpip (maze layer?)', skip=('current_level',))


if __name__ == "__main__":
    main()
