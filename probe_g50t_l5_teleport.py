"""G50T L5: test whether ghost-held sw[0]+sw[1] enables teleport from ulhh[4].

Plan:
  Prefix: walk to sw[0] + ACTION5 (ghost A)
          walk to sw[1] + ACTION5 (ghost B)
          walk to ulhh[4]
  After reaching ulhh[4], check if player is at (43, 37) or got teleported
  to (43, 49).

Then BFS from final state toward WIN.
"""
import importlib.util
from collections import deque
from arcengine import GameAction, ActionInput

spec = importlib.util.spec_from_file_location(
    'g50t', 'environment_files/g50t/5849a774/g50t.py'
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ACTION_NAMES = {'U': 'ACTION1', 'D': 'ACTION2', 'L': 'ACTION3', 'R': 'ACTION4'}


def fresh():
    g = mod.G50t()
    g.set_level(4)
    return g


def do(g, name):
    full = name if name.startswith('ACTION') else ACTION_NAMES[name]
    g.perform_action(ActionInput(id=getattr(GameAction, full)))


def apply(g, seq):
    for a in seq:
        do(g, a)


def pos(g):
    p = g.vgwycxsxjz.dzxunlkwxt
    return (p.x, p.y)


def doors(g):
    return tuple((d.x, d.y, bool(d.dijhfchobv)) for d in g.vgwycxsxjz.uwxkstolmf)


def sw_state(g):
    return tuple(getattr(h, 'dijhfchobv', None) for h in g.vgwycxsxjz.hamayflsib)


def is_win(g):
    return g._state.name == "WIN" or g._current_level_index > 4


# Ghost paths (ending on their respective switches):
# sw[0] path: UDDRRRUURRRRRRDDD (17 moves, ending at (55,25))
# sw[1] path: DDDRRRD (7 moves, ending at (19,37))
GHOST_A_PATH = list('UDDRRRUURRRRRRDDD')  # 17 moves → sw[0]
GHOST_B_PATH = list('DDDRRRD')  # 7 moves → sw[1]

# But wait: these paths modify latch states. Need to check how many times each
# path crosses sw[2] and sw[3].
#   GHOST_A_PATH: starts at (1,13). U to (1,7)=sw[3] (press #1). D→(1,13), D→(1,19),
#     R→(7,19), R→(13,19), R→(19,19), U→(19,13), U→(19,7) [door[2] latched by
#     previous sw[3] press so (19,7) open], R→(25,7), R→(31,7), R→(37,7),
#     R→(43,7), R→(49,7), R→(55,7), D→(55,13), D→(55,19), D→(55,25)=sw[0] press.
#     Presses: sw[3]×1, sw[0]×1. No sw[2], no sw[1].
#   GHOST_B_PATH: starts at (1,13). D→(1,19), D→(1,25), D→(1,31), R→(7,31),
#     R→(13,31), R→(19,31), D→(19,37)=sw[1] press.
#     Presses: sw[1]×1. No sw[2], no sw[3], no sw[0].
#
# Combined: sw[3] pressed once by ghost A (latch on). sw[0] pressed once by
# ghost A (transient). sw[1] pressed once by ghost B (transient). sw[2] never
# pressed by ghosts.
#
# But wait: during the FINAL live-player phase, the live player walks from
# (1,13) to ulhh[4]. That walk will press sw[2] once (on the way). So sw[2]
# will latch.

PREFIX = GHOST_A_PATH + ['ACTION5'] + GHOST_B_PATH + ['ACTION5']


def main():
    g = fresh()
    apply(g, PREFIX)
    print(f"After prefix ({len(PREFIX)} actions):")
    print(f"  player: {pos(g)}")
    print(f"  doors: {doors(g)}")
    print(f"  sw: {sw_state(g)}")
    print(f"  ghost count: {len(g.vgwycxsxjz.rloltuowth)}")
    print(f"  ghost paths: {[len(v) for v in g.vgwycxsxjz.rloltuowth.values()]}")

    # Now BFS for WIN from this state.
    # State key = (player_pos, door_states, clamped_move_count).
    # Clamp to max ghost path length (17) since beyond that ghost positions
    # are frozen and move count no longer affects future transitions.
    MAX_GHOST_LEN = max(len(GHOST_A_PATH), len(GHOST_B_PATH))
    print("\nBFS for win...")
    start_key = (pos(g), doors(g), 0)
    seen = {start_key: []}
    q = deque([(start_key, [])])
    best = None
    max_depth = 35
    while q:
        (p, d, _), path = q.popleft()
        if best and len(path) >= len(best):
            continue
        if len(path) > max_depth:
            continue
        for name in 'UDLR':
            g2 = fresh()
            apply(g2, PREFIX + path + [name])
            if is_win(g2):
                full = PREFIX + path + [name]
                if not best or len(full) < len(best):
                    best = full
                    print(f"  WIN at total {len(full)} actions")
                break
            new_p = pos(g2)
            new_d = doors(g2)
            new_mc = min(len(path) + 1, MAX_GHOST_LEN)
            new_key = (new_p, new_d, new_mc)
            if new_key in seen:
                continue
            seen[new_key] = path + [name]
            q.append((new_key, path + [name]))

    if best:
        print(f"\n=== L5 SOLUTION ({len(best)} actions vs baseline 96) ===")
        print(f"Ratio: {100*len(best)/96:.1f}%")
        to_letter = {'U': 'U', 'D': 'D', 'L': 'L', 'R': 'R', 'ACTION5': '!'}
        print(''.join(to_letter.get(a, '?') for a in best))
    else:
        print(f"\nNo win found. {len(seen)} states explored.")
        tiles = set(k[0] for k in seen)
        print(f"Distinct tiles: {len(tiles)}")


if __name__ == "__main__":
    main()
