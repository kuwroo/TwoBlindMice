import pygame
vec = pygame.math.Vector2
from misc import SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    def __init__(self, player, tilemap_width, tilemap_height):
        self.player = player
        self.offset = vec(0, 0)
        self.DISPLAY_W, self.DISPLAY_H = SCREEN_WIDTH, SCREEN_HEIGHT
        #woirld bounds
        self.world_bounds = {
            'left': 0,
            'right': tilemap_width,
            'top': 0,
            'bottom': tilemap_height
        }

    def scroll(self):
        # Horizontal follow
        target_x = self.player.rect.centerx - self.DISPLAY_W // 2
        self.offset.x += (target_x - self.offset.x) * 0.1
        self.offset.x = max(self.world_bounds['left'],
                            min(self.offset.x,
                                self.world_bounds['right'] - self.DISPLAY_W))

        # Only scroll vertically if the map is taller than the screen
        if self.world_bounds['bottom'] > self.DISPLAY_H:
            target_y = self.player.rect.centery - self.DISPLAY_H // 2
            self.offset.y += (target_y - self.offset.y) * 0.1
            self.offset.y = max(self.world_bounds['top'],
                                min(self.offset.y,
                                    self.world_bounds['bottom'] - self.DISPLAY_H))
        else:
            self.offset.y = 0

        return self.offset









