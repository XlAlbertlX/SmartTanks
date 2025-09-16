import pygame
import heapq
from settings import *

from bullet import Bullet

# ===== A* =====
class Node:
    def __init__(self, pos, g=0, h=0, parent=None):
        self.pos = pos
        self.g = g
        self.h = h
        self.f = g+h
        self.parent = parent

    def __lt__(self, other):
        return self.f < other.f

def heuristic(a, b):
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def astar(grid, start, goal):
    goal_x = max(0, min(goal[0], len(grid[0])-1))
    goal_y = max(0, min(goal[1], len(grid)-1))
    goal = (goal_x, goal_y)

    open_list = []
    closed = set()
    heapq.heappush(open_list, Node(start, 0, heuristic(start, goal)))

    while open_list:
        current = heapq.heappop(open_list)
        if current.pos == goal:
            path = []
            while current:
                path.append(current.pos)
                current = current.parent
            return path[::-1]

        closed.add(current.pos)
        x, y = current.pos
        for dx, dy in [(1,0),(-1,0),(0,1),(0,-1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
                if grid[ny][nx] == 1 or (nx, ny) in closed:
                    continue
                heapq.heappush(open_list, Node((nx, ny), current.g+1, heuristic((nx, ny), goal), current))
    return []

# ===== Танки =====
class Tank(pygame.sprite.Sprite):
    def __init__(self, x, y, color, hp=TANK_HP):
        super().__init__()
        self.body_image = pygame.Surface(TANK_BODY_SIZE)
        self.body_image.fill(color)
        self.turret_image = pygame.Surface(TURRET_SIZE)
        self.turret_image.fill((200, 50, 50))
        self.rect = self.body_image.get_rect(center=(x, y))
        self.speed = TANK_SPEED
        self.hp = hp
        self.color = color
        self.facing = pygame.Vector2(0, -1)
        self.shoot_cooldown = TANK_COOLDOWN
        self.last_shot_time = 0

    def can_shoot(self):
        return pygame.time.get_ticks() - self.last_shot_time >= self.shoot_cooldown

    def draw(self, screen):
        screen.blit(self.body_image, self.rect)
        angle = -self.facing.angle_to(pygame.Vector2(0, -1))
        rotated = pygame.transform.rotate(self.turret_image, angle)
        turret_rect = rotated.get_rect(center=self.rect.center)
        screen.blit(rotated, turret_rect)

class Player(Tank):
    def __init__(self, x, y, controls, color=PLAYER_COLOR, hp=TANK_HP):
        super().__init__(x, y, color, hp)
        self.controls = controls

    def update(self, keys, obstacles):
        dx = dy = 0
        if keys[self.controls['up']]:
            dy = -self.speed
        if keys[self.controls['down']]:
            dy = self.speed
        if keys[self.controls['left']]:
            dx = -self.speed
        if keys[self.controls['right']]:
            dx = self.speed

        self.rect.x += dx
        for obs in obstacles:
            if self.rect.colliderect(obs):
                if dx>0: self.rect.right=obs.left
                elif dx<0: self.rect.left=obs.right
        self.rect.y += dy
        for obs in obstacles:
            if self.rect.colliderect(obs):
                if dy>0: self.rect.bottom=obs.top
                elif dy<0: self.rect.top=obs.bottom

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        direction = mouse_pos - pygame.Vector2(self.rect.center)
        if direction.length() > 0:
            self.facing = direction.normalize()

class Bot(Tank):
    def __init__(self, x, y, grid, color=BOT_COLOR, hp=TANK_HP):
        super().__init__(x, y, color, hp)
        self.grid = grid
        self.path = []
        self.current_target = None
        self.recalc_timer = 0

    def update(self, player, bullets_group, obstacles):
        now = pygame.time.get_ticks()
        start = (self.rect.centerx // GRID_CELL, self.rect.centery // GRID_CELL)
        goal = (player.rect.centerx // GRID_CELL, player.rect.centery // GRID_CELL)

        if not self.path or now - self.recalc_timer > BOT_PATH_RECALC_MS:
            self.path = astar(self.grid, start, goal)
            self.recalc_timer = now
            if len(self.path) > 1:
                self.current_target = self.path[1]
            else:
                self.current_target = start

        if self.current_target:
            target_px = (self.current_target[0]*GRID_CELL + GRID_CELL//2,
                         self.current_target[1]*GRID_CELL + GRID_CELL//2)
            vec = pygame.Vector2(target_px) - pygame.Vector2(self.rect.center)
            if vec.length() > 1:
                move = vec.normalize() * self.speed
                self.rect.x += int(move.x)
                self.rect.y += int(move.y)
                for obs in obstacles:
                    if self.rect.colliderect(obs):
                        if move.x>0: self.rect.right=obs.left
                        elif move.x<0: self.rect.left=obs.right
                        if move.y>0: self.rect.bottom=obs.top
                        elif move.y<0: self.rect.top=obs.bottom

        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

        distance = pygame.Vector2(player.rect.center) - pygame.Vector2(self.rect.center)
        if self.can_shoot() and distance.length() < 400:
            direction = distance.normalize()
            b = Bullet(self.rect.centerx, self.rect.centery, direction, owner=self)
            bullets_group.add(b)
            self.last_shot_time = now
