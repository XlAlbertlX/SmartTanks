# bullet.py
import pygame
from settings import BULLET_SPEED, BULLET_SIZE, BULLET_COLOR, WIDTH, HEIGHT

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, owner):
        super().__init__()
        self.image = pygame.Surface(BULLET_SIZE)
        self.image.fill(BULLET_COLOR)
        self.rect = self.image.get_rect(center=(x, y))
        # направление — pygame.Vector2
        self.direction = direction.normalize()
        self.speed = BULLET_SPEED
        self.owner = owner

    def update(self):
        # движение
        self.rect.x += int(self.direction.x * self.speed)
        self.rect.y += int(self.direction.y * self.speed)
        # удаление за экраном
        if (self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()
