"""R11L: watch score with different click patterns."""
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


def click(g, x, y):
    g.perform_action(ActionInput(id=GameAction.ACTION6, data={'x': x, 'y': y}))


def snap(g):
    return (g._state.name, g.zxankdpxcx,
            (g.ftmaz[0].x, g.ftmaz[0].y),
            (g.ftmaz[1].x, g.ftmaz[1].y),
            g.winning, g.gfwuu, g.tfhng, g.tjffy, g.anzbz,
            g.zmxct.get('kpaac'))


def main():
    # Walk attempts — try to progress through the level systematically
    # Start: leg0=(5,34), leg1=(25,57)
    # Level bg at (-5,-6) size 73x78 so world is roughly [-5,68] x [-6,72]

    print("--- Step through a sequence of random clicks ---")
    g = fresh()
    print(f"start: {snap(g)}")
    moves = [
        (15, 15), (20, 20), (30, 30), (40, 40), (50, 50), (60, 60), (65, 65),
    ]
    for m in moves:
        click(g, *m)
        print(f"click{m}: {snap(g)}")

    # Try alternating between clicking leg positions and targets
    print("\n--- Alternating select + move (simulate walking) ---")
    g = fresh()
    print(f"start: {snap(g)}")
    # Step 1: click leg 1 to select it, click far right to advance
    click(g, 25, 57)
    print(f"sel leg1: {snap(g)}")
    click(g, 50, 50)
    print(f"move (50,50): {snap(g)}")

    # Try: make leg0 stay, advance leg1 toward corner
    g = fresh()
    for tx, ty in [(10, 40), (15, 45), (20, 50), (25, 55), (30, 60), (35, 65), (40, 70)]:
        click(g, tx, ty)
        s = snap(g)
        print(f"  click({tx},{ty}): state={s[0]} score={s[1]} ft0={s[2]} ft1={s[3]} winning={s[4]}")
        if s[0] == "WIN" or s[4]:
            print("  WIN!")
            break


if __name__ == "__main__":
    main()
