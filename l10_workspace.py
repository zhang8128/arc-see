"""L10 workspace — fresh game at L10 init + optional sim snapshot.

Usage:
    from l10_workspace import make_l10_game, l10_sim
    g = make_l10_game()          # real engine at L10 init
    s = l10_sim()                # pure-Python sim at L10 init

Both are ready to test L10 hypotheses. Playing to L10 takes ~1.4s;
thereafter use deepcopy snapshots to reset without replay.
"""
import sys
sys.path.insert(0, '/Users/kairos/Projects/arc-see')
import copy
from lf52_play_to_l10 import play_to_l10

_cached_snapshot = None


def make_l10_game(use_cache=True):
    """Return a live LF52 game at L10 init. Cached snapshot avoids L1-L9 replay."""
    global _cached_snapshot
    if use_cache and _cached_snapshot is not None:
        g, snap = _cached_snapshot
        g.env._game = copy.deepcopy(snap)
        g.obs = None
        g._cached_frame = None
        return g
    g = play_to_l10(verbose=False)
    _cached_snapshot = (g, copy.deepcopy(g.env._game))
    return g


def l10_sim():
    """Return a pure-Python Sim at L10 init. For fast hypothesis testing."""
    from l7_sim import load_init
    return load_init('/tmp/l10_init.json')


if __name__ == '__main__':
    import time
    t = time.time()
    g = make_l10_game()
    print(f'L10 game ready in {time.time()-t:.2f}s')
    # Reset test
    t = time.time()
    g = make_l10_game(use_cache=True)
    print(f'Reset via cache in {time.time()-t:.3f}s')
    # Sim test
    t = time.time()
    s = l10_sim()
    print(f'L10 sim ready in {time.time()-t:.3f}s — pieces: {s.pieces}')
