import pygame
import time
from map import get_tile, draw_noise_map, highlighted_tile, clicked_tile, marked_tiles, save_cache, target_pos, is_tile_passable, generate_passability_map
from config import WIDTH, HEIGHT, TILE_SIZE, real_time_per_game_hour, MENU_WIDTH, MENU_HEIGHT, MENU_OPTION_HEIGHT
from player import move_player_towards_target
from astar import astar
from npc import generate_npcs, draw_npcs
from inventory import Inventory
from button import Button

flash_counter = 0

# 玩家角色
player_pos = [0, 0]  # 玩家角色的初始位置
move_speed = 5  # 玩家每小时移动5个地块

# 游戏时间
game_time = 0  # 游戏时间，以小时为单位
last_time = time.time()
paused = False

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Infinite Noise Map')

clock = pygame.time.Clock()

x_offset, y_offset = 0, 0
running = True
menu_active = False  # 标志菜单是否激活
menu_rect = None  # 菜单矩形
menu_options = []  # 菜单选项

path = []  # 存储路径

# 生成NPC
noise_tile = get_tile(x_offset, y_offset, WIDTH // TILE_SIZE)
npcs = generate_npcs(10, WIDTH // TILE_SIZE, x_offset, y_offset, noise_tile)

# 初始化物品栏
inventory = Inventory(10)  # 设置物品栏容量为10
inventory.add_item("Sword")
inventory.add_item("Shield")

# 物品栏显示状态
show_inventory = False

# 创建按钮
button = Button(WIDTH - 120, 10, 100, 40, "Inventory")

def draw_game(screen, noise_tile, player_pos, highlighted_tile, clicked_tile, marked_tiles, target_pos, flash_counter, game_time, paused, menu_active, menu_rect, npcs, inventory, show_inventory, path, x_offset, y_offset):
    draw_noise_map(screen, noise_tile, WIDTH // TILE_SIZE, x_offset, y_offset, flash_counter, player_pos, highlighted_tile, clicked_tile, marked_tiles, target_pos)
    draw_npcs(screen, npcs, x_offset, y_offset, TILE_SIZE)
    
    # 绘制时间和暂停/继续状态
    font = pygame.font.Font(None, 36)
    time_text = font.render(f'Time: {int(game_time)}h', True, (255, 255, 255))
    screen.blit(time_text, (10, 10))
    
    if paused:
        pause_text = font.render('Paused - Press SPACE to continue', True, (255, 0, 0))
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2))
    
    # 绘制坐标信息
    coord_font = pygame.font.Font(None, 28)
    player_coord_text = coord_font.render(f'Player: ({player_pos[0]:.1f}, {player_pos[1]:.1f})', True, (255, 255, 255))
    mouse_coord_text = coord_font.render(f'Mouse: {highlighted_tile}', True, (255, 255, 255))
    screen.blit(player_coord_text, (10, HEIGHT - 30))
    screen.blit(mouse_coord_text, (WIDTH - 200, HEIGHT - 30))
    
    # 绘制按钮
    button.draw(screen)
    
    # 绘制物品栏
    if show_inventory:
        inventory.draw_inventory(screen, WIDTH - 300, 50, 280, HEIGHT - 100)
    
    # 如果菜单激活，绘制菜单
    if menu_active:
        pygame.draw.rect(screen, (200, 200, 200), menu_rect)
        pygame.draw.rect(screen, (0, 0, 0), menu_rect, 2)
        font = pygame.font.Font(None, 24)
        mark_text = font.render('Mark', True, (0, 0, 0))
        move_text = font.render('Move', True, (0, 0, 0))
        screen.blit(mark_text, (menu_rect.x + 10, menu_rect.y + 10))
        screen.blit(move_text, (menu_rect.x + 10, menu_rect.y + 40))
    
    # 绘制路径
    for step in path:
        step_x = (step[0] - x_offset) * TILE_SIZE + TILE_SIZE // 2
        step_y = (step[1] - y_offset) * TILE_SIZE + TILE_SIZE // 2
        pygame.draw.circle(screen, (255, 0, 0), (step_x, step_y), 5)

    pygame.display.flip()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            mouse_x, mouse_y = event.pos
            if not menu_active:
                tile_x = mouse_x // TILE_SIZE + x_offset
                tile_y = mouse_y // TILE_SIZE + y_offset
                highlighted_tile = (tile_x, tile_y)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击
                if button.is_clicked(event.pos):  # 如果点击了按钮
                    show_inventory = not show_inventory  # 切换物品栏显示状态
                elif menu_active and menu_rect.collidepoint(event.pos):  # 如果菜单激活且点击在菜单内
                    mouse_x, mouse_y = event.pos
                    if mouse_y < menu_rect.y + MENU_OPTION_HEIGHT:  # 如果点击在“Mark”区域
                        marked_tiles.append(menu_options[0])  # 标记地块
                    else:  # 如果点击在“Move”区域
                        target_pos = menu_options[0]  # 设置目标位置
                        noise_tile = get_tile(x_offset, y_offset, WIDTH // TILE_SIZE)
                        passability_map = generate_passability_map(noise_tile, WIDTH // TILE_SIZE)
                        start_pos = (int(player_pos[0]), int(player_pos[1]))
                        end_pos = (int(target_pos[0]), int(target_pos[1]))
                        print(f"Start: {start_pos}, End: {end_pos}")  # 调试信息
                        path = astar(passability_map, start_pos, end_pos)
                        print(f"Path: {path}")  # 调试信息
                    menu_active = False  # 关闭菜单
                else:
                    menu_active = False  # 如果点击在菜单外，关闭菜单
            elif event.button == 3 and not menu_active:  # 右键点击且菜单未激活
                mouse_x, mouse_y = event.pos
                tile_x = mouse_x // TILE_SIZE + x_offset
                tile_y = mouse_y // TILE_SIZE + y_offset
                menu_rect = pygame.Rect(mouse_x, mouse_y, MENU_WIDTH, MENU_HEIGHT)
                menu_options = [(tile_x, tile_y)]
                menu_active = True
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

    if not paused:
        current_time = time.time()
        elapsed_time = current_time - last_time
        game_time += elapsed_time / real_time_per_game_hour
        last_time = current_time
        
        player_pos, target_pos, path, reached = move_player_towards_target(player_pos, target_pos, elapsed_time, move_speed, path)
        if reached:
            target_pos = None

    noise_tile = get_tile(x_offset, y_offset, WIDTH // TILE_SIZE)
    draw_game(screen, noise_tile, player_pos, highlighted_tile, clicked_tile, marked_tiles, target_pos, flash_counter, game_time, paused, menu_active, menu_rect, npcs, inventory, show_inventory, path, x_offset, y_offset)
    
    clock.tick(30)
    flash_counter += 1

save_cache()
pygame.quit()
