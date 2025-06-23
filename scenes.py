import pygame
from misc import SCREEN_WIDTH, SCREEN_HEIGHT
from tilemap import TileMap
from player import PlayerMovement
from cursor import Cursor
from visibility import FogOfWar
from quest import play_first_quest
from button import Button

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
        self.prompt_text = self.font.render("Press E to enter", True, (255, 255, 255))
        self.near_door = False
        print("TitleScene initialized with door prompt")
        
    def check_door_proximity(self):
        if not self.is_mouse:
            # Get player position in world coordinates
            player_world_pos = pygame.Rect(
                self.player.rect.x + self.camera_offset.x,
                self.player.rect.y + self.camera_offset.y,
                self.player.rect.width,
                self.player.rect.height
            )
            
            for interactable in self.tile_map.interactables:
                if interactable["type"] == "door":
                    # Create an expanded interaction zone around the door
                    door_rect = interactable["rect"].inflate(100, 100)  # 50 pixels on each side
                    was_near = self.near_door
                    self.near_door = door_rect.colliderect(player_world_pos)
                    if self.near_door != was_near:
                        print(f"Door proximity changed: {self.near_door}")
                        print(f"Player pos: {player_world_pos}")
                        print(f"Door rect: {door_rect}")
                    return
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
            # Player movement and physics
            self.player.handle_input(keys)
            self.player.apply_gravity()
            
            # Get floor rectangles in world coordinates
            floor_rects = []
            for obj in self.tile_map.tmx_data.get_layer_by_name('floor'):
                floor_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                floor_rects.append(floor_rect)
            
            self.player.update_position(floor_rects)
            self.center_camera_on_player()
            self.player.update_animation(keys)
            
            # Check if player is near the door
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
            
            # Draw door prompt if near door
            if self.near_door:
                print("Drawing door prompt")  # Debug print
                prompt_x = (SCREEN_WIDTH - self.prompt_text.get_width()) // 2
                prompt_y = SCREEN_HEIGHT - 100  # Position prompt near bottom of screen
                screen.blit(self.prompt_text, (prompt_x, prompt_y))

class GameScene:
    def __init__(self, screen):
        self.screen = screen
        self.tile_map = TileMap("resources/sewermap.tmx")
        self.player = PlayerMovement(SCREEN_WIDTH, SCREEN_HEIGHT, self.tile_map.width)
        self.camera_offset = pygame.Vector2(0, 0)
        self.fog = FogOfWar(visibility_radius=150)
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.cheese_count = 1
        self.e_pressed_last_frame = False
        
    def center_camera_on_player(self):
        self.camera_offset.x = self.player.rect.centerx - SCREEN_WIDTH // 2
        self.camera_offset.y = self.player.rect.centery - SCREEN_HEIGHT // 2
        self.camera_offset.x = max(0, min(self.camera_offset.x, self.tile_map.width - SCREEN_WIDTH))
        self.camera_offset.y = max(0, min(self.camera_offset.y, self.tile_map.height - SCREEN_HEIGHT))
        
    def handle_event(self, event):
        # Handle any pygame events for the game scene
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                player_rect_map = self.player.rect.copy()
                player_rect_map.x += self.camera_offset.x
                player_rect_map.y += self.camera_offset.y
                
                for interactable in self.tile_map.interactables:
                    if player_rect_map.colliderect(interactable["rect"]):
                        print(f"Interacted with: {interactable['name']}")
                        if interactable["type"] == "Bin":
                            print("First Quest Starts!")
                            result = play_first_quest()
                            print("Quest result:", result)
        return None
        
    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.apply_gravity()
        self.player.update_position()
        self.center_camera_on_player()
        self.player.update_animation(keys)
        return None
        
    def draw(self, screen):
        screen.fill((30, 30, 30))
        self.tile_map.draw(screen, self.camera_offset)
        self.player.draw(screen, pygame.key.get_pressed(), self.camera_offset)
        
        # Update and draw fog of war
        self.fog.update((self.player.rect.centerx, self.player.rect.centery), self.camera_offset)
        self.fog.draw(screen)