"""G50T: probe win condition by directly placing the player at/near the goal."""
import copy
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def status(g, tag=""):
    eng = g.vgwycxsxjz
    p = eng.dzxunlkwxt
    print(f"  [{tag}] player=({p.x},{p.y}) state={g._state.name} "
          f"level_idx={g._current_level_index} win={getattr(g, 'win', None)} "
          f"win_score={getattr(g, 'win_score', None)}")


def set_player(g, x, y):
    p = g.vgwycxsxjz.dzxunlkwxt
    # Try direct assignment
    try:
        p.x = x
        p.y = y
        # Also set the backup fields
        p.xjzbfpegay = x
        p.yzwsikkoyp = y
        p.hziczfhrxn = x + p.width // 2
        p.prtgxvhmth = y + p.height // 2
        p.ojhzjvutrg = y
        p.cebscfuvab = x
    except Exception as e:
        print(f"  set_player error: {e}")


def main():
    g = mod.G50t()
    g.set_level(0)
    status(g, "start")
    print(f"  game.win_score = {g.win_score}")

    # Try placing the player directly on the goal
    g2 = copy.deepcopy(g)
    set_player(g2, 42, 48)
    status(g2, "manually placed at goal (42,48) BEFORE step")

    # Now perform an action to trigger any win check
    try:
        g2.perform_action(ActionInput(id=GameAction.ACTION5))
        # ACTION5 resets — probably not what we want
    except Exception as e:
        print(f"  ACTION5 error: {e}")
    status(g2, "after ACTION5")

    # Let's try stepping into position via natural move
    g3 = copy.deepcopy(g)
    set_player(g3, 43, 43)  # grid-aligned near goal
    status(g3, "manually placed at (43,43)")
    g3.perform_action(ActionInput(id=GameAction.ACTION2))  # try down
    status(g3, "+1D")

    # Try right from (43, 43)
    g4 = copy.deepcopy(g)
    set_player(g4, 43, 43)
    g4.perform_action(ActionInput(id=GameAction.ACTION4))
    status(g4, "placed (43,43) +1R")

    # Look for how win is checked — look at game.win_score vs current score
    print(f"\n  game attrs:")
    for name in ['win', 'win_score', '_win_score', 'score', '_score']:
        if hasattr(g, name):
            print(f"    g.{name} = {getattr(g, name)}")

    # Try placing player such that collision box touches goal
    print("\n=== Testing various player positions near goal ===")
    for pos in [(36, 42), (37, 42), (43, 42), (37, 48), (42, 48), (43, 48),
                (36, 43), (37, 43), (43, 43), (37, 49), (42, 49), (43, 49),
                (19, 49), (25, 49), (31, 49), (43, 49), (49, 49)]:
        g_test = copy.deepcopy(g)
        set_player(g_test, *pos)
        # No action, just check state
        print(f"  placed at {pos}: state={g_test._state.name} "
              f"level_idx={g_test._current_level_index}")


if __name__ == "__main__":
    main()
