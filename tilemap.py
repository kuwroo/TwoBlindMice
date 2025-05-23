# tilemap.py
import pygame
import pytmx

class TileMap:
    def __init__(self, filename):
        self.tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        self.interactables = self.load_interactables()

    def load_interactables(self):
        interactables = []
        for obj in self.tmx_data.objects:
            print(f"Found object: {obj.name} {obj.type}")
            if obj.type == "bin":  # Make sure this matches Type in Tiled
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                interactables.append({
                    "rect": rect,
                    "type": obj.type,
                    "name": obj.name
                })
        print("Loaded interactables:", interactables)
        return interactables

    def draw(self, surface, camera_offset):
        for layer in self.tmx_data.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        surface.blit(
                            tile,
                            (x * self.tmx_data.tilewidth - camera_offset.x,
                             y * self.tmx_data.tileheight - camera_offset.y)
                        )
