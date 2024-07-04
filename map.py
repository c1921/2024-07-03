import pygame
import noise
import numpy as np
import pickle
import os
from config import TILE_SIZE, SCALE, OCTAVES, PERSISTENCE, LACUNARITY, WATER_COLOR, SAND_COLOR, GRASS_COLOR, CACHE_FILE

# 加载缓存数据
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'rb') as f:
        tile_cache = pickle.load(f)
else:
    tile_cache = {}

highlighted_tile = None
clicked_tile = None
marked_tiles = []
target_pos = None  # 玩家角色目标位置

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

def draw_noise_map(screen, noise_tile, tile_size, x_offset, y_offset, flash_counter, player_pos, highlighted_tile, clicked_tile, marked_tiles, target_pos):
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
    pygame.draw.circle(screen, (139, 0, 0), (player_screen_x, player_screen_y), TILE_SIZE // 2)

    # 绘制标记
    for mark in marked_tiles:
        mark_screen_x = (mark[0] - x_offset) * TILE_SIZE + TILE_SIZE // 2
        mark_screen_y = (mark[1] - y_offset) * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.polygon(screen, (255, 0, 0), [(mark_screen_x, mark_screen_y - 10), 
                                                  (mark_screen_x - 10, mark_screen_y + 10), 
                                                  (mark_screen_x + 10, mark_screen_y + 10)])

    # 绘制目标十字标志
    if target_pos:
        target_screen_x = (target_pos[0] - x_offset) * TILE_SIZE + TILE_SIZE // 2
        target_screen_y = (target_pos[1] - y_offset) * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.line(screen, (255, 0, 0), (target_screen_x - 10, target_screen_y), (target_screen_x + 10, target_screen_y), 2)
        pygame.draw.line(screen, (255, 0, 0), (target_screen_x, target_screen_y - 10), (target_screen_x, target_screen_y + 10), 2)

# 保存缓存数据
def save_cache():
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(tile_cache, f)
