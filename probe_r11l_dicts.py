"""R11L: dive into brdck/dfugm/zmxct for character state."""
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


def show_dict(label, d):
    print(f"\n{label}:")
    for k, v in d.items():
        print(f"  [{k}]: {type(v).__name__}")
        if isinstance(v, dict):
            for k2, v2 in v.items():
                if hasattr(v2, 'x'):
                    print(f"      [{k2}]: {type(v2).__name__} at ({v2.x},{v2.y})")
                else:
                    print(f"      [{k2}]: {v2!r}")
        elif hasattr(v, 'x'):
            print(f"      at ({v.x}, {v.y})")
        else:
            print(f"      value: {v!r}")


def main():
    g = fresh()
    print(f"Initial player: mjdkn=({g.mjdkn.x},{g.mjdkn.y})")
    show_dict("brdck", g.brdck)
    show_dict("dfugm", g.dfugm)
    show_dict("zmxct", g.zmxct)
    print(f"\nmkugn: {g.mkugn}")
    print(f"whfmv: {g.whfmv}")

    # After a click somewhere
    print("\n=== After click at (20, 20) ===")
    g2 = fresh()
    g2.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': 20, 'y': 20}))
    print(f"mjdkn: ({g2.mjdkn.x},{g2.mjdkn.y})")
    show_dict("brdck", g2.brdck)
    show_dict("zmxct", g2.zmxct)
    print(f"ftmaz[0]: ({g2.ftmaz[0].x},{g2.ftmaz[0].y})")
    print(f"ftmaz[1]: ({g2.ftmaz[1].x},{g2.ftmaz[1].y})")

    # After click on ftmaz[1] position (25, 57)
    print("\n=== After click on (25, 57) (ftmaz[1]'s spot) ===")
    g3 = fresh()
    g3.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': 25, 'y': 57}))
    print(f"mjdkn: ({g3.mjdkn.x},{g3.mjdkn.y})")
    print(f"ftmaz[0]: ({g3.ftmaz[0].x},{g3.ftmaz[0].y})")
    print(f"ftmaz[1]: ({g3.ftmaz[1].x},{g3.ftmaz[1].y})")

    # Click 2x
    print("\n=== Click sequence: (25, 57) then (30, 30) ===")
    g4 = fresh()
    g4.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': 25, 'y': 57}))
    print(f"after 1st: mjdkn=({g4.mjdkn.x},{g4.mjdkn.y}) ftmaz[0]=({g4.ftmaz[0].x},{g4.ftmaz[0].y}) ftmaz[1]=({g4.ftmaz[1].x},{g4.ftmaz[1].y})")
    g4.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': 30, 'y': 30}))
    print(f"after 2nd: mjdkn=({g4.mjdkn.x},{g4.mjdkn.y}) ftmaz[0]=({g4.ftmaz[0].x},{g4.ftmaz[0].y}) ftmaz[1]=({g4.ftmaz[1].x},{g4.ftmaz[1].y})")
    print(f"  winning: {g4.winning} state: {g4._state.name}")


if __name__ == "__main__":
    main()
