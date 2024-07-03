import pygame
import noise
import sys
import numpy as np
import pickle
import os
from config import *

# 初始化Pygame
pygame.init()

# 设置屏幕大小
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + INFO_HEIGHT))
pygame.display.set_caption('Infinite Map with Tile Coordinates Display')

# 缓存已生成的块
tile_cache = {}
surface_cache = {}

# 加载缓存
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'rb') as f:
        tile_cache = pickle.load(f)

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

# 将噪波值映射到颜色
def get_color(value):
    if value < -0.05:
        return WATER_COLOR
    elif value < 0.0:
        return SAND_COLOR
    elif value < 0.5:
        return GRASS_COLOR
    elif value < 0.75:
        return MOUNTAIN_COLOR
    else:
        return SNOW_COLOR

# 获取地图块
def get_tile(x, y):
    if (x, y) not in tile_cache:
        tile_cache[(x, y)] = generate_noise_tile(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE)
    return tile_cache[(x, y)]

# 创建Surface缓存
def get_surface(x, y):
    if (x, y) not in surface_cache:
        tile = get_tile(x, y)
        surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
        for i in range(TILE_SIZE):
            for j in range(TILE_SIZE):
                color = get_color(tile[i][j])
                surface.set_at((i, j), color)
        surface_cache[(x, y)] = surface
    return surface_cache[(x, y)]

# 玩家初始位置 (0, 0) 坐标
player_x, player_y = 0, 0
player_speed = 5

# 初始化字体
pygame.font.init()
font = pygame.font.SysFont(None, FONT_SIZE)

# 显示的信息
selected_tile_coords = None
highlighted_tile_coords = None
flash_timer = 0

# 半透明颜色
highlight_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
highlight_surface.fill(HIGHLIGHT_COLOR)
flash_surface = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
flash_surface.fill(FLASH_COLOR)

# 游戏循环
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # 保存缓存
            with open(CACHE_FILE, 'wb') as f:
                pickle.dump(tile_cache, f)
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = event.pos
            if mouse_y < SCREEN_HEIGHT:
                tile_x = (player_x - SCREEN_WIDTH // 2 + mouse_x) // TILE_SIZE
                tile_y = (player_y - SCREEN_HEIGHT // 2 + mouse_y) // TILE_SIZE
                selected_tile_coords = (tile_x, tile_y)

    # 处理键盘输入
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player_y -= player_speed
    if keys[pygame.K_s]:
        player_y += player_speed
    if keys[pygame.K_a]:
        player_x -= player_speed
    if keys[pygame.K_d]:
        player_x += player_speed

    # 计算玩家所在的块
    player_tile_x = player_x // TILE_SIZE
    player_tile_y = player_y // TILE_SIZE

    # 清屏
    screen.fill((0, 0, 0))

    # 绘制当前视野内的地图块
    start_x = player_tile_x - SCREEN_WIDTH // TILE_SIZE // 2
    start_y = player_tile_y - SCREEN_HEIGHT // TILE_SIZE // 2
    for x in range(start_x, start_x + SCREEN_WIDTH // TILE_SIZE + 1):
        for y in range(start_y, start_y + SCREEN_HEIGHT // TILE_SIZE + 1):
            surface = get_surface(x, y)
            screen_x = (x - start_x) * TILE_SIZE - (player_x % TILE_SIZE)
            screen_y = (y - start_y) * TILE_SIZE - (player_y % TILE_SIZE)
            screen.blit(surface, (screen_x, screen_y))

            # 绘制高亮
            if (x, y) == selected_tile_coords:
                if flash_timer % FLASH_INTERVAL < FLASH_INTERVAL // 2:
                    screen.blit(flash_surface, (screen_x, screen_y))
            elif (x, y) == highlighted_tile_coords:
                screen.blit(highlight_surface, (screen_x, screen_y))

    # 更新高亮块
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if mouse_y < SCREEN_HEIGHT:
        highlight_x = (player_x - SCREEN_WIDTH // 2 + mouse_x) // TILE_SIZE
        highlight_y = (player_y - SCREEN_HEIGHT // 2 + mouse_y) // TILE_SIZE
        highlighted_tile_coords = (highlight_x, highlight_y)
    else:
        highlighted_tile_coords = None

    # 绘制底部信息栏
    pygame.draw.rect(screen, INFO_COLOR, (0, SCREEN_HEIGHT, SCREEN_WIDTH, INFO_HEIGHT))
    if selected_tile_coords:
        info_text = f'Tile Coordinates: {selected_tile_coords}'
        text_surface = font.render(info_text, True, TEXT_COLOR)
        screen.blit(text_surface, (10, SCREEN_HEIGHT + 5))

    # 更新显示
    pygame.display.flip()
    flash_timer += 1
