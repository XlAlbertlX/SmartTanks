import pygame
from settings import PLAYER_SPEED, PLAYER_SIZE, GREEN, WIDTH, HEIGHT
from bullet import Bullet

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, controls, color=GREEN):
        super().__init__()
        self.image = pygame.Surface(PLAYER_SIZE)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))

        self.controls = controls  # управление (dict с кнопками)
        self.dx, self.dy = 0, -1  # направление (по умолчанию вверх)

    def update(self, keys):
        if keys[self.controls['up']]:
            self.rect.y -= PLAYER_SPEED
            self.dx, self.dy = 0, -1
        if keys[self.controls['down']]:
            self.rect.y += PLAYER_SPEED
            self.dx, self.dy = 0, 1
        if keys[self.controls['left']]:
            self.rect.x -= PLAYER_SPEED
            self.dx, self.dy = -1, 0
        if keys[self.controls['right']]:
            self.rect.x += PLAYER_SPEED
            self.dx, self.dy = 1, 0

        # Ограничения, чтобы не выйти за экран
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(WIDTH, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(HEIGHT, self.rect.bottom)

    def shoot(self, bullets_group):
        bullet = Bullet(self.rect.centerx, self.rect.centery, self.dx, self.dy)
        bullets_group.add(bullet)
        return bullet
