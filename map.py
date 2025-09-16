# map.py
import pygame
from settings import WIDTH, HEIGHT, GRID_CELL, OBSTACLE_COLOR

class GameMap:
    def __init__(self):
        # obstacles: list of pygame.Rect
        self.obstacles = []
        self.create_sample_map()

    def create_sample_map(self):
        # некоторые статические препятствия — прямоугольники
        w, h = WIDTH, HEIGHT
        # рамка
        self.obstacles.append(pygame.Rect(0, 0, w, 16))
        self.obstacles.append(pygame.Rect(0, h-16, w, 16))
        self.obstacles.append(pygame.Rect(0, 0, 16, h))
        self.obstacles.append(pygame.Rect(w-16, 0, 16, h))

        # центральные блоки (чтобы делало игру интереснее)
        self.obstacles.append(pygame.Rect(220, 160, 200, 40))
        self.obstacles.append(pygame.Rect(480, 120, 40, 220))
        self.obstacles.append(pygame.Rect(140, 420, 320, 40))
        self.obstacles.append(pygame.Rect(520, 420, 260, 40))
        self.obstacles.append(pygame.Rect(380, 320, 40, 160))
        self.obstacles.append(pygame.Rect(720, 200, 40, 240))

        # добавим несколько маленьких ящиков
        self.obstacles.append(pygame.Rect(100, 100, 60, 60))
        self.obstacles.append(pygame.Rect(760, 540, 80, 60))

    def draw(self, surf):
        for r in self.obstacles:
            pygame.draw.rect(surf, OBSTACLE_COLOR, r)

    def collides_rect(self, rect):
        """True если rect пересекает любое препятствие."""
        for r in self.obstacles:
            if rect.colliderect(r):
                return True
        return False

    def raycast_clear(self, start_pos, end_pos):
        """Проверка на прямую видимость от start_pos до end_pos (line segment).
           Простая реализация: шаг по параметру t и проверка попадания в obstacle rect.
        """
        sx, sy = start_pos
        ex, ey = end_pos
        dx = ex - sx
        dy = ey - sy
        steps = int(max(abs(dx), abs(dy)) // 6) + 1
        for i in range(steps + 1):
            t = i / steps
            x = sx + dx * t
            y = sy + dy * t
            p = (int(x), int(y))
            # check if point inside any obstacle
            for r in self.obstacles:
                if r.collidepoint(p):
                    return False
        return True

    def get_grid(self):
        """Возвращает сетку проходности для pathfinding: 0 — свободно, 1 — препятствие"""
        cols = WIDTH // GRID_CELL
        rows = HEIGHT // GRID_CELL
        grid = [[0 for _ in range(cols)] for __ in range(rows)]
        for r in self.obstacles:
            left = r.left // GRID_CELL
            top = r.top // GRID_CELL
            right = (r.right - 1) // GRID_CELL
            bottom = (r.bottom - 1) // GRID_CELL
            for gy in range(max(0, top), min(rows, bottom + 1)):
                for gx in range(max(0, left), min(cols, right + 1)):
                    grid[gy][gx] = 1
        return grid
