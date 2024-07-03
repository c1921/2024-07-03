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
flash_counter = 0

# 玩家角色
player_pos = [0, 0]  # 玩家角色的初始位置
PLAYER_COLOR = (139, 0, 0)

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

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Infinite Noise Map')

clock = pygame.time.Clock()

x_offset, y_offset = 0, 0
running = True

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
            mouse_x, mouse_y = event.pos
            tile_x = mouse_x // TILE_SIZE + x_offset
            tile_y = mouse_y // TILE_SIZE + y_offset
            clicked_tile = (tile_x, tile_y)
            flash_counter = 0
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
    if keys[pygame.K_UP]:
        player_pos[1] -= 1
    if keys[pygame.K_DOWN]:
        player_pos[1] += 1
    if keys[pygame.K_LEFT]:
        player_pos[0] -= 1
    if keys[pygame.K_RIGHT]:
        player_pos[0] += 1

    # 更新游戏时间
    if not paused:
        current_time = time.time()
        elapsed_time = current_time - last_time
        game_time += elapsed_time / real_time_per_game_hour
        last_time = current_time

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
