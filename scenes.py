import pygame
from misc import SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_HEIGHT
from tilemap import TileMap
from player import PlayerMovement
from cursor import Cursor
from visibility import FogOfWar
from quest import play_first_quest

class TitleScene:
    def __init__(self, screen):
        self.screen = screen
        self.tile_map = TileMap("resources/titleTEST.tmx")
        self.is_mouse = True
        self.cursor = Cursor()
        self.player = PlayerMovement(SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_HEIGHT, self.tile_map.width)
        self.camera_offset = pygame.Vector2(0, 0)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.is_mouse:
            mouse_pos = pygame.mouse.get_pos()
            # Convert mouse position to world coordinates
            mouse_pos_world = (
                mouse_pos[0] + self.camera_offset.x,
                mouse_pos[1] + self.camera_offset.y
            )
            
            # Check each interactable
            for interactable in self.tile_map.interactables:
                if interactable.get("type") == "start":
                    if interactable["rect"].collidepoint(mouse_pos_world):
                        print("Clicked start area!")  # Debug print
                        self.is_mouse = False
                        self.cursor.is_mouse = False
                        # Set player position to clicked position
                        self.player.player_x = mouse_pos[0]  # Screen coordinates
                        self.player.player_y = mouse_pos[1]
                        self.player.rect.topleft = (self.player.player_x, self.player.player_y)
                        return "SWITCH_TO_GAME"
        return None

    def update(self):
        if self.is_mouse:
            self.cursor.update()
        else:
            self.player.handle_input(pygame.key.get_pressed())
            self.player.update()
        return None
        
    def draw(self, screen):
        screen.fill((30, 30, 30))
        self.tile_map.draw(screen, self.camera_offset)
        
        if not self.is_mouse:
            self.player.draw(screen, pygame.key.get_pressed(), self.camera_offset)
        
        if self.is_mouse:
            self.cursor.draw()

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
        
    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.apply_gravity()
        self.player.update_position()
        self.center_camera_on_player()
        self.player.update_animation(keys)
        
        # Quest interaction logic
        just_pressed_e = keys[pygame.K_e] and not self.e_pressed_last_frame
        if just_pressed_e:
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
        
        self.e_pressed_last_frame = keys[pygame.K_e]
        return None
        
    def draw(self, screen):
        screen.fill((30, 30, 30))
        self.tile_map.draw(screen, self.camera_offset)
        self.player.draw(screen, pygame.key.get_pressed(), self.camera_offset)
        
        # Update and draw fog of war
        self.fog.update((self.player.rect.centerx, self.player.rect.centery), self.camera_offset)
        self.fog.draw(screen)