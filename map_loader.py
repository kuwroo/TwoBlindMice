import pygame
from pytmx.util_pygame import load_pygame

class TiledMap:
    def __init__(self, filename):
        self.tmx_data = load_pygame(filename)
        self.tilewidth = self.tmx_data.tilewidth
        self.tileheight = self.tmx_data.tileheight
        self.width = self.tmx_data.width * self.tilewidth
        self.height = self.tmx_data.height * self.tileheight

    def draw(self, surface):
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):  # Only draw tile layers
                for x, y, gid in layer.tiles():
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(tile, (x * self.tilewidth, y * self.tileheight))
