import pygame
from misc import SCREEN_WIDTH, SCREEN_HEIGHT
from tilemap import TileMap
from player import PlayerMovement
from cursor import Cursor
from visibility import FogOfWar
from quest import play_first_quest, play_second_quest
from button import Button
import pytmx

class TitleScene:
    def __init__(self, screen):
        self.screen = screen
        self.tile_map = TileMap("resources/titleTEST.tmx")
        print("Loaded tilemap, interactables:", self.tile_map.interactables)  # Debug print
        self.is_mouse = True
        self.cursor = Cursor()
        self.player = PlayerMovement(SCREEN_WIDTH, SCREEN_HEIGHT, self.tile_map.width)
        self.camera_offset = pygame.Vector2(0, 0)
        
        # Create buttons
        button_width = 200
        button_height = 50
        # Center the start button
        start_x = (SCREEN_WIDTH - button_width) // 2
        start_y = (SCREEN_HEIGHT - button_height) // 2
        self.start_button = Button(start_x, start_y, button_width, button_height, "Start Mouse")
        
        # Position the game button below the start button
        game_y = start_y + button_height + 20  # 20 pixels padding
        self.game_button = Button(start_x, game_y, button_width, button_height, "Enter Game")
        
        # Door prompt text setup
        self.font = pygame.font.Font(None, 36)
        self.prompt_text = None
        self.near_door = False
        print("TitleScene initialized with door prompt")
        
    def check_door_proximity(self):
        if not self.is_mouse:
            # Get player position in world coordinates
            player_pos = pygame.Rect(
                self.player.player_x,
                self.player.player_y,
                self.player.rect.width,
                self.player.rect.height
            )
            #print(f"Player pos: {player_pos}")
            
            # Check each door
            for obj in self.tile_map.interactables:
                if obj["type"].lower() == "door":
                    door_rect = obj["rect"].inflate(100, 100)  # Expanded interaction zone
                    print(f"Door rect: {door_rect}")
                    if player_pos.colliderect(door_rect):
                        print("Near door - showing prompt")
                        self.prompt_text = self.font.render("Press E to enter", True, (255, 255, 255))
                        self.near_door = True
                        return
            
            # No door nearby
            self.prompt_text = None
            self.near_door = False

    def handle_event(self, event):
        if self.is_mouse:
            # Handle start button click to switch to player mouse
            if self.start_button.handle_event(event):
                print("Start button clicked - switching to mouse control")
                self.cursor.is_mouse = False
                # Set player position to screen center
                self.player.player_x = SCREEN_WIDTH // 2
                self.player.player_y = SCREEN_HEIGHT // 2
                self.player.rect.topleft = (self.player.player_x, self.player.player_y)
                self.is_mouse = False
                return None
        else:
            # Handle door interaction when 'E' is pressed
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e and self.near_door:
                print("Door interaction - switching to game scene!")
                return "SWITCH_TO_GAME"
        return None

    def update(self):
        keys = pygame.key.get_pressed()
        if self.is_mouse:
            self.cursor.update()
            self.start_button.update_position(self.camera_offset)
        else:
            # Update player
            self.player.handle_input(keys)
            self.player.apply_gravity()
            
            # Get floor rectangles and update position
            floor_rects = []
            floor_layer = self.tile_map.tmx_data.get_layer_by_name('floor')
            if isinstance(floor_layer, pytmx.TiledTileLayer):
                for x, y, gid in floor_layer:
                    if gid:  # If there's a tile here
                        floor_rect = pygame.Rect(
                            x * self.tile_map.tmx_data.tilewidth,
                            y * self.tile_map.tmx_data.tileheight,
                            self.tile_map.tmx_data.tilewidth,
                            self.tile_map.tmx_data.tileheight
                        )
                        floor_rects.append(floor_rect)
            
            ladder_rects = []
            ladder_layer = self.tile_map.tmx_data.get_layer_by_name('ladder')
            if isinstance(ladder_layer, pytmx.TiledTileLayer):
                for x, y, gid in ladder_layer:
                    if gid:
                        ladder_rect = pygame.Rect(
                            x * self.tile_map.tmx_data.tilewidth,
                            y * self.tile_map.tmx_data.tileheight,
                            self.tile_map.tmx_data.tilewidth,
                            self.tile_map.tmx_data.tileheight
                        )
                        ladder_rects.append(ladder_rect)
            
            self.player.update_position(floor_rects, ladder_rects)
            self.center_camera_on_player()
            self.player.update_animation(keys)
            
            # Check for door proximity
            self.check_door_proximity()
        
    
                
        
        return None
        
    def center_camera_on_player(self):
        # Center camera on player
        self.camera_offset.x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_offset.y = self.player.rect.centery - SCREEN_HEIGHT // 2
        # Clamp camera to map bounds
        self.camera_offset.x = max(0, min(self.camera_offset.x, self.tile_map.width - SCREEN_WIDTH))
        self.camera_offset.y = max(0, min(self.camera_offset.y, self.tile_map.height - SCREEN_HEIGHT))
        
    def draw(self, screen):
        screen.fill((30, 30, 30))
        self.tile_map.draw(screen, self.camera_offset)
        
        if self.is_mouse:
            self.start_button.draw(screen)
            self.cursor.draw()
        else:
            self.player.draw(screen, pygame.key.get_pressed(), self.camera_offset)
            
            # Draw interaction prompt if it exists
            if self.prompt_text:
                prompt_x = (SCREEN_WIDTH - self.prompt_text.get_width()) // 2
                prompt_y = SCREEN_HEIGHT - 100  # Position prompt near bottom of screen
                screen.blit(self.prompt_text, (prompt_x, prompt_y))
                #print(f"Drawing prompt at ({prompt_x}, {prompt_y})")
            
class GameScene:
    def __init__(self, screen):
        self.screen = screen
        self.tile_map = TileMap("resources/sewermap.tmx")
        self.player = PlayerMovement(SCREEN_WIDTH, SCREEN_HEIGHT, self.tile_map.width)
        # Set initial spawn position higher
        self.player.player_y = SCREEN_HEIGHT // 4
        self.player.rect.topleft = (self.player.player_x, self.player.player_y)
        self.camera_offset = pygame.Vector2(0, 0)
        self.fog = FogOfWar(visibility_radius=150)
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.cheese_count = 1
        self.font = pygame.font.Font(None, 36)
        self.prompt_text = None
        self.near_bin = False
        self.near_hole = False  # Add near_hole attribute
        self.cheese_sprite = pygame.image.load("resources/cheese.png")
        self.cheese_sprite = pygame.transform.scale(self.cheese_sprite, (24, 24))
        self.quest1_completed = False
        self.quest2_completed = False

    def check_bin_proximity(self):
        # Get player position in world coordinates
        player_pos = pygame.Rect(
            self.player.player_x,
            self.player.player_y,
            self.player.rect.width,
            self.player.rect.height
        )
        #print(f"Player pos: {player_pos}")
        
        # Check each bin
        for obj in self.tile_map.interactables:
            if obj["type"].lower() == "bin":
                bin_rect = obj["rect"].inflate(100, 100)  # Expanded interaction zone
                #print(f"Bin rect: {bin_rect}")
                if player_pos.colliderect(bin_rect):
                    #print("Near bin - showing prompt")
                    self.prompt_text = self.font.render("Press E to start quest", True, (255, 255, 255))
                    self.near_bin = True
                    return
        
        # No bin nearby
        self.prompt_text = None
        self.near_bin = False
        
    def check_hole_proximity(self):
        # Get player position in world coordinates
        player_pos = pygame.Rect(
            self.player.player_x,
            self.player.player_y,
            self.player.rect.width,
            self.player.rect.height
        )
        
        # Check each hole
        for obj in self.tile_map.interactables:
            if obj["type"].lower() == "hole":
                hole_rect = obj["rect"].inflate(100, 100)  # Expanded interaction zone
                if player_pos.colliderect(hole_rect):
                    self.prompt_text = self.font.render("Press E to start quest", True, (255, 255, 255))
                    self.near_hole = True
                    return
        
        # Reset if not near any hole
        if not self.near_bin:  # Only reset prompt if we're not near a bin
            self.prompt_text = None
        self.near_hole = False

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if self.near_bin:
                print("Starting first quest!")
                result = play_first_quest()
                print("Quest result:", result)
                if result == "win":
                    if not self.quest1_completed:  # Ensure cheese only increases once
                        self.cheese_count += 1
                    self.quest1_completed = True
            elif self.near_hole:
                print("Starting second quest!")
                result = play_second_quest()
                print("Quest result:", result)
                if result == "win":
                    if not self.quest2_completed:
                        self.cheese_count += 1
                    self.quest2_completed = True
        return None
        
    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.apply_gravity()
        
        # Get floor rectangles from tile layer
        floor_rects = []
        floor_layer = self.tile_map.tmx_data.get_layer_by_name('floor')
        if isinstance(floor_layer, pytmx.TiledTileLayer):
            for x, y, gid in floor_layer:
                if gid:
                    floor_rect = pygame.Rect(
                        x * self.tile_map.tmx_data.tilewidth,
                        y * self.tile_map.tmx_data.tileheight,
                        self.tile_map.tmx_data.tilewidth,
                        self.tile_map.tmx_data.tileheight
                    )
                    floor_rects.append(floor_rect)
        
        self.player.update_position(floor_rects)
        self.center_camera_on_player()
        self.player.update_animation(keys)
        
        # Check for bin and hole proximity
        self.check_bin_proximity()
        self.check_hole_proximity()
        return None
        
    def center_camera_on_player(self):
        # Center camera on player
        self.camera_offset.x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_offset.y = self.player.rect.centery - SCREEN_HEIGHT // 2
        # Clamp camera to map bounds
        self.camera_offset.x = max(0, min(self.camera_offset.x, self.tile_map.width - SCREEN_WIDTH))
        self.camera_offset.y = max(0, min(self.camera_offset.y, self.tile_map.height - SCREEN_HEIGHT))

    def draw(self, screen):
        screen.fill((30, 30, 30))
        self.tile_map.draw(screen, self.camera_offset)
        self.player.draw(screen, pygame.key.get_pressed(), self.camera_offset)
        
        # Draw interaction prompt if it exists
        if self.prompt_text:
            prompt_x = (SCREEN_WIDTH - self.prompt_text.get_width()) // 2
            prompt_y = SCREEN_HEIGHT - 100  # Position prompt near bottom of screen
            screen.blit(self.prompt_text, (prompt_x, prompt_y))
            
        # Draw cheese count
        cheese_x = 10
        cheese_y = 10
        screen.blit(self.cheese_sprite, (cheese_x, cheese_y))
        cheese_text = self.font.render(f"x {self.cheese_count}", True, (255, 255, 255))
        screen.blit(cheese_text, (cheese_x + 30, cheese_y))
        
        # Update and draw fog of war
        self.fog.update((self.player.rect.centerx, self.player.rect.centery), self.camera_offset)
        self.fog.draw(screen)