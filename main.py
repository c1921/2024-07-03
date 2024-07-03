import pygame
import noise
import sys
import numpy as np
import pickle
import os
from config import *

# 初始化Pygame
pygame.init()

# 设置虚拟屏幕和实际窗口大小
virtual_screen = pygame.Surface((VIRTUAL_SCREEN_WIDTH, VIRTUAL_SCREEN_HEIGHT + INFO_HEIGHT))
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT + int(INFO_HEIGHT * WINDOW_SCALE)))
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
player_pos = [0, 0]
player_speed = 1

# 摄像机初始位置
camera_x, camera_y = 0, 0
camera_speed = 5

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

# 按钮区域
button_up = pygame.Rect(720, 610, 50, 20)
button_down = pygame.Rect(720, 640, 50, 20)
button_left = pygame.Rect(680, 625, 50, 20)
button_right = pygame.Rect(760, 625, 50, 20)

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
            mouse_x = int(mouse_x / WINDOW_SCALE)
            mouse_y = int(mouse_y / WINDOW_SCALE)
            if mouse_y < VIRTUAL_SCREEN_HEIGHT:
                tile_x = (camera_x - VIRTUAL_SCREEN_WIDTH // 2 + mouse_x) // TILE_SIZE
                tile_y = (camera_y - VIRTUAL_SCREEN_HEIGHT // 2 + mouse_y) // TILE_SIZE
                selected_tile_coords = (tile_x, tile_y)
            else:
                if button_up.collidepoint(mouse_x, mouse_y):
                    player_pos[1] -= player_speed
                elif button_down.collidepoint(mouse_x, mouse_y):
                    player_pos[1] += player_speed
                elif button_left.collidepoint(mouse_x, mouse_y):
                    player_pos[0] -= player_speed
                elif button_right.collidepoint(mouse_x, mouse_y):
                    player_pos[0] += player_speed

    # 处理键盘输入
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        camera_y -= camera_speed
    if keys[pygame.K_s]:
        camera_y += camera_speed
    if keys[pygame.K_a]:
        camera_x -= camera_speed
    if keys[pygame.K_d]:
        camera_x += camera_speed

    # 计算摄像机所在的块
    camera_tile_x = camera_x // TILE_SIZE
    camera_tile_y = camera_y // TILE_SIZE

    # 清屏
    virtual_screen.fill((0, 0, 0))

    # 绘制当前视野内的地图块
    start_x = camera_tile_x - VIRTUAL_SCREEN_WIDTH // TILE_SIZE // 2
    start_y = camera_tile_y - VIRTUAL_SCREEN_HEIGHT // TILE_SIZE // 2
    for x in range(start_x, start_x + VIRTUAL_SCREEN_WIDTH // TILE_SIZE + 1):
        for y in range(start_y, start_y + VIRTUAL_SCREEN_HEIGHT // TILE_SIZE + 1):
            surface = get_surface(x, y)
            screen_x = (x - start_x) * TILE_SIZE - (camera_x % TILE_SIZE)
            screen_y = (y - start_y) * TILE_SIZE - (camera_y % TILE_SIZE)
            virtual_screen.blit(surface, (screen_x, screen_y))

            # 绘制高亮
            if (x, y) == selected_tile_coords:
                if flash_timer % FLASH_INTERVAL < FLASH_INTERVAL // 2:
                    virtual_screen.blit(flash_surface, (screen_x, screen_y))
            elif (x, y) == highlighted_tile_coords:
                virtual_screen.blit(highlight_surface, (screen_x, screen_y))

    # 绘制玩家
    player_screen_x = (player_pos[0] * TILE_SIZE) - camera_x + VIRTUAL_SCREEN_WIDTH // 2
    player_screen_y = (player_pos[1] * TILE_SIZE) - camera_y + VIRTUAL_SCREEN_HEIGHT // 2
    pygame.draw.circle(virtual_screen, PLAYER_COLOR, (player_screen_x, player_screen_y), TILE_SIZE // 2)

    # 更新高亮块
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_x = int(mouse_x / WINDOW_SCALE)
    mouse_y = int(mouse_y / WINDOW_SCALE)
    if mouse_y < VIRTUAL_SCREEN_HEIGHT:
        highlight_x = (camera_x - VIRTUAL_SCREEN_WIDTH // 2 + mouse_x) // TILE_SIZE
        highlight_y = (camera_y - VIRTUAL_SCREEN_HEIGHT // 2 + mouse_y) // TILE_SIZE
        highlighted_tile_coords = (highlight_x, highlight_y)
    else:
        highlighted_tile_coords = None

    # 绘制底部信息栏
    pygame.draw.rect(virtual_screen, INFO_COLOR, (0, VIRTUAL_SCREEN_HEIGHT, VIRTUAL_SCREEN_WIDTH, INFO_HEIGHT))
    if selected_tile_coords:
        info_text = f'Tile Coordinates: {selected_tile_coords}'
        text_surface = font.render(info_text, True, TEXT_COLOR)
        virtual_screen.blit(text_surface, (10, VIRTUAL_SCREEN_HEIGHT + 5))

    # 绘制按钮
    pygame.draw.rect(virtual_screen, (200, 200, 200), button_up)
    pygame.draw.rect(virtual_screen, (200, 200, 200), button_down)
    pygame.draw.rect(virtual_screen, (200, 200, 200), button_left)
    pygame.draw.rect(virtual_screen, (200, 200, 200), button_right)
    virtual_screen.blit(font.render("Up", True, TEXT_COLOR), (button_up.x + 10, button_up.y + 2))
    virtual_screen.blit(font.render("Down", True, TEXT_COLOR), (button_down.x + 2, button_down.y + 2))
    virtual_screen.blit(font.render("Left", True, TEXT_COLOR), (button_left.x + 2, button_left.y + 2))
    virtual_screen.blit(font.render("Right", True, TEXT_COLOR), (button_right.x + 2, button_right.y + 2))

    # 将虚拟屏幕缩放并绘制到实际窗口
    scaled_screen = pygame.transform.scale(virtual_screen, (SCREEN_WIDTH, SCREEN_HEIGHT + int(INFO_HEIGHT * WINDOW_SCALE)))
    screen.blit(scaled_screen, (0, 0))

    # 更新显示
    pygame.display.flip()
    flash_timer += 1
