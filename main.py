import pygame
import noise
import numpy as np
import pickle
import os
import time
from config import WIDTH, HEIGHT, TILE_SIZE, SCALE, OCTAVES, PERSISTENCE, LACUNARITY, WATER_COLOR, SAND_COLOR, GRASS_COLOR, CACHE_FILE

# 加载缓存数据
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'rb') as f:
        tile_cache = pickle.load(f)
else:
    tile_cache = {}

highlighted_tile = None
clicked_tile = None
marked_tiles = []
flash_counter = 0

# 玩家角色
player_pos = [0, 0]  # 玩家角色的初始位置
PLAYER_COLOR = (139, 0, 0)
target_pos = None  # 玩家角色目标位置
move_speed = 5  # 玩家每小时移动5个地块

# 游戏时间
game_time = 0  # 游戏时间，以小时为单位
real_time_per_game_hour = 30  # 每小时等于实际时间30秒
last_time = time.time()
paused = False

# 生成噪波地图数据
def generate_noise_tile(x_offset, y_offset, tile_size):
    noise_tile = np.zeros((tile_size, tile_size))
    for x in range(tile_size):
        for y in range(tile_size):
            noise_value = noise.pnoise2(
                (x + x_offset) / SCALE,
                (y + y_offset) / SCALE,
                octaves=OCTAVES,
                persistence=PERSISTENCE,
                lacunarity=LACUNARITY,
                repeatx=1024,
                repeaty=1024,
                base=42
            )
            noise_tile[x][y] = noise_value
    return noise_tile

# 获取地图块（带缓存）
def get_tile(x_offset, y_offset, tile_size):
    key = (x_offset, y_offset)
    if key in tile_cache:
        return tile_cache[key]
    else:
        noise_tile = generate_noise_tile(x_offset, y_offset, tile_size)
        tile_cache[key] = noise_tile
        return noise_tile

# 将噪波值映射到颜色
def get_color(value):
    if value < -0.05:
        return WATER_COLOR
    elif value < 0.0:
        return SAND_COLOR
    else:
        return GRASS_COLOR

def increase_brightness(color, factor=1.2):
    return tuple(min(int(c * factor), 255) for c in color)

def draw_noise_map(screen, noise_tile, tile_size, x_offset, y_offset):
    global flash_counter
    for x in range(tile_size):
        for y in range(tile_size):
            abs_x = x + x_offset
            abs_y = y + y_offset
            color = get_color(noise_tile[x][y])
            tile_rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)

            if highlighted_tile == (abs_x, abs_y):
                color = increase_brightness(color)

            if clicked_tile == (abs_x, abs_y):
                if flash_counter % 30 < 15:
                    color = increase_brightness(color, factor=1.5)
            
            pygame.draw.rect(screen, color, tile_rect)

    # 绘制玩家角色
    player_screen_x = (player_pos[0] - x_offset) * TILE_SIZE + TILE_SIZE // 2
    player_screen_y = (player_pos[1] - y_offset) * TILE_SIZE + TILE_SIZE // 2
    pygame.draw.circle(screen, PLAYER_COLOR, (player_screen_x, player_screen_y), TILE_SIZE // 2)

    # 绘制标记
    for mark in marked_tiles:
        mark_screen_x = (mark[0] - x_offset) * TILE_SIZE + TILE_SIZE // 2
        mark_screen_y = (mark[1] - y_offset) * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.polygon(screen, (255, 0, 0), [(mark_screen_x, mark_screen_y - 10), 
                                                  (mark_screen_x - 10, mark_screen_y + 10), 
                                                  (mark_screen_x + 10, mark_screen_y + 10)])

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Infinite Noise Map')

clock = pygame.time.Clock()

x_offset, y_offset = 0, 0
running = True

def move_player_towards_target(elapsed_time):
    global player_pos, target_pos
    if target_pos:
        dx = target_pos[0] - player_pos[0]
        dy = target_pos[1] - player_pos[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        move_distance = move_speed * (elapsed_time / real_time_per_game_hour)
        if distance <= move_distance:
            player_pos = list(target_pos)
            target_pos = None
        else:
            angle = np.arctan2(dy, dx)
            player_pos[0] += move_distance * np.cos(angle)
            player_pos[1] += move_distance * np.sin(angle)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            tile_x = mouse_x // TILE_SIZE + x_offset
            tile_y = mouse_y // TILE_SIZE + y_offset
            highlighted_tile = (tile_x, tile_y)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 3:  # 右键点击
                mouse_x, mouse_y = event.pos
                tile_x = mouse_x // TILE_SIZE + x_offset
                tile_y = mouse_y // TILE_SIZE + y_offset
                menu = pygame.Rect(mouse_x, mouse_y, 100, 60)
                pygame.draw.rect(screen, (200, 200, 200), menu)
                pygame.draw.rect(screen, (0, 0, 0), menu, 2)
                font = pygame.font.Font(None, 24)
                mark_text = font.render('Mark', True, (0, 0, 0))
                move_text = font.render('Move', True, (0, 0, 0))
                screen.blit(mark_text, (mouse_x + 10, mouse_y + 10))
                screen.blit(move_text, (mouse_x + 10, mouse_y + 40))
                pygame.display.flip()
                selecting = True
                while selecting:
                    for sub_event in pygame.event.get():
                        if sub_event.type == pygame.QUIT:
                            running = False
                            selecting = False
                        elif sub_event.type == pygame.MOUSEBUTTONDOWN:
                            if menu.collidepoint(sub_event.pos):
                                if sub_event.pos[1] < mouse_y + 30:
                                    marked_tiles.append((tile_x, tile_y))
                                else:
                                    target_pos = (tile_x, tile_y)
                            selecting = False
                        elif sub_event.type == pygame.KEYDOWN:
                            if sub_event.key == pygame.K_SPACE:
                                paused = not paused
                            selecting = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                paused = not paused

    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        y_offset -= 1
    if keys[pygame.K_s]:
        y_offset += 1
    if keys[pygame.K_a]:
        x_offset -= 1
    if keys[pygame.K_d]:
        x_offset += 1

    # 更新游戏时间
    if not paused:
        current_time = time.time()
        elapsed_time = current_time - last_time
        game_time += elapsed_time / real_time_per_game_hour
        last_time = current_time
        move_player_towards_target(elapsed_time)

    noise_tile = get_tile(x_offset, y_offset, WIDTH // TILE_SIZE)
    draw_noise_map(screen, noise_tile, WIDTH // TILE_SIZE, x_offset, y_offset)

    # 绘制时间和暂停/继续状态
    font = pygame.font.Font(None, 36)
    time_text = font.render(f'Time: {int(game_time)}h', True, (255, 255, 255))
    screen.blit(time_text, (10, 10))

    if paused:
        pause_text = font.render('Paused', True, (255, 0, 0))
        screen.blit(pause_text, (WIDTH - 100, 10))

    pygame.display.flip()
    clock.tick(30)
    flash_counter += 1

# 保存缓存数据
with open(CACHE_FILE, 'wb') as f:
    pickle.dump(tile_cache, f)

pygame.quit()
