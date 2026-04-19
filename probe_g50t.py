"""G50T probe — discover mechanics and find a hashable internal state key.

Approach (from project_g50t_prep.md):
1. Try each action once on L1, observe what changed.
2. Deepcopy + step to find which attributes actually change.
3. Build state_key(g) tuple of the changing fields for BFS dedup.
"""
import copy
import importlib.util
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTIONS = [GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3,
           GameAction.ACTION4, GameAction.ACTION5]


def pixels_sig(g):
    """Hash of rendered pixels — what the MCP lens sees."""
    try:
        p = g.get_pixels()
        return hash(tuple(tuple(row) for row in p))
    except Exception as e:
        return f"err:{e}"


def walk_attrs(obj, prefix='', depth=0, max_depth=3, seen=None):
    """Yield (path, value_repr) for leaf attributes."""
    if seen is None:
        seen = set()
    if id(obj) in seen or depth > max_depth:
        return
    seen.add(id(obj))
    for name in sorted(dir(obj)):
        if name.startswith('_') or name in ('get_pixels', 'perform_action'):
            continue
        try:
            val = getattr(obj, name)
        except Exception:
            continue
        if callable(val):
            continue
        path = f"{prefix}.{name}" if prefix else name
        # Skip massive collections
        if isinstance(val, (list, tuple)):
            yield path, f"<{type(val).__name__} len={len(val)}>"
            if len(val) <= 20:
                for i, item in enumerate(val):
                    if hasattr(item, '__dict__'):
                        yield from walk_attrs(item, f"{path}[{i}]", depth + 1, max_depth, seen)
        elif isinstance(val, (int, float, bool, str, type(None))):
            yield path, repr(val)
        elif hasattr(val, '__dict__'):
            yield path, f"<{type(val).__name__}>"
            yield from walk_attrs(val, path, depth + 1, max_depth, seen)


def snapshot(g):
    """Return a dict of path -> value for all leaf attrs we can see."""
    return dict(walk_attrs(g, max_depth=4))


def diff_snapshots(before, after):
    changed = {}
    for k, v in after.items():
        if before.get(k) != v:
            changed[k] = (before.get(k), v)
    # Also detect removals
    for k in before:
        if k not in after:
            changed[k] = (before[k], None)
    return changed


def try_action(g, action_name):
    before_pix = pixels_sig(g)
    before_snap = snapshot(g)
    g.perform_action(ActionInput(id=getattr(GameAction, action_name)))
    after_pix = pixels_sig(g)
    after_snap = snapshot(g)
    diff = diff_snapshots(before_snap, after_snap)
    return {
        'pixels_changed': before_pix != after_pix,
        'attrs_changed': len(diff),
        'diff': diff,
        'state': g._state.name,
        'level_idx': g._current_level_index,
    }


def probe_l1():
    print("=== G50T L1 probe ===\n")
    g = mod.G50t()
    g.set_level(0)
    print(f"Initial state: {g._state.name}, level_idx={g._current_level_index}")
    print(f"Initial pixels hash: {pixels_sig(g)}")

    # Baseline snapshot
    init_snap = snapshot(g)
    print(f"Initial attrs visible: {len(init_snap)}")
    print("\nSample top-level attrs:")
    for k, v in sorted(init_snap.items())[:30]:
        if '.' not in k:  # only top-level
            print(f"  {k} = {v}")

    # Try each action from a fresh deepcopy
    print("\n=== Action probes (each from fresh state) ===")
    for a in ['ACTION1', 'ACTION2', 'ACTION3', 'ACTION4', 'ACTION5']:
        g2 = copy.deepcopy(g)
        try:
            result = try_action(g2, a)
            print(f"\n{a}: pixels_changed={result['pixels_changed']} "
                  f"attrs_changed={result['attrs_changed']} "
                  f"state={result['state']} level={result['level_idx']}")
            # Show first few diffs
            for k, (b, a_val) in list(result['diff'].items())[:8]:
                print(f"    {k}: {b!r} -> {a_val!r}")
        except Exception as e:
            print(f"\n{a}: ERROR {type(e).__name__}: {e}")


if __name__ == "__main__":
    probe_l1()
