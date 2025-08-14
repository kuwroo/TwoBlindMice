import pygame
from misc import *

class MapLoader:
    def __init__(self, map_image_path):
        self.map_image = pygame.image.load(map_image_path).convert()
        self.map_rect = self.map_image.get_rect()

    def load_map(self):
        # Placeholder in case you need to expand
        pass

    def draw_map(self, surface, camera_offset):
        surface.blit(self.map_image, (-camera_offset.x, -camera_offset.y))

# Camera class to manage camera offset
class Camera:
    def __init__(self, width, height):
        self.offset = pygame.Vector2(0, 0)
        self.width = width
        self.height = height

    def center_on(self, target_rect):
        self.offset.x = target_rect.centerx - SCREEN_WIDTH // 2
        self.offset.y = target_rect.centery - SCREEN_HEIGHT // 2

camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

