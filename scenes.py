import pygame
from misc import SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_HEIGHT
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
        self.is_mouse = True
        self.cursor = Cursor()
        self.player = PlayerMovement(SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_HEIGHT, self.tile_map.width)
        self.camera_offset = pygame.Vector2(0, 0)
        
        # Create start button in center of screen
        button_width = 200
        button_height = 50
        button_x = (SCREEN_WIDTH - button_width) // 2
        button_y = (SCREEN_HEIGHT - button_height) // 2
        self.start_button = Button(button_x, button_y, button_width, button_height, "Start Game")
        
    def handle_event(self, event):
        if self.is_mouse:
            # Handle button click to switch to player
            if self.start_button.handle_event(event):
                print("Start button clicked - switching to player control")
                self.is_mouse = False
                self.cursor.is_mouse = False
                # Set player position to center of screen
                self.player.player_x = SCREEN_WIDTH // 2
                self.player.player_y = SCREEN_HEIGHT // 2
                self.player.rect.topleft = (self.player.player_x, self.player.player_y)
                return None  # Don't switch scenes yet
        else:
            # Handle door interaction when 'E' is pressed
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                player_rect_map = self.player.rect.copy()
                player_rect_map.x += self.camera_offset.x
                player_rect_map.y += self.camera_offset.y
                
                for interactable in self.tile_map.interactables:
                    if interactable["type"] == "door":
                        if player_rect_map.colliderect(interactable["rect"]):
                            print("Door reached - switching to game scene!")
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
            
            # Get floor rectangles adjusted for camera position
            floor_rects = []
            for obj in self.tile_map.tmx_data.get_layer_by_name('floor'):
                floor_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                floor_rects.append(floor_rect)
            
            self.player.update_position(floor_rects)
            self.center_camera_on_player()
            self.player.update_animation(keys)
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

class GameScene:
    def __init__(self, screen):
        self.screen = screen
        self.tile_map = TileMap("resources/sewermap.tmx")
        self.player = PlayerMovement(SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_HEIGHT, self.tile_map.width)
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
        
        # Get floor rectangles for collision
        floor_rects = []
        for obj in self.tile_map.tmx_data.get_layer_by_name('floor'):
            floor_rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            floor_rects.append(floor_rect)
        
        self.player.update_position(floor_rects)
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