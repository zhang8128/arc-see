"""KA59 full solver — replay known + explore/solve unknown levels."""
import sys
import copy
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location('ka59', 'environment_files/ka59/9f096b4a/ka59.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

U = ActionInput(id=GameAction.ACTION1, data={})
D = ActionInput(id=GameAction.ACTION2, data={})
L = ActionInput(id=GameAction.ACTION3, data={})
R = ActionInput(id=GameAction.ACTION4, data={})
ACTION_MAP = {'U': U, 'D': D, 'L': L, 'R': R}
NAME_MAP = {GameAction.ACTION1: 'U', GameAction.ACTION2: 'D',
            GameAction.ACTION3: 'L', GameAction.ACTION4: 'R', GameAction.ACTION6: 'C'}
BASELINES = [39, 175, 86, 47, 21, 132, 326]


def click_action(g, sprite):
    """Create a click action targeting a sprite's center in display coordinates."""
    gx = sprite.x + sprite.width // 2
    gy = sprite.y + sprite.height // 2
    sc, ox, oy = g.camera._calculate_scale_and_offset()
    dx = int(gx * sc + ox)
    dy = int(gy * sc + oy)
    return ActionInput(id=GameAction.ACTION6, data={'x': dx, 'y': dy})


def get_full_state(g):
    """Full state hash including pieces, enemies, selection, and hidden momentum."""
    pieces = g.current_level.get_sprites_by_tag('xlfuqjygey')
    enemies = g.current_level.get_sprites_by_tag('nnckfubbhi')
    sel = g.ascpmvdpwj
    state = []
    for s in sorted(pieces, key=lambda s: s.name):
        is_sel = 1 if s is sel else 0
        state.append(('P', s.x, s.y, is_sel))
    for s in sorted(enemies, key=lambda s: s.name):
        state.append(('E', s.x, s.y))
    # Include zhcrzgpwcp hidden momentum per sprite
    try:
        for s in sorted(pieces, key=lambda s: s.name):
            if hasattr(s, 'zhcrzgpwcp'):
                state.append(('Z', s.name, s.zhcrzgpwcp))
    except:
        pass
    # Include msbtawvatm if exists
    try:
        if hasattr(g, 'msbtawvatm'):
            state.append(('M', g.msbtawvatm))
    except:
        pass
    return tuple(state)


def get_all_actions(g):
    """Get all possible actions: UDLR + click on non-selected pieces."""
    actions = [U, D, L, R]
    pieces = g.current_level.get_sprites_by_tag('xlfuqjygey')
    sel = g.ascpmvdpwj
    for s in pieces:
        if s is not sel:
            actions.append(click_action(g, s))
    return actions


def describe_level(g, level_idx):
    """Print level layout."""
    pieces = g.current_level.get_sprites_by_tag('xlfuqjygey')
    frames = g.current_level.get_sprites_by_tag('rktpmjcpkt')
    enemies = g.current_level.get_sprites_by_tag('nnckfubbhi')
    enemy_frames = g.current_level.get_sprites_by_tag('ucjzrlvfkb')
    sel = g.ascpmvdpwj

    print(f"\n{'='*60}")
    print(f"Level {level_idx+1} (baseline {BASELINES[level_idx]})")
    print(f"{'='*60}")
    print(f"  Pieces ({len(pieces)}):")
    for s in pieces:
        sel_mark = ' [SELECTED]' if s is sel else ''
        print(f"    {s.name}: ({s.x},{s.y}) {s.width}x{s.height}{sel_mark}")
    print(f"  Player frames ({len(frames)}):")
    for s in frames:
        print(f"    {s.name}: ({s.x},{s.y}) {s.width}x{s.height} -> target ({s.x+1},{s.y+1})")
    if enemies:
        print(f"  Enemies ({len(enemies)}):")
        for s in enemies:
            print(f"    {s.name}: ({s.x},{s.y}) {s.width}x{s.height}")
    if enemy_frames:
        print(f"  Enemy frames ({len(enemy_frames)}):")
        for s in enemy_frames:
            print(f"    {s.name}: ({s.x},{s.y}) {s.width}x{s.height} -> target ({s.x+1},{s.y+1})")


def parse_solution(sol_str):
    """Parse a solution string like 'RRRLDDLLL' or 'R R R L D D L L L' into actions."""
    actions = []
    for ch in sol_str.replace(' ', '').replace(',', ''):
        if ch in ACTION_MAP:
            actions.append(ACTION_MAP[ch])
    return actions


def replay_solution(g, level_idx, actions):
    """Replay a sequence of actions. Returns True if level was won."""
    for a in actions:
        g.perform_action(a)
        if g._current_level_index > level_idx:
            return True
    return g._current_level_index > level_idx


def replay_with_clicks(g, level_idx, seq):
    """Replay a sequence that may include click actions.
    Format: list of (action_type, optional_sprite_name) tuples or ActionInput objects.
    """
    for item in seq:
        if isinstance(item, ActionInput):
            g.perform_action(item)
        elif isinstance(item, str) and item in ACTION_MAP:
            g.perform_action(ACTION_MAP[item])
        elif isinstance(item, tuple) and item[0] == 'CLICK':
            sprite_name = item[1]
            for s in g.current_level.get_sprites_by_tag('xlfuqjygey'):
                if s.name == sprite_name:
                    g.perform_action(click_action(g, s))
                    break
        if g._current_level_index > level_idx:
            return True
    return g._current_level_index > level_idx


def bfs_solve(g, level_idx, max_iters=500000, max_depth=None):
    """Deepcopy BFS with full state hash."""
    limit = max_depth or min(BASELINES[level_idx] + 10, 200)
    start_state = get_full_state(g)
    print(f"  BFS: limit={limit}, max_iters={max_iters}")
    print(f"  Start state: {start_state}", flush=True)

    queue = deque()
    queue.append((g, [], 'start'))
    visited = {start_state}
    iters = 0

    while queue:
        cur_g, path, last_name = queue.popleft()
        iters += 1
        if iters % 5000 == 0:
            print(f"  iter={iters} q={len(queue)} d={len(path)} v={len(visited)}", flush=True)
        if iters > max_iters:
            print(f"  Hit max_iters={max_iters} at depth={len(path)}, visited={len(visited)}")
            return None

        if len(path) >= limit:
            continue

        if cur_g._current_level_index > level_idx:
            names = []
            for a in path:
                if a.id == GameAction.ACTION6:
                    names.append(f"C({a.data.get('x')},{a.data.get('y')})")
                else:
                    names.append(NAME_MAP.get(a.id, '?'))
            print(f"  SOLVED! {len(path)} actions ({iters} iters, {len(visited)} states)")
            print(f"  Path: {' '.join(names)}")
            return path

        for action in get_all_actions(cur_g):
            g2 = copy.deepcopy(cur_g)
            g2.perform_action(action)
            state = get_full_state(g2)
            if state not in visited:
                visited.add(state)
                queue.append((g2, path + [action], ''))

    print(f"  No solution (visited {len(visited)}, {iters} iters)")
    return None


# Known solutions (from previous sessions)
KNOWN_SOLUTIONS = {
    # L1: 11 actions BFS optimal
    # R,R,R (push P2 across divider), L, D, L, L, L, CLICK_P2, U, R
    # But we need click coords... let's use deepcopy BFS for L1 too if fast enough
}


def solve_all():
    """Attempt to solve all 7 levels."""
    g = mod.Ka59()
    total_actions = 0

    for level_idx in range(7):
        g.set_level(level_idx)
        describe_level(g, level_idx)

        # Try BFS for each level
        print(f"\n  Attempting BFS solve...")
        result = bfs_solve(g, level_idx, max_iters=200000,
                          max_depth=min(BASELINES[level_idx], 60))

        if result:
            # Replay on fresh game to advance
            g.set_level(level_idx)
            for a in result:
                g.perform_action(a)
            total_actions += len(result)
            print(f"  Level {level_idx+1} COMPLETE! ({len(result)} actions, baseline {BASELINES[level_idx]})")
        else:
            print(f"  Level {level_idx+1} UNSOLVED — need manual play or better solver")
            print(f"  Total so far: {total_actions} actions")
            return level_idx

    print(f"\n{'='*60}")
    print(f"ALL LEVELS SOLVED! Total: {total_actions} actions")
    print(f"Baseline total: {sum(BASELINES)}")
    return 7


def explore_level(level_idx):
    """Just explore a specific level - print layout and try BFS."""
    g = mod.Ka59()
    g.set_level(level_idx)
    describe_level(g, level_idx)

    # Also check for hidden state attributes
    pieces = g.current_level.get_sprites_by_tag('xlfuqjygey')
    for s in pieces:
        attrs = [a for a in dir(s) if not a.startswith('_') and a not in
                 ('x','y','width','height','name','visible','collidable','tags','layer','pixels','rotation')]
        if attrs:
            print(f"    Extra attrs on {s.name}: {attrs}")
            for a in attrs:
                try:
                    print(f"      {a} = {getattr(s, a)}")
                except:
                    pass

    # Check game-level attributes
    game_attrs = [a for a in dir(g) if not a.startswith('_') and a not in
                  ('camera', 'current_level', 'perform_action', 'get_pixels', 'set_level')]
    print(f"  Game attrs: {game_attrs}")
    for a in ['ascpmvdpwj', 'zhcrzgpwcp', 'msbtawvatm']:
        try:
            val = getattr(g, a)
            print(f"    {a} = {val}")
        except:
            pass


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'explore':
        level = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        explore_level(level)
    elif len(sys.argv) > 1 and sys.argv[1] == 'bfs':
        level = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        max_iters = int(sys.argv[3]) if len(sys.argv) > 3 else 500000
        max_depth = int(sys.argv[4]) if len(sys.argv) > 4 else None
        g = mod.Ka59()
        g.set_level(level)
        describe_level(g, level)
        bfs_solve(g, level, max_iters=max_iters, max_depth=max_depth)
    else:
        solve_all()
