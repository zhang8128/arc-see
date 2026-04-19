"""G50T L1: dump the hamay output wiring (nexhtmlmxh, ytztewxdin)."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def describe(obj, prefix=''):
    t = type(obj).__name__
    x = getattr(obj, 'x', '?')
    y = getattr(obj, 'y', '?')
    return f"{prefix}{t}@({x},{y})"


def main():
    g = mod.G50t()
    g.set_level(0)
    eng = g.vgwycxsxjz

    print(f"hamayflsib count: {len(eng.hamayflsib)}")
    for i, h in enumerate(eng.hamayflsib):
        print(f"\n[{i}] {describe(h)}")
        # Try to find output attrs
        for name in ['nexhtmlmxh', 'ytztewxdin', 'vbqvjbxkfm', 'dijhfchobv']:
            try:
                v = getattr(h, name)
                if isinstance(v, list):
                    print(f"    {name}: list len={len(v)}")
                    for item in v:
                        print(f"      -> {describe(item)}")
                elif isinstance(v, set):
                    print(f"    {name}: set len={len(v)}")
                elif v is None:
                    print(f"    {name}: None")
                elif hasattr(v, 'x'):
                    print(f"    {name}: {describe(v)}")
                    # Recurse into its output
                    for sub in ['nexhtmlmxh', 'ytztewxdin', 'dijhfchobv']:
                        try:
                            sv = getattr(v, sub)
                            if isinstance(sv, list):
                                print(f"        .{sub}: list len={len(sv)}")
                                for item in sv:
                                    print(f"          -> {describe(item)}")
                            elif hasattr(sv, 'x'):
                                print(f"        .{sub}: {describe(sv)}")
                            else:
                                print(f"        .{sub}: {sv}")
                        except Exception:
                            pass
                else:
                    print(f"    {name}: {v}")
            except Exception as e:
                pass

    print(f"\nuwxkstolmf count: {len(eng.uwxkstolmf)}")
    for i, u in enumerate(eng.uwxkstolmf):
        print(f"[{i}] {describe(u)}")
        for name in ['dijhfchobv', 'dpdubazedr', 'lzwacefckd', 'rotation',
                     'xjzbfpegay', 'yzwsikkoyp', 'ecvzipvalj', 'flzkzvlsvl']:
            try:
                v = getattr(u, name)
                print(f"    {name}: {v}")
            except Exception:
                pass


if __name__ == "__main__":
    main()
