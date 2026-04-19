"""DC22 Level 6 complete solution.
Strategy:
  Phase 0: Reveal pickup button + d button via zbhi triggers
  Phase 1: Cycle itki and teleport to pressure plate area
  Phase 2: Use nxhz to move bridge to (12,0)
  Phase 3: Teleport to (18,48), d-cycle to itkizfrq, teleport to (4,4) with bridge in dmxj1
  Phase 4: Walk through bridge and wall gap to target
"""
import importlib.util, copy
import arc_agi
from arcengine import GameAction, ActionInput, InteractionMode

spec = importlib.util.spec_from_file_location('dc22', 'environment_files/dc22/4c9bff3e/dc22.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

UP, DOWN, LEFT, RIGHT = GameAction.ACTION1, GameAction.ACTION2, GameAction.ACTION3, GameAction.ACTION4
CLICK = GameAction.ACTION6

g = mod.Dc22()
g.set_level(5)
all_actions = []

def pos():
    return (g.fdvakicpimr.x, g.fdvakicpimr.y)

def do(action):
    g.perform_action(action)
    all_actions.append(action)

def moves(s):
    for c in s:
        do(ActionInput(id={'U':UP,'D':DOWN,'L':LEFT,'R':RIGHT}[c]))

def click_c():
    do(ActionInput(id=CLICK, data={'x': 51, 'y': 25}))

def click_f():
    do(ActionInput(id=CLICK, data={'x': 56, 'y': 8}))

def click_d():
    do(ActionInput(id=CLICK, data={'x': 51, 'y': 48}))

def click_pickup():
    do(ActionInput(id=CLICK, data={'x': 51, 'y': 18}))

def click_nxhz_left():
    do(ActionInput(id=CLICK, data={'x': 47, 'y': 37}))

def click_nxhz_right():
    do(ActionInput(id=CLICK, data={'x': 55, 'y': 37}))

def click_nxhz_up():
    do(ActionInput(id=CLICK, data={'x': 51, 'y': 33}))  # zmjbupyjfyb: nxhz_y += 1

def move_to_plate(tag):
    plates = {'e': (32,58), 'b': (34,56), 'a': (36,58), 'h': (34,60)}
    tx, ty = plates[tag]
    cx, cy = pos()
    dx, dy = tx - cx, ty - cy
    while dx > 0: moves('R'); dx -= 2
    while dx < 0: moves('L'); dx += 2
    while dy > 0: moves('D'); dy -= 2
    while dy < 0: moves('U'); dy += 2

def check(msg):
    p = pos()
    steps = g.step_counter_ui.rdnpeqedga - g.step_counter_ui.current_steps
    won = g._state.name == "WIN" or g._current_level_index > 5
    print(f"  {msg}: {p} | {len(all_actions)} actions, {steps} steps" + (" | WIN!" if won else ""))
    return won

print("=== DC22 Level 6 Solution ===")

# === PHASE 0: Reveal buttons ===
# Walk to itkiupry1 at (18,48), teleport to (32,52), walk to zbhi at (34,48)
moves('LLLLL')    # (28,52) → (18,52)
moves('UU')       # → (18,48) on itkiupry1
click_c()         # c1: teleport to (32,52), hhxv→dmxj2
moves('UUR')      # → (34,48) steps on zbhi-g → reveals pickup button
check("Phase 0a: pickup revealed")

# Walk back to itki, teleport back
moves('LDD')      # → (32,52) on itkiupry1
click_c()         # c2: teleport to (18,48), hhxv→dmxj1
check("Phase 0b: back at (18,48)")

# Navigate to zbhi at (6,18) for d button
moves('DD')       # → (18,52)
click_c()         # c3: hhxv→dmxj2 (opens vertical column at old pos)
for _ in range(4): click_f()
moves('DDLLL')    # → (12,56)
moves('DL')       # → (10,58)
click_f()
moves('UL')       # → (8,56)
click_f()
moves('U' * 19)   # → (8,18) up through vertical column
moves('L')        # → (6,18) steps on zbhi-d → reveals d button
check("Phase 0c: d button revealed")

# === PHASE 1: Navigate to itki at (18,48) and teleport to (34,58) ===
moves('DDR')      # → (8,22)
moves('D' * 16)   # → (8,54)
moves('R')        # → (10,54)
click_f(); moves('R')
click_f(); moves('R')
click_f(); moves('R')
click_f(); moves('R')  # → (18,54)
moves('UUU')      # → (18,48) on itkiupry2 (swapped by c3)
check("Phase 1: at itki (18,48)")

# Cycle itki with d button: itkiupry2 → itkibgeg2 → itkizfrq2 → itkijbyz2
for _ in range(3): click_d()
click_c()         # c4: teleport to itkijbyz1 at (34,58), hhxv→dmxj1
check("Phase 1: teleported to (34,58)")

# === PHASE 2: Move bridge using nxhz ===
# Move LEFT 4x to reach grid (-4,0) for pickup
move_to_plate('e')  # LEFT arrow
for _ in range(4): click_nxhz_left()
click_pickup()      # Pick up bridge
print(f"  Pickup: attached={g.nxhz_attached_kind}, grid=({g.nxhz_x},{g.nxhz_y})")

# Move to grid (-1,6): R5, U3, L2, U3
# RIGHT: plate 'a'
move_to_plate('a')
for _ in range(5): click_nxhz_right()
# UP (nxhz_y+=1): plate 'b'
move_to_plate('b')
for _ in range(3): click_nxhz_up()
# LEFT: plate 'e'
move_to_plate('e')
for _ in range(2): click_nxhz_left()
# UP: plate 'b'
move_to_plate('b')
for _ in range(3): click_nxhz_up()
print(f"  Bridge grid: ({g.nxhz_x},{g.nxhz_y})")

for sp in g.current_level.get_sprites():
    if 'hhxv-dmxj' in sp.name and sp.interaction != InteractionMode.REMOVED:
        print(f"  Bridge: {sp.name} at ({sp.x},{sp.y})")
check("Phase 2: bridge placed")

# === PHASE 3: Teleport to (4,4) via itkizfrq ===
# Step 1: Walk to itkijbyz2 at (34,58), click c to teleport to (18,48)
# This also rotates bridge to dmxj2 (5th c)
moves('R')  # from plate 'b' at (34,56) → (34,58)... wait check
px, py = pos()
print(f"  Current: ({px},{py})")
# Navigate to (34,58)
if py != 58:
    dy = 58 - py
    while dy > 0: moves('D'); dy -= 2
    while dy < 0: moves('U'); dy += 2
if pos()[0] != 34:
    dx = 34 - pos()[0]
    while dx > 0: moves('R'); dx -= 2
    while dx < 0: moves('L'); dx += 2
check("Phase 3a: at (34,58)")

click_c()  # c5: teleport from itkijbyz2 at (34,58) to itkijbyz2 at (18,48), hhxv→dmxj2
check("Phase 3b: teleported to (18,48)")

# Step 2: d-cycle itki at (18,48): itkijbyz2 → upry2 → bgeg2 → zfrq2
for _ in range(3): click_d()
print(f"  Itki at (18,48):")
for sp in g.current_level.get_sprites():
    if 'itki' in sp.tags and sp.x == 18 and sp.y == 48 and sp.interaction != InteractionMode.REMOVED:
        print(f"    {sp.name}")

# Step 3: click c to teleport from itkizfrq2 at (18,48) to itkizfrq1 at (4,4)
# c6: hhxv→dmxj1 (even number of c's = back to dmxj1)
click_c()
check("Phase 3c: teleported to (4,4)")

# Verify bridge state
for sp in g.current_level.get_sprites():
    if 'hhxv-dmxj' in sp.name and sp.interaction != InteractionMode.REMOVED:
        print(f"  Bridge: {sp.name} at ({sp.x},{sp.y})")

# === PHASE 4: Walk through bridge and wall gap to target ===
# From (4,4), walk down to y=10, then right through bridge to target
moves('DDD')  # (4,4) → (4,10)
check("Phase 4a: at y=10")

# Walk right: through kbqq (x=4-11), bridge (x=12-31), kbqq (x=32-41), wall gap, kbqq (x=42-49)
right_moves = (46 - 4) // 2  # 21 right moves to reach x=46
for _ in range(right_moves):
    moves('R')
check("Phase 4b: at x=46")

# Walk up to target at (46,6)
moves('UU')  # (46,10) → (46,6)
won = check("Phase 4c: at target")

if won:
    print(f"\n=== SOLUTION FOUND: {len(all_actions)} actions ===")
    # Verify with API
    print("\nVerifying with API...")
    arcade = arc_agi.Arcade()
    env = arcade.make("dc22-4c9bff3e", render_mode=None)
    result = env.reset()

    # Skip to level 6 (need to solve L1-L5 first)
    # For now just verify locally for L6
    # The full solver would include L1-L5 solutions
    print(f"L6 local: {len(all_actions)} actions, WIN={won}")

    # Count step types
    moves_count = sum(1 for a in all_actions if a.id != CLICK)
    clicks = sum(1 for a in all_actions if a.id == CLICK)
    print(f"  Moves: {moves_count}, Clicks: {clicks}")
