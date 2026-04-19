"""G50T: dump the alyzsfkumg relay entity — where is it, what does it do?"""
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
    eng = g.vgwycxsxjz

    relay = eng.hamayflsib[0].nexhtmlmxh
    print(f"relay: {type(relay).__name__} at ({relay.x}, {relay.y})")
    print(f"  size: {relay.width}x{relay.height}")
    print(f"  is_visible: {relay.is_visible}")
    print(f"  dijhfchobv: {relay.dijhfchobv}")
    print(f"  ytztewxdin: {len(relay.ytztewxdin)} outputs")
    for out in relay.ytztewxdin:
        print(f"    -> {type(out).__name__} at ({out.x}, {out.y})")

    # Its sprite data
    inner = relay.xmdjbwrpmv
    px = inner.pixels
    print(f"\n  pixels shape: {px.shape}")
    print(f"  layer: {inner.layer}")
    print(f"  is_collidable: {inner.is_collidable}")
    print(f"  tags: {list(inner.tags)}")
    print(f"  pixel dump:")
    for row in px:
        s = ''
        for v in row:
            v = int(v)
            if v < 0:
                s += '-'
            elif v < 16:
                s += f'{v:x}'
            else:
                s += '?'
        print(f"    {s}")

    # Positioned at (16, 10) — is this INSIDE the maze where the player walks?
    print(f"\n  Global position: ({relay.x}, {relay.y})")
    print(f"  Size: {relay.width}x{relay.height}")
    print(f"  Right/bottom: ({relay.x + relay.width}, {relay.y + relay.height})")

    # Player starts at (13, 7) with 7x7 box from (13, 7) to (20, 14)
    # Player center = (16, 10) — EXACTLY where the relay is!
    # Check if the relay's pixel data at player center is non-transparent
    print(f"\n  Player starting center: (16, 10)")
    lx = 16 - relay.x
    ly = 10 - relay.y
    print(f"  Relay local coord of player center: ({lx}, {ly})")
    if 0 <= lx < relay.width and 0 <= ly < relay.height:
        print(f"  Relay pixel at player center: {int(px[ly, lx])}")

    # Does the player overlap the relay? Use yywhlgibxj
    p = eng.dzxunlkwxt
    print(f"\n  player.yywhlgibxj(relay): {p.yywhlgibxj(relay)}")
    # And esidlbhbhw
    print(f"  relay.esidlbhbhw(player.hziczfhrxn, player.prtgxvhmth) = "
          f"{relay.esidlbhbhw(p.hziczfhrxn, p.prtgxvhmth)}")

    # Non-start positions
    print("\n  relay's non-transparent area covers these pixel coordinates:")
    coords = []
    for ry in range(px.shape[0]):
        for rx in range(px.shape[1]):
            if int(px[ry, rx]) >= 0:
                coords.append((relay.x + rx, relay.y + ry))
    if len(coords) <= 80:
        print(f"    {coords}")
    else:
        print(f"    {len(coords)} cells: first 20: {coords[:20]}")
        print(f"    bounding box: x in [{min(c[0] for c in coords)}, {max(c[0] for c in coords)}], "
              f"y in [{min(c[1] for c in coords)}, {max(c[1] for c in coords)}]")


if __name__ == "__main__":
    main()
