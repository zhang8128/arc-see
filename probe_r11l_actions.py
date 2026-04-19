"""R11L: explore what the actions do."""
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


def snap(g):
    return {
        'state': g._state.name,
        'level': g._current_level_index,
        'score': g.zxankdpxcx,
        'winning': g.winning,
        'mjdkn': (g.mjdkn.x, g.mjdkn.y),
        'anzbz': g.anzbz,
        'gfwuu': g.gfwuu,
        'tfhng': g.tfhng,
        'tjffy': g.tjffy,
        'wvopxkipus': g.wvopxkipus,
        'bmtib': g.bmtib,
        'cjcex': g.cjcex,
        'cyaxdmynov': g.cyaxdmynov,
        'xjryq': g.xjryq,
        'whfmv': g.whfmv,
        'mkugn': g.mkugn,
    }


def diff(a, b):
    return {k: (a[k], b[k]) for k in a if a[k] != b[k]}


def main():
    g = fresh()
    base = snap(g)
    print(f"Base: {base}")

    # Try each action
    for aid in range(1, 8):
        try:
            act = getattr(GameAction, f'ACTION{aid}')
        except AttributeError:
            continue
        g = fresh()
        try:
            g.perform_action(ActionInput(id=act))
            s = snap(g)
            d = diff(base, s)
            print(f"\nACTION{aid}: diff={d}")
        except Exception as e:
            print(f"\nACTION{aid}: error {e}")

    # Try ACTION6 click at various positions
    print("\n--- ACTION6 click scan ---")
    base = snap(fresh())
    for x, y in [(8, 8), (16, 16), (32, 32), (48, 48), (24, 24), (0, 0), (20, 40), (40, 20)]:
        g = fresh()
        try:
            g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': x, 'y': y}))
            s = snap(g)
            d = diff(base, s)
            print(f"  click({x},{y}): diff={d}")
        except Exception as e:
            print(f"  click({x},{y}): error {e}")

    # Dump a few structural attrs
    print("\n=== Structural ===")
    g = fresh()
    print(f"brdck keys: {list(g.brdck.keys())[:20]}")
    print(f"dfugm keys: {list(g.dfugm.keys())[:20]}")
    print(f"fwqwj keys: {list(g.fwqwj.keys())[:20]}")
    print(f"zmxct keys: {list(g.zmxct.keys())[:20]}")
    print(f"ftmaz len: {len(g.ftmaz)}")
    print(f"kdabh len: {len(g.kdabh)}")
    print(f"nxahg len: {len(g.nxahg)}")
    print(f"yhfnp len: {len(g.yhfnp)}")


if __name__ == "__main__":
    main()
