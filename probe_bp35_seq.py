"""BP35: sequence exploration — find how to win L1."""
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'bp35', 'environment_files/bp35/0a0ad940/bp35.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def fresh(level=0):
    g = mod.Bp35()
    g.set_level(level)
    return g


def do(g, name, **kw):
    aid = getattr(GameAction, name)
    ai = ActionInput(id=aid, **kw)
    g.perform_action(ai)


def status(g):
    eng = g.oztjzzyqoek
    p = eng.twdpowducb
    return (g._state.name, g.hbqwwgceeqp, (p.x, p.y), g._current_level_index)


def main():
    # Try a long sequence of LR to see if score changes
    g = fresh(0)
    print(f"Start: {status(g)}")
    for i in range(20):
        do(g, 'ACTION3')
        print(f"  L{i+1}: {status(g)}")
        if g._state.name == "WIN":
            break

    # Reset, try ACTION7
    print("\n--- ACTION7 spam ---")
    g = fresh(0)
    for i in range(5):
        do(g, 'ACTION7')
        print(f"  L{i+1}: {status(g)}")

    # Try alternating
    print("\n--- Alternating L R U ---")
    g = fresh(0)
    for i, a in enumerate(['ACTION3', 'ACTION4', 'ACTION7'] * 5):
        do(g, a)
        print(f"  L{i+1} {a}: {status(g)}")

    # Check engine entity list
    print("\n=== Engine entity list inspection ===")
    g = fresh(0)
    eng = g.oztjzzyqoek
    print(f"uzkgdtbjsr: {eng.uzkgdtbjsr}")
    print(f"zdfflsbctnz: {eng.zdfflsbctnz}")
    print(f"kiopdubfvza dict keys sample: {list(eng.kiopdubfvza.keys())[:5]}")
    print(f"kiopdubfvza size: {len(eng.kiopdubfvza)}")

    # Look at pevrvnrfxnw and camera
    print(f"camera: x={eng.camera.x}, y={eng.camera.y}")
    print(f"pevrvnrfxnw: x={eng.pevrvnrfxnw.x}, y={eng.pevrvnrfxnw.y}")
    print(f"height: {eng.height}, width: {eng.width}")

    # Look at the game tile/sprite map
    print(f"pjdcytzsmft shape: {eng.pjdcytzsmft.shape}")


if __name__ == "__main__":
    main()
