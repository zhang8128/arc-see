"""L7 interactive harness with checkpoint caching.

Provides L7Harness class that:
1. Lazily sets up a game at chain-8 state (cached via deepcopy)
2. Allows interactive exploration without re-running setup each time
3. Saves/restores state within one Python session

Use:
    from l7_harness import L7Harness
    h = L7Harness()
    h.restore_to('chain8')    # restores cached state
    h.action(4)               # or h.click(x, y)
    pix = h.pixels()
    h.save('chain9_attempt')  # save current state
    h.restore_to('chain9_attempt')
    h.render('/tmp/foo.png')
    # fast scan
    hits = h.scan_reactive(x_range=(0,64), y_range=(50,64), skip_counter=True)
"""
import copy
import numpy as np
from lf52_tool import LF52, render_png
from l7_play import find_vehicle


CHAINS = {
    'chain1': {  # load tan
        'actions': [3, 3, 1, 1, 3, 3, 3],
        'clicks': [(6, 12), (6, 24)],
    },
    'chain2': {  # deliver tan → slot 1
        'actions': [4, 4, 4, 2, 2, 3, 3, 2],
        'clicks': [(13, 44), (13, 55)],
    },
    'load_lb': {  # drive + load lightblue
        'actions': [1, 4, 4, 1, 1, 4, 4, 4],
        'clicks': [(42, 12), (42, 24)],
    },
    'deliver_lb': {  # deliver lb → slot 6
        'actions': [3, 3, 3, 2, 2, 4, 4, 4, 2],
        'clicks': [(43, 44), (43, 55)],
    },
    'return_to_left': {  # drive back to (10, 41)
        'actions': [1, 3, 3, 3, 1, 1, 3, 3, 3, 4, 4, 4, 2, 2, 3, 3, 3, 2],
        'clicks': [],
    },
    'chain3': {'actions': [], 'clicks': [(13, 55), (25, 55)]},  # tan 1→3
    'chain4': {'actions': [], 'clicks': [(25, 55), (37, 55)]},  # tan 3→5
    'chain5': {'actions': [], 'clicks': [(37, 55), (47, 55)]},  # tan 5→7
    'chain6': {'actions': [], 'clicks': [(43, 55), (55, 55)]},  # lb 6→8 — SCROLLS
    'chain7': {'actions': [], 'clicks': [(5, 55), (17, 55)]},   # post-scroll tan fwd
    'chain8': {  # drive to (20,53), chain lb into vehicle
        'actions': [2, 3, 2, 2, 4, 4, 2],
        'clicks': [(11, 55), (23, 55)],
    },
    'chain9': {  # tan (9,8) → (11,8) via LB pivot at (10,8)
        'actions': [],
        'clicks': [(15, 55), (29, 55)],
    },
}

# Order to apply chains in
CHAIN_ORDER = ['chain1', 'chain2', 'load_lb', 'deliver_lb', 'return_to_left',
               'chain3', 'chain4', 'chain5', 'chain6', 'chain7', 'chain8', 'chain9']


class L7Harness:
    def __init__(self, verbose=False):
        self._base = LF52(up_to_level=7, verbose=verbose)
        self._snaps = {}  # name → deepcopy of env._game
        self._snaps['l7_start'] = copy.deepcopy(self._base.env._game)
        self._current = 'l7_start'

    def _apply_step(self, step):
        for a in step['actions']:
            self._base.action(a)
        for x, y in step['clicks']:
            self._base.click(x, y)

    def _ensure_chain(self, target):
        """Build up to named chain checkpoint, caching intermediate states."""
        if target in self._snaps:
            return
        # Restore from nearest prior snapshot
        idx = CHAIN_ORDER.index(target)
        for i in range(idx, -1, -1):
            name = CHAIN_ORDER[i]
            if name in self._snaps:
                self._base.env._game = copy.deepcopy(self._snaps[name])
                self._base.obs = None
                self._base._cached_frame = None
                self._current = name
                break
        else:
            self._base.env._game = copy.deepcopy(self._snaps['l7_start'])
            self._base.obs = None
            self._base._cached_frame = None
        # Apply chains from current position to target
        start_idx = CHAIN_ORDER.index(self._current) + 1 if self._current != 'l7_start' else 0
        for j in range(start_idx, idx + 1):
            name = CHAIN_ORDER[j]
            self._apply_step(CHAINS[name])
            self._snaps[name] = copy.deepcopy(self._base.env._game)
        self._current = target

    def restore_to(self, name):
        """Restore to a saved state (chain checkpoint or user-saved)."""
        if name in CHAIN_ORDER or name == 'l7_start':
            if name != 'l7_start':
                self._ensure_chain(name)
            self._base.env._game = copy.deepcopy(self._snaps[name])
            self._base.obs = None
            self._base._cached_frame = None
            self._current = name
        elif name in self._snaps:
            self._base.env._game = copy.deepcopy(self._snaps[name])
            self._base.obs = None
            self._base._cached_frame = None
            self._current = name
        else:
            raise KeyError(f'No snap named {name}')
        return self

    def save(self, name):
        """Save current state under given name."""
        self._snaps[name] = copy.deepcopy(self._base.env._game)
        return self

    def action(self, a):
        self._base.action(a)
        return self

    def click(self, x, y):
        self._base.click(x, y)
        return self

    def pixels(self):
        return self._base.pixels()

    def level(self):
        return self._base.level()

    def state_name(self):
        return self._base.state_name()

    def vehicle(self):
        return find_vehicle(self.pixels())

    def vp(self):
        return tuple(self._base.env._game.ikhhdzfmarl.hncnfaqaddg.cdpcbbnfdp)

    def render(self, path, label=''):
        render_png(self.pixels(), label=label).save(path)
        return path

    def scan_reactive(self, x_range=(0, 64), y_range=(0, 64), step=1, exclude_diffs=(29,)):
        """Scan all click positions, return (x, y, diff) for reactive ones.

        Returns a list of (cx, cy, diff) tuples for clicks that change the frame.
        """
        from arcengine import GameAction
        # Ensure we have a real 64x64 pixel frame by forcing a cheap action
        if self._base.obs is None:
            # Take a no-op click far outside game area to populate obs
            self._base.click(0, 0)
        base = self.pixels().copy()
        if base.shape != (64, 64):
            raise RuntimeError(f'base shape {base.shape} != (64,64)')
        snap = copy.deepcopy(self._base.env._game)
        hits = []
        for cy in range(y_range[0], y_range[1], step):
            for cx in range(x_range[0], x_range[1], step):
                self._base.env._game = copy.deepcopy(snap)
                obs = self._base.env.step(GameAction.ACTION6, data={'x': cx, 'y': cy})
                new = np.array(obs.frame[-1], dtype=np.int64)
                diff = (base != new).sum()
                if diff > 5 and diff not in exclude_diffs:
                    hits.append((cx, cy, int(diff)))
        # Restore
        self._base.env._game = copy.deepcopy(snap)
        self._base.obs = None
        self._base._cached_frame = None
        return hits
