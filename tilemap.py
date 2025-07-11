# tilemap.py
import pygame
import pytmx

import os
import sys

def resource_path(relative_path):
    # Get the absolute path to a resource, works for dev and for PyInstaller
    try:
        base_path = sys._MEIPASS  # When running as .exe
    except Exception:
        base_path = os.path.abspath(".")  # When running as script

    return os.path.join(base_path, relative_path)


class TileMap:
    def __init__(self, filename):
        self.tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        self.interactables = self.load_interactables()
        self.font = pygame.font.SysFont(None, 24)  # Create a font for text drawing

    def load_interactables(self):
        interactables = []
        for obj in self.tmx_data.objects:
            print(f"Found object: {obj.name} {obj.type}")
            if obj.type:  # Only include objects with a type
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                interactables.append({
                    "rect": rect,
                    "type": obj.type,
                    "name": obj.name
                })

        #print("Loaded interactables:", interactables)
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
    
    def draw_texts(self, surface, camera_offset):
        for obj in self.tmx_data.objects:
            if hasattr(obj, 'text') and obj.text:
                # Render the text
                text_surface = self.font.render(obj.text, True, (255, 255, 255))
                # Position adjusted by camera offset, slightly above the object's position
                x = obj.x - camera_offset.x
                y = obj.y - camera_offset.y - text_surface.get_height()
                surface.blit(text_surface, (x, y))
                
    def get_interaction_prompt(self, player_rect):
        # Adjust player rect to world coordinates (if needed, or expect player_rect already in world coords)
        # Here, assume player_rect is in world coords (no offset)
        for interactable in self.interactables:
            # Inflate interactable rect a bit for easier detection
            interact_rect = interactable["rect"].inflate(50, 50)  # Increased detection range
            if player_rect.colliderect(interact_rect):
                # You can customize prompt text here by type or name
                if interactable["type"].lower() == "bin":
                    return "Press E to start first quest!"
                elif interactable["type"].lower() == "hole":
                    return "Press E to start second quest!"
                elif interactable["type"].lower() == "door":
                    return "Press E to enter"
                else:
                    return "Press E to interact!"
        return ""  # no prompt if no nearby interactable

