# main.py
import pygame, random
from settings import *
from tank import Player, Bot
from bullet import Bullet
from model import LogisticModel, raycast_count_obstacles

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Tanks — ML Bot")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, FONT_SIZE)
button_font = pygame.font.SysFont(None, 32)

# ===== карта (стены разной формы) =====
obstacles = [
    pygame.Rect(160,120,580,20),
    pygame.Rect(100,260,20,240),
    pygame.Rect(780,260,20,240),
    pygame.Rect(260,380,380,20),
    pygame.Rect(420,480,20,160),
    pygame.Rect(320,220,20,120),
    pygame.Rect(560,220,20,120)
]
# grid
grid_w = WIDTH // GRID_CELL; grid_h = HEIGHT // GRID_CELL
grid = [[0]*grid_w for _ in range(grid_h)]
for rect in obstacles:
    for y in range(rect.top//GRID_CELL, (rect.bottom+GRID_CELL-1)//GRID_CELL):
        for x in range(rect.left//GRID_CELL, (rect.right+GRID_CELL-1)//GRID_CELL):
            if 0<=x<grid_w and 0<=y<grid_h:
                grid[y][x] = 1

# ===== создаём и обучаем модель на данной карте =====
model = LogisticModel(n_features=5)
# тренируем (набор генерируется внутри train_on_map)
# это может занять ~0.5-2 сек в зависимости от ML_TRAIN_SAMPLES и ML_EPOCHS
model.train_on_map(obstacles, grid_w, grid_h, samples=ML_TRAIN_SAMPLES)

# ===== функция экрана конца (Play again / Exit) =====
def show_end_screen(screen, text):
    while True:
        screen.fill((0,0,0))
        label = font.render(text, True, (255,220,0))
        rect = label.get_rect(center=(WIDTH//2, HEIGHT//2 - 60))
        screen.blit(label, rect)

        play_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 0, 240, 56)
        exit_rect = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 80, 240, 56)
        pygame.draw.rect(screen, (70,200,70), play_rect); pygame.draw.rect(screen, (200,70,70), exit_rect)
        screen.blit(button_font.render("Играть снова", True, (0,0,0)), (play_rect.x+40, play_rect.y+12))
        screen.blit(button_font.render("Выйти", True, (0,0,0)), (exit_rect.x+95, exit_rect.y+12))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
                if play_rect.collidepoint(event.pos):
                    return True
                if exit_rect.collidepoint(event.pos):
                    pygame.quit(); return False

# ===== основная функция игры (возвращает True если Replay) =====
def run_game():
    # создаём игрока и бота (передаём модель в бота)
    controls = {'up':pygame.K_w,'down':pygame.K_s,'left':pygame.K_a,'right':pygame.K_d}
    player = Player(WIDTH//2, HEIGHT-80, controls)
    bot = Bot(WIDTH//2, 80, grid, model)
    all_sprites = [player, bot]
    bullets_group = pygame.sprite.Group()

    running = True
    while running:
        clock.tick(FPS)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # стрельба игрока по клику
                mp = pygame.Vector2(pygame.mouse.get_pos())
                dirv = mp - pygame.Vector2(player.rect.center)
                if dirv.length() > 0 and player.can_shoot():
                    b = Bullet(player.rect.centerx, player.rect.centery, dirv, owner=player)
                    bullets_group.add(b)
                    player.last_shot_time = pygame.time.get_ticks()

        # обновления
        player.update(keys, obstacles)
        bot.update(player, bullets_group, obstacles)
        bullets_group.update()

        # пули vs препятствия и танки
        for bullet in list(bullets_group):
            hit = False
            # пуля попадает в игрока/бота
            if bullet.owner is not player and player.rect.colliderect(bullet.rect):
                player.hp -= 1; bullet.kill(); hit = True
            elif bullet.owner is not bot and bot.rect.colliderect(bullet.rect):
                bot.hp -= 1; bullet.kill(); hit = True
            if hit: continue
            # пуля в стену
            for obs in obstacles:
                if bullet.rect.colliderect(obs):
                    bullet.kill(); break

        # отрисовка
        screen.fill(BG_COLOR)
        for r in obstacles:
            pygame.draw.rect(screen, OBSTACLE_COLOR, r)
        for t in all_sprites:
            t.draw(screen)
        bullets_group.draw(screen)
        # UI
        screen.blit(font.render(f"P1 HP: {player.hp}", True, HP_TEXT_COLOR), (10, HEIGHT-36))
        screen.blit(font.render(f"Bot HP: {bot.hp}", True, HP_TEXT_COLOR), (WIDTH-170, 10))
        pygame.display.flip()

        # проверка конца
        if player.hp <= 0:
            # show end screen
            replay = show_end_screen(screen, "Бот выиграл!")
            return replay
        if bot.hp <= 0:
            replay = show_end_screen(screen, "Игрок выиграл!")
            return replay
    return False

# ===== main loop: повтор при выборе "Играть снова" =====
if __name__ == "__main__":
    replay = True
    while replay:
        replay = run_game()
    pygame.quit()
