import pygame

class Inventory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.items = []

    def add_item(self, item):
        if len(self.items) < self.capacity:
            self.items.append(item)
            return True
        return False

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            return True
        return False

    def draw_inventory(self, screen, x, y, width, height):
        pygame.draw.rect(screen, (50, 50, 50), (x, y, width, height))
        pygame.draw.rect(screen, (0, 0, 0), (x, y, width, height), 2)
        
        font = pygame.font.Font(None, 36)
        y_offset = y + 10
        for item in self.items:
            item_text = font.render(item, True, (255, 255, 255))
            screen.blit(item_text, (x + 10, y_offset))
            y_offset += 40
