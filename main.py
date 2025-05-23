import pygame
import sys
from misc import *
from movement import *
from quest import *
# from dialogue import Dialogue  # Commented out for testing
# import pygame_gui  # Commented out for testing
# from maploader import *
from player import *  # Import TrashBin class
from quest import *  # for quests
from tilemap import *



pygame.init()

# --- Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2 Blind Mice")
clock = pygame.time.Clock()

# Initialize MapLoader
# map_loader = MapLoader("sewermap.png")
# map_loader.load_map()
tile_map = TileMap("sewermap.tmx")  # Or the correct TMX filename


# Create Player
player = PlayerMovement(SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_HEIGHT)

# Sprite Groups 
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Cheese Count
cheese_count = 1

# Quest State 
e_pressed_last_frame = False

# Camera Offset 
camera_offset = pygame.Vector2(0, 0)
def center_camera_on_player(player_rect):
    camera_offset.x = player.rect.x - SCREEN_WIDTH // 2
    camera_offset.y = player.rect.y - SCREEN_HEIGHT // 2

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
    # --- Movement Input ---
    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.apply_gravity()
    player.update_position()
    player.update_animation(keys)
    just_pressed_e = keys[pygame.K_e] and not e_pressed_last_frame


    # --- Interact with E ---
    if just_pressed_e:
        for interactable in tile_map.interactables:
            player_rect_map = player.rect.copy()
            player_rect_map.x += camera_offset.x
            player_rect_map.y += camera_offset.y

            if player_rect_map.colliderect(interactable["rect"]):
                print(f"Interacted with: {interactable['name']}")
                if interactable["type"] == "bin":
                    print("First Quest Starts!")
                    result = play_first_quest()
                    print("Quest result:", result)
                    # Re-create the main game window
                    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                    pygame.display.set_caption("2 Blind Mice")
                    
    # Center camera
    center_camera_on_player(player)

    # Draw background and map
    screen.fill((30, 30, 30))
    # map_loader.draw_map(screen, camera_offset)
    tile_map.draw(screen, camera_offset)

    # Draw player
    player.draw(screen, keys)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)
    e_pressed_last_frame = keys[pygame.K_e]



pygame.quit()
sys.exit()
