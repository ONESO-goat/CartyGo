"""
Cart Auto Simulation
====================
A parking lot sandbox for testing autonomous shopping cart behavior.
Watch carts navigate, fail, and (eventually) succeed at returning home.
"""

import pygame
import sys
import random
import math
from enum import Enum
from collections import deque

# ─────────────────────────────────────────────
#  CONSTANTS
# ─────────────────────────────────────────────
SCREEN_W, SCREEN_H = 1200, 800
TILE = 40          # grid tile size in pixels
COLS  = SCREEN_W // TILE   # 30
ROWS  = SCREEN_H // TILE   # 20
FPS   = 60

# Colors (muted, industrial palette)
C_BG         = (45,  48,  52)
C_ASPHALT    = (58,  62,  68)
C_LANE       = (70,  75,  82)
C_LINE       = (200, 190, 120)
C_SIDEWALK   = (160, 155, 145)
C_STORE      = (80,  110, 140)
C_STORE_DOOR = (150, 200, 230)
C_CORRAL     = (60,  90,  60)
C_CORRAL_BDR = (100, 180, 100)
C_PARKED_CAR = (100, 105, 115)
C_MOVING_CAR = (180, 140,  60)
C_CART       = (220, 220, 220)
C_CART_AUTO  = (80,  200, 120)   # autonomous cart
C_CART_BAD   = (220,  80,  80)   # cart in trouble
C_CITIZEN    = (220, 160, 100)
C_HUD_BG     = (20,  22,  26, 200)
C_GREEN      = (80,  200, 120)
C_RED        = (220,  80,  80)
C_YELLOW     = (240, 200,  60)
C_WHITE      = (240, 240, 240)
C_GRAY       = (120, 125, 135)
C_DEBUG      = (60,  180, 220, 120)


# ─────────────────────────────────────────────
#  TILE TYPES
# ─────────────────────────────────────────────
class Tile(Enum):
    LANE      = 0   # driveable
    PARKING   = 1   # parking space
    SIDEWALK  = 2   # pedestrian
    STORE     = 3   # store building (blocked)
    CORRAL    = 4   # cart home
    DIVIDER   = 5   # median / curb (blocked)


# Which tiles block cars vs carts vs citizens
CAR_BLOCKED     = {Tile.STORE, Tile.SIDEWALK, Tile.DIVIDER, Tile.CORRAL}
CART_BLOCKED    = {Tile.STORE, Tile.DIVIDER}
CITIZEN_BLOCKED = {Tile.STORE, Tile.LANE}   # citizens avoid fast lanes mostly


# ─────────────────────────────────────────────
#  PARKING LOT MAP  (30 cols × 20 rows)
# ─────────────────────────────────────────────
# Layout key:
#   0 = lane   1 = parking   2 = sidewalk
#   3 = store  4 = corral    5 = divider

RAW_MAP = [
    # 0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  25  26  27  28  29
    [ 2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2],  # row 0  sidewalk top
    [ 2,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  2],  # row 1  store
    [ 2,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  2],  # row 2  store
    [ 2,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  3,  2],  # row 3  store
    [ 2,  2,  2,  4,  2,  2,  2,  2,  2,  4,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  4,  2,  2,  2,  2,  2,  4,  2,  2,  2],  # row 4  sidewalk w/ corrals
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],  # row 5  main lane
    [ 1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  0],  # row 6  parking row A
    [ 1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  0],  # row 7  parking row A
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],  # row 8  inner lane
    [ 5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5,  5],  # row 9  divider / median
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],  # row 10 inner lane
    [ 1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  0],  # row 11 parking row B
    [ 1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  0],  # row 12 parking row B
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],  # row 13 lane
    [ 1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  0],  # row 14 parking row C
    [ 1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  1,  1,  0],  # row 15 parking row C
    [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],  # row 16 lane
    [ 1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  4,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  4,  1,  1,  0,  1,  1,  0],  # row 17 parking row D w/ corrals
    [ 1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  4,  1,  1,  0,  1,  1,  1,  0,  1,  1,  1,  0,  4,  1,  1,  0,  1,  1,  0],  # row 18 parking row D w/ corrals
    [ 2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2,  2],  # row 19 sidewalk bottom
]

GRID = [[Tile(v) for v in row] for row in RAW_MAP]

# Gather corral positions (grid coords)
CORRAL_POSITIONS = [
    (r, c) for r in range(ROWS) for c in range(COLS)
    if GRID[r][c] == Tile.CORRAL
]

# Gather lane positions for car spawning
LANE_POSITIONS = [
    (r, c) for r in range(ROWS) for c in range(COLS)
    if GRID[r][c] == Tile.LANE
]

# Gather parking positions
PARKING_POSITIONS = [
    (r, c) for r in range(ROWS) for c in range(COLS)
    if GRID[r][c] == Tile.PARKING
]

# Sidewalk positions for citizens
SIDEWALK_POSITIONS = [
    (r, c) for r in range(ROWS) for c in range(COLS)
    if GRID[r][c] in (Tile.SIDEWALK, Tile.PARKING, Tile.CORRAL)
]


# ─────────────────────────────────────────────
#  PATHFINDING  (BFS on grid)
# ─────────────────────────────────────────────
def bfs(start_rc, goal_rc, blocked_tiles):
    """Simple BFS returning list of (row,col) from start to goal."""
    sr, sc = start_rc
    gr, gc = goal_rc
    if (sr, sc) == (gr, gc):
        return []
    visited = {(sr, sc)}
    queue = deque([[(sr, sc)]])
    while queue:
        path = queue.popleft()
        r, c = path[-1]
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and (nr,nc) not in visited:
                if GRID[nr][nc] not in blocked_tiles:
                    new_path = path + [(nr, nc)]
                    if (nr, nc) == (gr, gc):
                        return new_path
                    visited.add((nr, nc))
                    queue.append(new_path)
    return []  # no path found


def pixel_to_grid(px, py):
    return py // TILE, px // TILE

def grid_to_pixel_center(r, c):
    return c * TILE + TILE // 2, r * TILE + TILE // 2


# ─────────────────────────────────────────────
#  CART STATE MACHINE
# ─────────────────────────────────────────────
class CartState(Enum):
    IDLE      = "idle"        # sitting in corral, happy
    DEPLOYED  = "deployed"    # being used / abandoned
    RETURNING = "returning"   # autonomously heading home
    BLOCKED   = "blocked"     # obstacle in path
    EMERGENCY = "emergency"   # force stop, something went wrong


# ─────────────────────────────────────────────
#  CART
# ─────────────────────────────────────────────
class Cart:
    SIZE = 14
    ABANDON_TIMEOUT = 8.0     # seconds until auto-return triggers
    RETURN_SPEED    = 1.2     # pixels per frame when returning

    def __init__(self, x, y, home_rc, autonomous=True):
        self.x = float(x)
        self.y = float(y)
        self.home_rc  = home_rc           # (row, col) of assigned corral
        self.home_px  = grid_to_pixel_center(*home_rc)
        self.state    = CartState.DEPLOYED
        self.autonomous = autonomous
        self.path     = []                # BFS waypoints [(r,c), ...]
        self.path_idx = 0
        self.idle_timer = 0.0             # how long since last touched
        self.blocked_timer = 0.0
        self.collision_flash = 0          # frames of red flash
        self.rect = pygame.Rect(int(self.x) - self.SIZE//2,
                                int(self.y) - self.SIZE//2,
                                self.SIZE, self.SIZE)
        self.trail = deque(maxlen=20)     # debug trail
        self.penalty_this_frame = 0       # score delta

    @property
    def grid_pos(self):
        return pixel_to_grid(int(self.x), int(self.y))

    def request_path_home(self):
        start = self.grid_pos
        goal  = self.home_rc
        self.path = bfs(start, goal, CART_BLOCKED)
        self.path_idx = 0

    def update(self, dt, all_carts, citizens, cars, score_manager):
        self.penalty_this_frame = 0
        self.rect.topleft = (int(self.x) - self.SIZE//2, int(self.y) - self.SIZE//2)

        if self.collision_flash > 0:
            self.collision_flash -= 1

        if self.state == CartState.IDLE:
            return

        # ── Idle timer → trigger autonomous return ──
        if self.state == CartState.DEPLOYED and self.autonomous:
            self.idle_timer += dt
            if self.idle_timer >= self.ABANDON_TIMEOUT:
                self.state = CartState.RETURNING
                self.request_path_home()

        # ── Navigate home ──
        if self.state == CartState.RETURNING:
            self._navigate(dt, all_carts, citizens, cars, score_manager)

        # ── Score penalties ──
        self._check_boundary(score_manager)

    def _navigate(self, dt, all_carts, citizens, cars, score_manager):
        if not self.path or self.path_idx >= len(self.path):
            # Arrived!
            hx, hy = self.home_px
            if math.hypot(self.x - hx, self.y - hy) < TILE:
                self.x, self.y = hx, hy
                self.state = CartState.IDLE
                score_manager.add(15, "Cart returned home!")
            else:
                self.request_path_home()
            return

        # Target next waypoint
        tr, tc = self.path[self.path_idx]
        tx, ty = grid_to_pixel_center(tr, tc)
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)

        # Check for nearby obstacles
        blocked = self._detect_obstacle(all_carts, citizens, cars)
        if blocked:
            self.blocked_timer += 1/FPS
            self.state = CartState.BLOCKED
            if self.blocked_timer > 2.0:
                # Re-route
                self.request_path_home()
                self.blocked_timer = 0
            return
        else:
            self.state = CartState.RETURNING
            self.blocked_timer = 0

        if dist < 3:
            self.trail.append((self.x, self.y))
            self.path_idx += 1
        else:
            speed = self.RETURN_SPEED
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed

    def _detect_obstacle(self, all_carts, citizens, cars):
        """Return True if something is too close ahead."""
        DANGER = self.SIZE * 2.2
        for obj in list(all_carts) + list(citizens) + list(cars):
            if obj is self:
                continue
            ox = getattr(obj, 'x', None)
            oy = getattr(obj, 'y', None)
            if ox is None: continue
            if math.hypot(self.x - ox, self.y - oy) < DANGER:
                return True
        return False

    def _check_boundary(self, score_manager):
        r, c = self.grid_pos
        if not (0 <= r < ROWS and 0 <= c < COLS):
            score_manager.add(-10, "Cart out of bounds!")
            self.penalty_this_frame += 10

    def hit(self, score_manager, reason="Collision"):
        """Called when this cart collides with something."""
        self.collision_flash = 20
        score_manager.add(-5, reason)
        self.penalty_this_frame += 5

    def draw(self, surf, debug=False):
        # Debug trail
        if debug and len(self.trail) > 1:
            pts = [(int(x), int(y)) for x, y in self.trail]
            pygame.draw.lines(surf, C_DEBUG[:3], False, pts, 1)

        # Debug path
        if debug and self.path:
            for pr, pc in self.path[self.path_idx:]:
                px, py = grid_to_pixel_center(pr, pc)
                pygame.draw.circle(surf, C_DEBUG[:3], (px, py), 3)

        # Body color
        if self.collision_flash > 0:
            color = C_CART_BAD
        elif self.state == CartState.RETURNING:
            color = C_CART_AUTO
        elif self.state == CartState.IDLE:
            color = C_CORRAL_BDR
        elif self.state == CartState.BLOCKED:
            color = C_YELLOW
        else:
            color = C_CART

        r = pygame.Rect(int(self.x)-self.SIZE//2, int(self.y)-self.SIZE//2,
                        self.SIZE, self.SIZE)
        pygame.draw.rect(surf, color, r, border_radius=2)
        pygame.draw.rect(surf, C_WHITE, r, 1, border_radius=2)

        # Debug collision radius
        if debug:
            s = pygame.Surface((self.SIZE*5, self.SIZE*5), pygame.SRCALPHA)
            pygame.draw.circle(s, (*C_DEBUG[:3], 40),
                               (self.SIZE*5//2, self.SIZE*5//2), self.SIZE*2)
            surf.blit(s, (int(self.x)-self.SIZE*5//2, int(self.y)-self.SIZE*5//2))


# ─────────────────────────────────────────────
#  CITIZEN  (NPC pedestrian)
# ─────────────────────────────────────────────
class Citizen:
    RADIUS   = 7
    SPEED    = 0.6
    WANDER_INTERVAL = (60, 180)  # frames between direction changes

    def __init__(self, x, y):
        self.x   = float(x)
        self.y   = float(y)
        self.vx  = random.uniform(-1, 1)
        self.vy  = random.uniform(-1, 1)
        self._normalise()
        self.wander_timer = random.randint(*self.WANDER_INTERVAL)
        self.color = (
            random.randint(180, 240),
            random.randint(120, 180),
            random.randint(80, 140)
        )
        self.carrying_cart = False

    def _normalise(self):
        mag = math.hypot(self.vx, self.vy) or 1
        self.vx /= mag
        self.vy /= mag

    def update(self):
        self.wander_timer -= 1
        if self.wander_timer <= 0:
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-1, 1)
            self._normalise()
            self.wander_timer = random.randint(*self.WANDER_INTERVAL)

        nx = self.x + self.vx * self.SPEED
        ny = self.y + self.vy * self.SPEED

        # Stay in walkable tiles
        nr, nc = pixel_to_grid(int(nx), int(ny))
        if 0 <= nr < ROWS and 0 <= nc < COLS and GRID[nr][nc] not in CITIZEN_BLOCKED:
            self.x, self.y = nx, ny
        else:
            self.vx = random.uniform(-1, 1)
            self.vy = random.uniform(-1, 1)
            self._normalise()

        # Clamp to screen
        self.x = max(self.RADIUS, min(SCREEN_W - self.RADIUS, self.x))
        self.y = max(self.RADIUS, min(SCREEN_H - self.RADIUS, self.y))

    def draw(self, surf, debug=False):
        ix, iy = int(self.x), int(self.y)
        pygame.draw.circle(surf, self.color, (ix, iy), self.RADIUS)
        pygame.draw.circle(surf, C_WHITE,   (ix, iy), self.RADIUS, 1)
        # Head dot
        pygame.draw.circle(surf, C_WHITE,   (ix, iy - self.RADIUS + 3), 3)

        if debug:
            s = pygame.Surface((self.RADIUS*6, self.RADIUS*6), pygame.SRCALPHA)
            pygame.draw.circle(s, (220, 160, 100, 40),
                               (self.RADIUS*3, self.RADIUS*3), self.RADIUS*2)
            surf.blit(s, (ix - self.RADIUS*3, iy - self.RADIUS*3))


# ─────────────────────────────────────────────
#  CAR  (NPC vehicle)
# ─────────────────────────────────────────────
class Car:
    W, H   = 32, 18
    SPEED  = 0.8
    PARK_CHANCE = 0.0015   # chance per frame to start parking

    def __init__(self):
        # Spawn on edge lanes
        self._spawn_edge()
        self.parked = False
        self.park_timer = 0
        self.color = (
            random.randint(80, 200),
            random.randint(80, 200),
            random.randint(80, 200)
        )

    def _spawn_edge(self):
        side = random.choice(['left','right','top_lane','bottom_lane'])
        if side == 'left':
            self.x = -self.W
            self.y = float(random.choice([5,8,10,13,16]) * TILE + TILE//2)
            self.vx, self.vy = self.SPEED, 0
        elif side == 'right':
            self.x = float(SCREEN_W + self.W)
            self.y = float(random.choice([5,8,10,13,16]) * TILE + TILE//2)
            self.vx, self.vy = -self.SPEED, 0
        elif side == 'top_lane':
            self.x = float(random.choice(range(2, COLS-2)) * TILE + TILE//2)
            self.y = -self.H
            self.vx, self.vy = 0, self.SPEED
        else:
            self.x = float(random.choice(range(2, COLS-2)) * TILE + TILE//2)
            self.y = float(SCREEN_H + self.H)
            self.vx, self.vy = 0, -self.SPEED

        self.angle = math.degrees(math.atan2(-self.vy, self.vx))

    def update(self):
        if self.parked:
            self.park_timer -= 1
            if self.park_timer <= 0:
                self.parked = False
            return

        # Occasionally park
        if random.random() < self.PARK_CHANCE:
            r, c = pixel_to_grid(int(self.x), int(self.y))
            # Only park if near a parking tile
            for dr in range(-1,2):
                for dc in range(-1,2):
                    nr, nc = r+dr, c+dc
                    if 0<=nr<ROWS and 0<=nc<COLS and GRID[nr][nc]==Tile.PARKING:
                        self.parked = True
                        self.park_timer = random.randint(120, 480)
                        return

        self.x += self.vx
        self.y += self.vy
        self.angle = math.degrees(math.atan2(-self.vy, self.vx))

    def is_offscreen(self):
        return (self.x < -100 or self.x > SCREEN_W+100 or
                self.y < -100 or self.y > SCREEN_H+100)

    def draw(self, surf):
        car_surf = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        pygame.draw.rect(car_surf, self.color, (0, 0, self.W, self.H), border_radius=4)
        pygame.draw.rect(car_surf, C_WHITE,    (0, 0, self.W, self.H), 1, border_radius=4)
        # Windshield hint
        pygame.draw.rect(car_surf, (*C_WHITE, 80), (4, 2, 10, self.H-4), border_radius=2)
        rotated = pygame.transform.rotate(car_surf, self.angle)
        r = rotated.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(rotated, r)


# ─────────────────────────────────────────────
#  SCORE MANAGER
# ─────────────────────────────────────────────
class ScoreManager:
    def __init__(self):
        self.score = 0
        self.events = deque(maxlen=8)   # recent score events for HUD

    def add(self, delta, reason=""):
        self.score += delta
        color = C_GREEN if delta > 0 else C_RED
        self.events.append((reason, delta, color, 180))  # 180 frame fade

    def tick(self):
        """Age out events."""
        aged = []
        for reason, delta, color, ttl in self.events:
            if ttl > 0:
                aged.append((reason, delta, color, ttl-1))
        self.events = deque(aged, maxlen=8)


# ─────────────────────────────────────────────
#  PARKING LOT  (map renderer + collision)
# ─────────────────────────────────────────────
class ParkingLot:
    def __init__(self):
        self.surface = pygame.Surface((SCREEN_W, SCREEN_H))
        self._bake_surface()

    def _bake_surface(self):
        """Pre-render the static map once."""
        self.surface.fill(C_ASPHALT)
        for r in range(ROWS):
            for c in range(COLS):
                tile = GRID[r][c]
                rect = pygame.Rect(c*TILE, r*TILE, TILE, TILE)

                if tile == Tile.LANE:
                    pygame.draw.rect(self.surface, C_LANE, rect)
                elif tile == Tile.PARKING:
                    pygame.draw.rect(self.surface, C_ASPHALT, rect)
                    pygame.draw.rect(self.surface, C_LINE, rect, 1)
                elif tile == Tile.SIDEWALK:
                    pygame.draw.rect(self.surface, C_SIDEWALK, rect)
                elif tile == Tile.STORE:
                    pygame.draw.rect(self.surface, C_STORE, rect)
                elif tile == Tile.CORRAL:
                    pygame.draw.rect(self.surface, C_CORRAL, rect)
                    pygame.draw.rect(self.surface, C_CORRAL_BDR, rect, 2)
                    # Draw 'H' for Home
                    font = pygame.font.SysFont('monospace', 14, bold=True)
                    lbl = font.render("H", True, C_CORRAL_BDR)
                    self.surface.blit(lbl, (c*TILE + TILE//2 - 4, r*TILE + TILE//2 - 7))
                elif tile == Tile.DIVIDER:
                    pygame.draw.rect(self.surface, C_BG, rect)
                    # Hatch pattern
                    for i in range(0, TILE, 8):
                        pygame.draw.line(self.surface, C_GRAY,
                                         (c*TILE, r*TILE+i), (c*TILE+i, r*TILE), 1)

        # Store entrance doors
        for dc in [12, 13, 16, 17]:
            door_rect = pygame.Rect(dc*TILE+2, 3*TILE, TILE-4, TILE//2)
            pygame.draw.rect(self.surface, C_STORE_DOOR, door_rect, border_radius=2)

        # Lane direction arrows (subtle)
        arrow_font = pygame.font.SysFont('monospace', 10)
        for c in range(0, COLS, 5):
            for lane_r in [5, 8, 10, 13, 16]:
                direction = "→" if lane_r in [5, 10, 16] else "←"
                lbl = arrow_font.render(direction, True, (*C_LINE[:3], 80))
                self.surface.blit(lbl, (c*TILE + 4, lane_r*TILE + 14))

    def draw(self, surf):
        surf.blit(self.surface, (0, 0))


# ─────────────────────────────────────────────
#  GAME MANAGER
# ─────────────────────────────────────────────
class GameManager:
    NUM_CARTS    = 12
    NUM_CITIZENS = 14
    MAX_CARS     = 6
    CAR_SPAWN_RATE = 180   # frames

    def __init__(self):
        pygame.init()
        self.screen  = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Cart Auto Sim — Julius' Parking Lot")
        self.clock   = pygame.time.Clock()

        self.lot     = ParkingLot()
        self.score   = ScoreManager()
        self.carts   = []
        self.citizens = []
        self.cars    = []

        self.debug   = False
        self.paused  = False
        self.car_spawn_timer = 0
        self.total_time = 0.0

        self._init_fonts()
        self._spawn_initial()

    def _init_fonts(self):
        self.font_sm  = pygame.font.SysFont('monospace', 11)
        self.font_md  = pygame.font.SysFont('monospace', 14, bold=True)
        self.font_lg  = pygame.font.SysFont('monospace', 22, bold=True)
        self.font_hd  = pygame.font.SysFont('monospace', 13)

    def _spawn_initial(self):
        # Spawn carts — some in corrals, some abandoned
        corrals = list(CORRAL_POSITIONS)
        for i in range(self.NUM_CARTS):
            home_rc = random.choice(corrals)
            if i < len(corrals):
                # Start in corral
                px, py = grid_to_pixel_center(*home_rc)
                cart = Cart(px, py, home_rc, autonomous=True)
                cart.state = CartState.IDLE
                cart.idle_timer = 0
            else:
                # Abandoned somewhere in parking/lane
                pos = random.choice(PARKING_POSITIONS + LANE_POSITIONS)
                px, py = grid_to_pixel_center(*pos)
                cart = Cart(px, py, home_rc, autonomous=True)
                cart.state = CartState.DEPLOYED
                cart.idle_timer = random.uniform(0, self.NUM_CARTS)
            self.carts.append(cart)

        # Spawn citizens on sidewalks
        for _ in range(self.NUM_CITIZENS):
            pos = random.choice(SIDEWALK_POSITIONS)
            px, py = grid_to_pixel_center(*pos)
            px += random.randint(-10, 10)
            py += random.randint(-10, 10)
            self.citizens.append(Citizen(float(px), float(py)))

        # Spawn initial cars
        for _ in range(3):
            self.cars.append(Car())

    def _spawn_car(self):
        if len(self.cars) < self.MAX_CARS:
            self.cars.append(Car())

    def _check_collisions(self):
        # Cart ↔ Citizen
        for cart in self.carts:
            if cart.state in (CartState.IDLE,):
                continue
            cr = pygame.Rect(int(cart.x)-cart.SIZE, int(cart.y)-cart.SIZE,
                             cart.SIZE*2, cart.SIZE*2)
            for citizen in self.citizens:
                dist = math.hypot(cart.x - citizen.x, cart.y - citizen.y)
                if dist < cart.SIZE + citizen.RADIUS + 2:
                    cart.hit(self.score, "Hit citizen!")
                    # Bounce citizen away
                    dx = citizen.x - cart.x or 1
                    dy = citizen.y - cart.y or 1
                    mag = math.hypot(dx, dy) or 1
                    citizen.x += dx/mag * 8
                    citizen.y += dy/mag * 8

        # Cart ↔ Car
        for cart in self.carts:
            if cart.state == CartState.IDLE:
                continue
            for car in self.cars:
                dist = math.hypot(cart.x - car.x, cart.y - car.y)
                if dist < cart.SIZE + car.W//2:
                    cart.hit(self.score, "Hit a car!")

        # Cart ↔ Cart
        for i, ca in enumerate(self.carts):
            for cb in self.carts[i+1:]:
                if ca.state == CartState.IDLE and cb.state == CartState.IDLE:
                    continue
                dist = math.hypot(ca.x - cb.x, ca.y - cb.y)
                if dist < ca.SIZE + cb.SIZE - 2:
                    if ca.state != CartState.IDLE:
                        ca.hit(self.score, "Carts collided!")
                    if cb.state != CartState.IDLE:
                        cb.hit(self.score, "Carts collided!")

    def _draw_hud(self):
        # Score panel (top-left)
        hud_w, hud_h = 280, 160
        hud = pygame.Surface((hud_w, hud_h), pygame.SRCALPHA)
        hud.fill((20, 22, 26, 210))
        pygame.draw.rect(hud, C_GRAY, (0, 0, hud_w, hud_h), 1, border_radius=4)

        score_color = C_GREEN if self.score.score >= 0 else C_RED
        score_lbl = self.font_lg.render(f"SCORE  {self.score.score:+}", True, score_color)
        hud.blit(score_lbl, (12, 10))

        # Cart status counts
        states = {s: 0 for s in CartState}
        for c in self.carts:
            states[c.state] += 1

        y = 42
        state_colors = {
            CartState.IDLE:      C_CORRAL_BDR,
            CartState.DEPLOYED:  C_CART,
            CartState.RETURNING: C_CART_AUTO,
            CartState.BLOCKED:   C_YELLOW,
            CartState.EMERGENCY: C_RED,
        }
        for s, cnt in states.items():
            col = state_colors[s]
            pygame.draw.rect(hud, col, (12, y+2, 8, 8), border_radius=2)
            lbl = self.font_sm.render(f"{s.value.upper():12s} {cnt}", True, C_WHITE)
            hud.blit(lbl, (26, y))
            y += 16

        # Time
        mins = int(self.total_time // 60)
        secs = int(self.total_time % 60)
        time_lbl = self.font_sm.render(f"TIME  {mins:02d}:{secs:02d}", True, C_GRAY)
        hud.blit(time_lbl, (12, y+2))

        self.screen.blit(hud, (10, 10))

        # Event feed (top-right)
        ex = SCREEN_W - 300
        ey = 10
        for reason, delta, color, ttl in list(self.score.events)[-6:]:
            alpha = min(255, ttl * 2)
            sign = "+" if delta > 0 else ""
            txt = f"{sign}{delta}  {reason}"
            lbl = self.font_hd.render(txt, True, color)
            lbl.set_alpha(alpha)
            self.screen.blit(lbl, (ex, ey))
            ey += 18

        # Controls (bottom-left)
        ctrl_lines = [
            "[D] Debug overlay",
            "[P] Pause",
            "[R] Respawn carts",
            "[ESC] Quit",
        ]
        cy = SCREEN_H - len(ctrl_lines)*16 - 8
        for line in ctrl_lines:
            lbl = self.font_sm.render(line, True, C_GRAY)
            self.screen.blit(lbl, (10, cy))
            cy += 16

        # Debug banner
        if self.debug:
            dbg = self.font_md.render("[ DEBUG MODE ON ]", True, C_DEBUG[:3])
            self.screen.blit(dbg, (SCREEN_W//2 - dbg.get_width()//2, 10))

        if self.paused:
            pau = self.font_lg.render("PAUSED", True, C_YELLOW)
            self.screen.blit(pau, (SCREEN_W//2 - pau.get_width()//2, SCREEN_H//2))

    def _respawn_carts(self):
        """Reset all deployed/abandoned carts, give them fresh idle timers."""
        for cart in self.carts:
            if cart.state != CartState.IDLE:
                pos = random.choice(PARKING_POSITIONS)
                cart.x, cart.y = grid_to_pixel_center(*pos)
                cart.state = CartState.DEPLOYED
                cart.idle_timer = random.uniform(0, 6)
                cart.path = []
                cart.path_idx = 0

    def run(self):
        while True:
            dt = self.clock.tick(FPS) / 1000.0
            self.total_time += dt if not self.paused else 0

            # ── Events ──
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()
                    if event.key == pygame.K_d:
                        self.debug = not self.debug
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    if event.key == pygame.K_r:
                        self._respawn_carts()

            if not self.paused:
                # ── Spawn cars ──
                self.car_spawn_timer += 1
                if self.car_spawn_timer >= self.CAR_SPAWN_RATE:
                    self._spawn_car()
                    self.car_spawn_timer = 0

                # ── Update NPCs ──
                for citizen in self.citizens:
                    citizen.update()

                for car in self.cars:
                    car.update()
                self.cars = [c for c in self.cars if not c.is_offscreen()]

                # ── Update carts ──
                for cart in self.carts:
                    cart.update(dt, self.carts, self.citizens, self.cars, self.score)

                # ── Passive score: reward organized carts ──
                idle_count = sum(1 for c in self.carts if c.state == CartState.IDLE)
                if idle_count > 0 and int(self.total_time * 10) % 20 == 0:
                    self.score.add(1, f"{idle_count} carts home")

                # ── Passive penalty: abandoned carts blocking lanes ──
                for cart in self.carts:
                    r, c = cart.grid_pos
                    if (0 <= r < ROWS and 0 <= c < COLS and
                            GRID[r][c] == Tile.LANE and
                            cart.state == CartState.DEPLOYED and
                            cart.idle_timer > 5):
                        if random.random() < 0.002:
                            self.score.add(-2, "Cart blocking lane!")

                self._check_collisions()
                self.score.tick()

            # ── Draw ──
            self.lot.draw(self.screen)

            for car in self.cars:
                car.draw(self.screen)

            for cart in self.carts:
                cart.draw(self.screen, debug=self.debug)

            for citizen in self.citizens:
                citizen.draw(self.screen, debug=self.debug)

            self._draw_hud()

            pygame.display.flip()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    gm = GameManager()
    gm.run()