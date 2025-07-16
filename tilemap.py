# tilemap.py
import pygame
import pytmx
from npc import NPC
from utils import resource_path

class TileMap:
    def __init__(self, filename):
        self.tmx_data = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = self.tmx_data.width * self.tmx_data.tilewidth
        self.height = self.tmx_data.height * self.tmx_data.tileheight
        self.interactables = self.load_interactables()
        self.font = pygame.font.SysFont(None, 24)  # Create a font for text drawing
        # Pre-load commonly used rectangles
        self.floor_rects = self.get_floor_rectangles()
        self.ladder_rects = self.get_ladder_rectangles()
        self.npcs = self.load_npcs()

    def load_interactables(self):
        interactables = []
        for obj in self.tmx_data.objects:
            if obj.type:  # Only include objects with a type
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                
                # Access properties as a dictionary
                props = obj.properties if hasattr(obj, "properties") else {}

                # Extract text content from 'Text' or 'text' property
                text_value = props.get("Text") or props.get("text")

                # Also convert properties into a list of dicts if you still need that
                properties_list = [{"name": k, "value": v} for k, v in props.items()]

                interactables.append({
                    "rect": rect,
                    "type": obj.type,
                    "name": obj.name,
                    "properties": properties_list,
                    "text": text_value 
                })
        return interactables


    def load_npcs(self):
        """Load NPCs from the map's object layer."""
        npcs = []
        print("\nLoading NPCs from tilemap...")
        for obj in self.tmx_data.objects:
            print(f"Found object: type={getattr(obj, 'type', 'None')}, name={getattr(obj, 'name', 'None')}")
            if obj.type == "NPC":
                name = getattr(obj, 'name', 'default_npc')
                dialogue = getattr(obj, 'properties', {}).get('dialogue', 'Hello!')
                
                print(f"Creating NPC: {name} with dialogue: {dialogue}")
                npc = NPC(obj.x, obj.y, name, dialogue)
                npcs.append(npc)
        print(f"Loaded {len(npcs)} NPCs\n")
        return npcs

    def draw(self, surface, camera_offset):
        # Draw tile layers
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
        
        # Draw NPCs
        current_time = pygame.time.get_ticks()
        for npc in self.npcs:
            npc.update(current_time)
            npc.draw(surface, camera_offset)
    
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

    def get_floor_rectangles(self):
        """Get floor rectangles from tile layer."""
        floor_rects = []
        try:
            floor_layer = self.tmx_data.get_layer_by_name('floor')
        except ValueError:
            return floor_rects
            
        if isinstance(floor_layer, pytmx.TiledTileLayer):
            for x, y, gid in floor_layer:
                if gid:  # If there's a tile here
                    floor_rect = pygame.Rect(
                        x * self.tmx_data.tilewidth,
                        y * self.tmx_data.tileheight,
                        self.tmx_data.tilewidth,
                        self.tmx_data.tileheight
                    )
                    floor_rects.append(floor_rect)
        return floor_rects

    def get_ladder_rectangles(self):
        """Get ladder rectangles from tile layer."""
        ladder_rects = []
        try:
            ladder_layer = self.tmx_data.get_layer_by_name('ladder')
        except:
            return ladder_rects
        else:
            if isinstance(ladder_layer, pytmx.TiledTileLayer):
                for x, y, gid in ladder_layer:
                    if gid:
                        ladder_rect = pygame.Rect(
                            x * self.tmx_data.tilewidth,
                            y * self.tmx_data.tileheight,
                            self.tmx_data.tilewidth,
                            self.tmx_data.tileheight
                        )
                        ladder_rects.append(ladder_rect)
        return ladder_rects

