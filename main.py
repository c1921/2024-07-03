import pygame
import time
from map import get_tile, draw_noise_map, highlighted_tile, clicked_tile, marked_tiles, save_cache
from config import WIDTH, HEIGHT, TILE_SIZE, real_time_per_game_hour
from player import move_player_towards_target

flash_counter = 0

# 玩家角色
player_pos = [0, 0]  # 玩家角色的初始位置
target_pos = None  # 玩家角色目标位置
move_speed = 5  # 玩家每小时移动5个地块

# 游戏时间
game_time = 0  # 游戏时间，以小时为单位
last_time = time.time()
paused = False

dragging = False  # 用于窗口拖动的标志
drag_offset_x = 0
drag_offset_y = 0

# 初始化Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
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
            if dragging:
                new_pos_x = event.pos[0] - drag_offset_x
                new_pos_y = event.pos[1] - drag_offset_y
                pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
                screen.fill((0, 0, 0))
                x_offset = new_pos_x // TILE_SIZE
                y_offset = new_pos_y // TILE_SIZE
            else:
                tile_x = mouse_x // TILE_SIZE + x_offset
                tile_y = mouse_y // TILE_SIZE + y_offset
                highlighted_tile = (tile_x, tile_y)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左键点击开始拖动
                dragging = True
                drag_offset_x = event.pos[0]
                drag_offset_y = event.pos[1]
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
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左键释放停止拖动
                dragging = False
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
        player_pos, target_pos = move_player_towards_target(player_pos, target_pos, elapsed_time, move_speed)

    noise_tile = get_tile(x_offset, y_offset, WIDTH // TILE_SIZE)
    draw_noise_map(screen, noise_tile, WIDTH // TILE_SIZE, x_offset, y_offset, flash_counter, player_pos, highlighted_tile, clicked_tile, marked_tiles)

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
save_cache()
pygame.quit()
