
import pygame
from tilemap import resource_path
from spritesheet_loader import load_spritesheet


class NPC():
    def __init__(self, x, y, name):
        self.rect = pygame.Rect(x, y, 100, 100)
        self.name = name
        self.sprite_frames = self.load_spritesheet('resources/'+ 'name' + ''.png', 4, 32, 32)
        self.sprite_rect = self.sprite.get_rect(center=self.rect.center)
        self.is_hovered = False
        
    def interact():
        
        