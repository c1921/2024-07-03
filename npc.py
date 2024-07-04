import numpy as np
import random
import pygame
from map import get_color_and_passable

def generate_npcs(num_npcs, tile_size, x_offset, y_offset, noise_tile):
    """
    生成NPC，确保在非不可通行的地块上随机生成。
    
    参数:
    num_npcs: int, 生成的NPC数量
    tile_size: int, 地图的大小（边长）
    x_offset: int, 地图的x偏移量
    y_offset: int, 地图的y偏移量
    noise_tile: 2D array, 噪波地图数据
    
    返回:
    npcs: list, NPC的坐标列表
    """
    npcs = []
    attempts = 0
    while len(npcs) < num_npcs and attempts < num_npcs * 10:
        x = random.randint(-100, 100)
        y = random.randint(-100, 100)
        tile_x = x + x_offset
        tile_y = y + y_offset
        if 0 <= tile_x < tile_size and 0 <= tile_y < tile_size:
            noise_value = noise_tile[tile_x][tile_y]
            _, passable = get_color_and_passable(noise_value)
            if passable:
                npcs.append((x, y))
        attempts += 1
    return npcs

def draw_npcs(screen, npcs, x_offset, y_offset, tile_size):
    """
    绘制NPC。
    
    参数:
    screen: pygame.Surface, Pygame的屏幕对象
    npcs: list, NPC的坐标列表
    x_offset: int, 地图的x偏移量
    y_offset: int, 地图的y偏移量
    tile_size: int, 每个地块的大小
    """
    for npc in npcs:
        npc_screen_x = (npc[0] - x_offset) * tile_size + tile_size // 2
        npc_screen_y = (npc[1] - y_offset) * tile_size + tile_size // 2
        pygame.draw.circle(screen, (255, 255, 255), (npc_screen_x, npc_screen_y), tile_size // 2)
