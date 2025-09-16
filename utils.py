import pygame
from settings import FONT_SIZE, WIDTH, HEIGHT


def draw_ui(screen, font, tank1, tank2):
    hp_text1 = font.render(f"P1 HP: {tank1.hp}", True, (255, 255, 255))
    screen.blit(hp_text1, (10, HEIGHT - 30))

    hp_text2 = font.render(f"P2 HP: {tank2.hp}", True, (255, 255, 255))
    screen.blit(hp_text2, (WIDTH - 10 - hp_text2.get_width(), 10))
