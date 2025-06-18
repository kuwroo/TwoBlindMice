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
        try:
            self.tmx_data = pytmx.load_pygame(resource_path(filename), pixelalpha=True)
            self.width = self.tmx_data.width * self.tmx_data.tilewidth
            self.height = self.tmx_data.height * self.tmx_data.tileheight
            self.interactables = self.load_interactables()
        except Exception as e:
            print(f"Error loading tilemap {filename}: {e}")
            raise

    def load_interactables(self):
        interactables = []
        try:
            for obj in self.tmx_data.objects:
                # Get the object group name if available
                group_name = getattr(obj.parent, 'name', '').lower()
                # Get the object type if available, fallback to group name
                obj_type = getattr(obj, 'type', group_name)
                
                if obj_type in ["bin", "start", "floor"]:
                    rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                    # Use object type as name if no name is set
                    obj_name = getattr(obj, 'name', obj_type)
                    interactables.append({
                        "rect": rect,
                        "type": obj_type,
                        "name": obj_name
                    })
                    print(f"Added interactable: type={obj_type}, name={obj_name}")
                    
        except Exception as e:
            print(f"Error loading interactables: {e}")
            
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
