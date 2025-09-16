import pygame
from settings import *
from tank import Player, Bot
from bullet import Bullet

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Tanks")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, FONT_SIZE)

# ===== Карта =====
obstacles = [
    pygame.Rect(200,150,500,20),
    pygame.Rect(100,300,20,300),
    pygame.Rect(700,300,20,300),
    pygame.Rect(300,400,300,20),
    pygame.Rect(400,500,20,100)
]

grid_w = WIDTH // GRID_CELL
grid_h = HEIGHT // GRID_CELL
grid = [[0]*grid_w for _ in range(grid_h)]
for rect in obstacles:
    for y in range(rect.top//GRID_CELL, (rect.bottom+GRID_CELL-1)//GRID_CELL):
        for x in range(rect.left//GRID_CELL, (rect.right+GRID_CELL-1)//GRID_CELL):
            if 0<=x<grid_w and 0<=y<grid_h:
                grid[y][x] = 1

# ===== Игрок и бот =====
controls = {'up':pygame.K_w, 'down':pygame.K_s,'left':pygame.K_a,'right':pygame.K_d}
player = Player(WIDTH//2, HEIGHT-80, controls)
bot = Bot(WIDTH//2, 80, grid)
all_sprites = [player, bot]
bullets_group = pygame.sprite.Group()

def show_end_screen(screen, text):
    running = True
    button_font = pygame.font.SysFont(None, 36)
    while running:
        screen.fill((0,0,0))
        label = font.render(text, True, (255,255,0))
        rect = label.get_rect(center=(WIDTH//2, HEIGHT//2-50))
        screen.blit(label, rect)

        # кнопки
        play_rect = pygame.Rect(WIDTH//2-100, HEIGHT//2+20, 200,50)
        exit_rect = pygame.Rect(WIDTH//2-100, HEIGHT//2+90, 200,50)
        pygame.draw.rect(screen, (50,200,50), play_rect)
        pygame.draw.rect(screen, (200,50,50), exit_rect)
        screen.blit(button_font.render("Играть снова", True, (0,0,0)), (play_rect.x+30, play_rect.y+10))
        screen.blit(button_font.render("Выйти", True, (0,0,0)), (exit_rect.x+70, exit_rect.y+10))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit()
                exit()
            if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if play_rect.collidepoint(event.pos):
                    return True
                if exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    exit()

running = True
while running:
    clock.tick(FPS)
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type==pygame.QUIT:
            running=False
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            direction = pygame.Vector2(pygame.mouse.get_pos()) - pygame.Vector2(player.rect.center)
            if direction.length()>0 and player.can_shoot():
                b = Bullet(player.rect.centerx, player.rect.centery, direction, owner=player)
                bullets_group.add(b)
                player.last_shot_time = pygame.time.get_ticks()

    player.update(keys, obstacles)
    bot.update(player, bullets_group, obstacles)
    bullets_group.update()

    # столкновения пуль
    for bullet in bullets_group:
        if bullet.owner != player and player.rect.colliderect(bullet.rect):
            player.hp -= 1
            bullet.kill()
        elif bullet.owner != bot and bot.rect.colliderect(bullet.rect):
            bot.hp -=1
            bullet.kill()
        else:
            for obs in obstacles:
                if bullet.rect.colliderect(obs):
                    bullet.kill()
                    break

    screen.fill(BG_COLOR)
    for rect in obstacles:
        pygame.draw.rect(screen, OBSTACLE_COLOR, rect)
    for t in all_sprites:
        t.draw(screen)
    bullets_group.draw(screen)
    screen.blit(font.render(f"P1 HP: {player.hp}", True, HP_TEXT_COLOR), (10, HEIGHT-30))
    screen.blit(font.render(f"P2 HP: {bot.hp}", True, HP_TEXT_COLOR), (WIDTH-10-120,10))
    pygame.display.flip()

    # проверка конца игры
    if player.hp <=0:
        if show_end_screen(screen, "Бот выиграл!"):
            exec(open(__file__).read())
        break
    elif bot.hp<=0:
        if show_end_screen(screen, "Игрок выиграл!"):
            exec(open(__file__).read())
        break

pygame.quit()
