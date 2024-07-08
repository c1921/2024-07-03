import pygame
import time
from map import get_tile, draw_noise_map, highlighted_tile, clicked_tile, marked_tiles, save_cache, target_pos, is_tile_passable, generate_passability_map
from config import WIDTH, HEIGHT, TILE_SIZE, real_time_per_game_hour
from astar import astar

flash_counter = 0

# Player position
player_pos = [0, 0]

# Game time
game_time = 0
last_time = time.time()
paused = False

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('Infinite Noise Map')

clock = pygame.time.Clock()

x_offset, y_offset = 0, 0
running = True
menu_active = False
menu_rect = None
menu_options = []

path = []

def handle_events():
    global running, menu_active, menu_rect, menu_options, paused, highlighted_tile, target_pos, path, x_offset, y_offset, player_pos
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEMOTION:
            handle_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            handle_mouse_button_down(event)
        elif event.type == pygame.KEYDOWN:
            handle_key_down(event)

def handle_mouse_motion(event):
    global highlighted_tile
    mouse_x, mouse_y = event.pos
    if not menu_active:
        tile_x = mouse_x // TILE_SIZE + x_offset
        tile_y = mouse_y // TILE_SIZE + y_offset
        highlighted_tile = (tile_x, tile_y)

def handle_mouse_button_down(event):
    global menu_active, menu_rect, menu_options, target_pos, path, clicked_tile, player_pos, x_offset, y_offset
    
    if event.button == 3 and not menu_active:
        mouse_x, mouse_y = event.pos
        tile_x = mouse_x // TILE_SIZE + x_offset
        tile_y = mouse_y // TILE_SIZE + y_offset
        menu_rect = pygame.Rect(mouse_x, mouse_y, 100, 60)
        menu_options = [(tile_x, tile_y)]
        menu_active = True
    elif menu_active and menu_rect.collidepoint(event.pos):
        mouse_x, mouse_y = event.pos
        if mouse_y < menu_rect.y + 30:
            marked_tiles.append(menu_options[0])
        else:
            target_pos = menu_options[0]
            noise_tile = get_tile(x_offset, y_offset, WIDTH // TILE_SIZE)
            passability_map = generate_passability_map(noise_tile, WIDTH // TILE_SIZE)
            path = astar(passability_map, (int(player_pos[0] - x_offset), int(player_pos[1] - y_offset)), (int(target_pos[0] - x_offset), (int(target_pos[1] - y_offset))))
        menu_active = False
    else:
        menu_active = False

def handle_key_down(event):
    global paused
    if event.key == pygame.K_SPACE:
        paused = not paused

def handle_key_presses():
    global x_offset, y_offset
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        y_offset -= 1
    if keys[pygame.K_s]:
        y_offset += 1
    if keys[pygame.K_a]:
        x_offset -= 1
    if keys[pygame.K_d]:
        x_offset += 1

def update_game_time():
    global game_time, last_time, path, player_pos
    if not paused:
        current_time = time.time()
        elapsed_time = current_time - last_time
        game_time += elapsed_time / real_time_per_game_hour
        last_time = current_time
        if path:
            next_step = path.pop(0)
            player_pos = [next_step[0] + x_offset, next_step[1] + y_offset]

def draw_ui():
    font = pygame.font.Font(None, 36)
    time_text = font.render(f'Time: {int(game_time)}h', True, (255, 255, 255))
    screen.blit(time_text, (10, 10))
    
    if paused:
        pause_text = font.render('Paused', True, (255, 0, 0))
        screen.blit(pause_text, (WIDTH - 100, 10))
    
    coord_font = pygame.font.Font(None, 28)
    player_coord_text = coord_font.render(f'Player: ({player_pos[0]:.1f}, {player_pos[1]:.1f})', True, (255, 255, 255))
    mouse_coord_text = coord_font.render(f'Mouse: {highlighted_tile}', True, (255, 255, 255))
    screen.blit(player_coord_text, (10, HEIGHT - 30))
    screen.blit(mouse_coord_text, (WIDTH - 200, HEIGHT - 30))

def draw_menu():
    if menu_active:
        pygame.draw.rect(screen, (200, 200, 200), menu_rect)
        pygame.draw.rect(screen, (0, 0, 0), menu_rect, 2)
        font = pygame.font.Font(None, 24)
        mark_text = font.render('Mark', True, (0, 0, 0))
        move_text = font.render('Move', True, (0, 0, 0))
        screen.blit(mark_text, (menu_rect.x + 10, menu_rect.y + 10))
        screen.blit(move_text, (menu_rect.x + 10, menu_rect.y + 40))

while running:
    handle_events()
    handle_key_presses()
    update_game_time()

    noise_tile = get_tile(x_offset, y_offset, WIDTH // TILE_SIZE)
    draw_noise_map(screen, noise_tile, WIDTH // TILE_SIZE, x_offset, y_offset, flash_counter, player_pos, highlighted_tile, clicked_tile, marked_tiles, target_pos)

    draw_ui()
    draw_menu()

    pygame.display.flip()
    clock.tick(30)
    flash_counter += 1

save_cache()
pygame.quit()
