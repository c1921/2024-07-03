import pygame
import time
from map import get_tile, draw_noise_map, highlighted_tile, clicked_tile, marked_tiles, save_cache, target_pos, is_tile_passable, generate_passability_map
from config import WIDTH, HEIGHT, TILE_SIZE, real_time_per_game_hour
from player import move_player_towards_target
from astar import astar

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

while running:
    for event in pygame.event.get():  # 处理事件队列中的所有事件
        if event.type == pygame.QUIT:  # 如果事件类型是QUIT，退出程序
            running = False
        elif event.type == pygame.MOUSEMOTION:  # 如果鼠标移动
            mouse_x, mouse_y = event.pos
            if not menu_active:  # 如果菜单未激活
                tile_x = mouse_x // TILE_SIZE + x_offset  # 计算高亮的地块x坐标
                tile_y = mouse_y // TILE_SIZE + y_offset  # 计算高亮的地块y坐标
                highlighted_tile = (tile_x, tile_y)  # 更新高亮地块
        elif event.type == pygame.MOUSEBUTTONDOWN:  # 如果鼠标按下
            if event.button == 3 and not menu_active:  # 右键点击且菜单未激活
                mouse_x, mouse_y = event.pos
                tile_x = mouse_x // TILE_SIZE + x_offset  # 计算点击的地块x坐标
                tile_y = mouse_y // TILE_SIZE + y_offset  # 计算点击的地块y坐标
                menu_rect = pygame.Rect(mouse_x, mouse_y, 100, 60)  # 创建菜单矩形
                menu_options = [(tile_x, tile_y)]  # 保存菜单选项
                menu_active = True  # 激活菜单
            elif menu_active and menu_rect.collidepoint(event.pos):  # 菜单激活且点击在菜单内
                mouse_x, mouse_y = event.pos
                if mouse_y < menu_rect.y + 30:  # 如果点击在“Mark”区域
                    marked_tiles.append(menu_options[0])  # 标记地块
                else:  # 如果点击在“Move”区域
                    target_pos = menu_options[0]  # 设置目标位置
                    noise_tile = get_tile(x_offset, y_offset, WIDTH // TILE_SIZE)
                    passability_map = generate_passability_map(noise_tile, WIDTH // TILE_SIZE)
                    path = astar(passability_map, (int(player_pos[0] - x_offset), int(player_pos[1] - y_offset)), (int(target_pos[0] - x_offset), int(target_pos[1] - y_offset)))
                menu_active = False  # 关闭菜单
            else:  # 如果点击在菜单外
                menu_active = False  # 关闭菜单
        elif event.type == pygame.KEYDOWN:  # 如果键盘按下
            if event.key == pygame.K_SPACE:  # 按下空格键，暂停/继续
                paused = not paused

    keys = pygame.key.get_pressed()  # 获取所有按键状态
    if keys[pygame.K_w]:  # 如果按下W键
        y_offset -= 1  # 更新y轴偏移
    if keys[pygame.K_s]:  # 如果按下S键
        y_offset += 1  # 更新y轴偏移
    if keys[pygame.K_a]:  # 如果按下A键
        x_offset -= 1  # 更新x轴偏移
    if keys[pygame.K_d]:  # 如果按下D键
        x_offset += 1  # 更新x轴偏移

    # 更新游戏时间
    if not paused:
        current_time = time.time()  # 获取当前时间
        elapsed_time = current_time - last_time  # 计算自上次更新以来的时间
        game_time += elapsed_time / real_time_per_game_hour  # 更新游戏时间
        last_time = current_time  # 更新最后时间
        if path:
            next_step = path.pop(0)
            player_pos = [next_step[0] + x_offset, next_step[1] + y_offset]

    noise_tile = get_tile(x_offset, y_offset, WIDTH // TILE_SIZE)  # 获取当前视角的噪波地图
    draw_noise_map(screen, noise_tile, WIDTH // TILE_SIZE, x_offset, y_offset, flash_counter, player_pos, highlighted_tile, clicked_tile, marked_tiles, target_pos)  # 绘制地图

    # 绘制时间和暂停/继续状态
    font = pygame.font.Font(None, 36)
    time_text = font.render(f'Time: {int(game_time)}h', True, (255, 255, 255))
    screen.blit(time_text, (10, 10))  # 显示游戏时间

    if paused:
        pause_text = font.render('Paused', True, (255, 0, 0))
        screen.blit(pause_text, (WIDTH - 100, 10))  # 显示暂停状态

    # 绘制坐标信息
    coord_font = pygame.font.Font(None, 28)
    player_coord_text = coord_font.render(f'Player: ({player_pos[0]:.1f}, {player_pos[1]:.1f})', True, (255, 255, 255))
    mouse_coord_text = coord_font.render(f'Mouse: {highlighted_tile}', True, (255, 255, 255))
    screen.blit(player_coord_text, (10, HEIGHT - 30))  # 显示玩家坐标
    screen.blit(mouse_coord_text, (WIDTH - 200, HEIGHT - 30))  # 显示鼠标悬浮地块的坐标

    # 如果菜单激活，绘制菜单
    if menu_active:
        pygame.draw.rect(screen, (200, 200, 200), menu_rect)  # 绘制菜单背景
        pygame.draw.rect(screen, (0, 0, 0), menu_rect, 2)  # 绘制菜单边框
        font = pygame.font.Font(None, 24)
        mark_text = font.render('Mark', True, (0, 0, 0))
        move_text = font.render('Move', True, (0, 0, 0))
        screen.blit(mark_text, (menu_rect.x + 10, menu_rect.y + 10))  # 显示“Mark”文本
        screen.blit(move_text, (menu_rect.x + 10, menu_rect.y + 40))  # 显示“Move”文本

    pygame.display.flip()  # 更新屏幕显示
    clock.tick(30)  # 控制帧率
    flash_counter += 1  # 更新闪烁计数器

# 保存缓存数据
save_cache()
pygame.quit()  # 退出Pygame
