"""G50T: use _get_valid_actions to find context-dependent actions."""
import copy
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def act(g, name):
    g.perform_action(ActionInput(id=getattr(GameAction, name)))


def main():
    g = mod.G50t()
    g.set_level(0)
    p = g.vgwycxsxjz.dzxunlkwxt

    # Start
    try:
        v = g._get_valid_actions()
        print(f"start ({p.x},{p.y}): _get_valid_actions() = {v}")
    except Exception as e:
        print(f"start: ERR {e}")

    # Walk right 4, check at each step
    paths = [
        [],
        ['ACTION4'],
        ['ACTION4', 'ACTION4'],
        ['ACTION4', 'ACTION4', 'ACTION4'],
        ['ACTION4', 'ACTION4', 'ACTION4', 'ACTION4'],  # at (37,7) trigger
        ['ACTION2'],
        ['ACTION2', 'ACTION2'],
        ['ACTION2', 'ACTION2', 'ACTION2'],
        ['ACTION2', 'ACTION2', 'ACTION2', 'ACTION2'],
    ]
    for path in paths:
        g2 = copy.deepcopy(g)
        for a in path:
            act(g2, a)
        p2 = g2.vgwycxsxjz.dzxunlkwxt
        try:
            v = g2._get_valid_actions()
            print(f"  after {path}: pos=({p2.x},{p2.y}) valid={v}")
        except Exception as e:
            print(f"  after {path}: ERR {e}")

    # Try clickable/placeable
    print("\n=== _get_valid_clickable_actions ===")
    try:
        v = g._get_valid_clickable_actions()
        print(f"  {v}")
    except Exception as e:
        print(f"  ERR {e}")

    print("\n=== _get_valid_placeble_actions ===")
    try:
        v = g._get_valid_placeble_actions()
        print(f"  {v}")
    except Exception as e:
        print(f"  ERR {e}")

    # Maybe there are "action data" versions of actions that take extra params.
    # Look at what ActionInput expects and what the game does with data.
    print("\n=== ActionInput introspection ===")
    ai = ActionInput(id=GameAction.ACTION1)
    for name in dir(ai):
        if name.startswith('_'):
            continue
        v = getattr(ai, name)
        if not callable(v):
            print(f"  {name}: {v!r}")


if __name__ == "__main__":
    main()
