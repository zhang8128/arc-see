"""G50T: inspect collision modes of each entity and understand the win condition."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def sprite_summary(s, tag):
    inner = getattr(s, 'xmdjbwrpmv', None)
    if inner is None:
        return
    print(f"  {tag} @ ({s.x}, {s.y}):")
    for attr in ['is_collidable', 'is_visible', 'layer', 'interaction',
                 'blocking', 'scale', 'rotation', 'name']:
        try:
            v = getattr(inner, attr, None)
            if hasattr(v, 'name'):  # enum
                v = f"{v.name}({v.value})"
            print(f"    {attr}: {v}")
        except Exception as e:
            print(f"    {attr}: ERR {e}")
    # Tags
    try:
        print(f"    tags: {list(inner.tags)}")
    except Exception:
        pass


def main():
    g = mod.G50t()
    g.set_level(0)
    eng = g.vgwycxsxjz

    print("=== L1 sprite collision summary ===")
    sprite_summary(eng.dzxunlkwxt, "player")
    sprite_summary(eng.whftgckbcu, "goal")
    sprite_summary(eng.afbbgvkpip, "maze_layer")
    for i, e in enumerate(eng.hamayflsib):
        sprite_summary(e, f"hamayflsib[{i}]")
    for i, e in enumerate(eng.uwxkstolmf):
        sprite_summary(e, f"uwxkstolmf[{i}]")
    for i, e in enumerate(eng.drofvwhbxb):
        sprite_summary(e, f"drofvwhbxb[{i}]")
    if eng.zmqoxwsfgh:
        sprite_summary(eng.zmqoxwsfgh, "zmqoxwsfgh")

    # Is there any get_sprites_by_tag on current_level that works?
    lvl = g.current_level
    print("\n=== Level tag search (all known tags) ===")
    for tag in ['rsrdfsruqh', 'qftsebtxuc', 'lqtxaumfed', 'yyzqramdhd', 'fdukwsxcoo']:
        try:
            sprites = lvl.get_sprites_by_tag(tag)
            print(f"  {tag}: {len(sprites)} sprites")
            for s in sprites:
                print(f"    at ({s.x}, {s.y}) type {type(s).__name__}")
        except Exception as e:
            print(f"  {tag}: ERR {e}")

    # Let's see if the LEVEL has any sprite list
    print("\n=== Level.__dict__ or dir ===")
    for name in sorted(dir(lvl)):
        if name.startswith('_'):
            continue
        try:
            v = getattr(lvl, name)
        except Exception:
            continue
        if callable(v):
            continue
        print(f"  {name}: {type(v).__name__}", end='')
        if isinstance(v, (int, float, bool, str)):
            print(f" = {v!r}")
        elif isinstance(v, (list, tuple)):
            print(f" len={len(v)}")
        else:
            print()

    # Check the maze layer's pixel values at key transitions
    print("\n=== Win condition probe ===")
    # What is the "win" state? Check whftgckbcu is_collidable and interaction
    goal_inner = eng.whftgckbcu.xmdjbwrpmv
    print(f"  goal interaction: {goal_inner.interaction.name}")
    print(f"  goal layer: {goal_inner.layer}")

    # ARC games usually have a "check_win" or similar method
    for name in dir(g):
        if 'win' in name.lower() or 'check' in name.lower():
            print(f"  game.{name}")
    for name in dir(eng):
        if 'win' in name.lower() or 'check' in name.lower():
            print(f"  eng.{name}")


if __name__ == "__main__":
    main()
