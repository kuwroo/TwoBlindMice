import pygame
import asyncio, sys
from misc import *
# from movement import *
# from dialogue import Dialogue  # Commented out for testing
# import pygame_gui  # Commented out for testing
from player import *  # Import PlayerMovement and Camera class
from quest import *  # for quests
from tilemap import * # for TileMap and resource_path
from visibility import FogOfWar  # Import the new FogOfWar class

pygame.init()

# --- Setup ---
screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], pygame.SRCALPHA, 32)
pygame.display.set_caption("2 Blind Mice")
clock = pygame.time.Clock()

# Load TileMap
tile_map = TileMap(resource_path("resources/sewermap.tmx"))
WORLD_WIDTH = tile_map.width

# Create Player
player = PlayerMovement(SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_HEIGHT, WORLD_WIDTH)

# Create Fog of War
fog = FogOfWar(visibility_radius=150, fog_image_path=resource_path("resources/fog.png"))

# Sprite Groups 
all_sprites = pygame.sprite.Group()
all_sprites.add(player)

# Cheese Count Tracker
cheese_count = 1
quest1_completed = False  # Flag to ensure cheese only increases once
quest2_completed = False  # Initialize quest2_completed
# Load cheese sprite AFTER display is initialized
cheese_sprite = pygame.image.load(resource_path("resources/cheese.png"))
cheese_sprite = pygame.transform.scale(cheese_sprite, (24, 24))

# Quest State 
e_pressed_last_frame = False

# Camera Offset 
camera_offset = pygame.Vector2(0, 0)

# Font for displaying cheese count
font = pygame.font.SysFont(None, 28)

def center_camera_on_player(player):
    camera_offset.x = player.rect.centerx - SCREEN_WIDTH // 2
    camera_offset.y = player.rect.centery - SCREEN_HEIGHT // 2
    camera_offset.x = max(0, min(camera_offset.x, tile_map.width - SCREEN_WIDTH))
    camera_offset.y = max(0, min(camera_offset.y, tile_map.height - SCREEN_HEIGHT))

async def main():
    global e_pressed_last_frame, cheese_count, quest1_completed, quest2_completed, screen  # <-- Added screen here!

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
        center_camera_on_player(player)
        player.update_animation(keys)
        just_pressed_e = keys[pygame.K_e] and not e_pressed_last_frame

        # --- Interact with E ---
        if just_pressed_e:
            for interactable in tile_map.interactables:
                player_rect_map = player.rect.copy()

                if player_rect_map.colliderect(interactable["rect"]):
                    print(f"Interacted with: {interactable['name']}")
                    
                    if interactable["type"] == "Bin":
                        print("First Quest Starts!")
                        result = play_first_quest()
                        print("Quest result:", result)
                        
                        # Only increment cheese count if won AND not already completed
                        if result == "win" and not quest1_completed:
                            cheese_count += 1
                            quest1_completed = True

                        # Re-create the main game window
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                        pygame.display.set_caption("2 Blind Mice")

                    if interactable["type"] == "Hole":
                        print("Second Quest Starts!")
                        result = play_second_quest()
                        print("Quest result:", result)

                        # Only increment cheese count if won AND not already completed
                        if result == "win" and not quest2_completed:
                            cheese_count += 1
                            quest2_completed = True

                        # Re-create the main game window
                        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                        pygame.display.set_caption("2 Blind Mice")

        # Center camera
        center_camera_on_player(player)

        # Draw background and map
        screen.fill((30, 30, 30))
        tile_map.draw(screen, camera_offset)
        tile_map.draw_texts(screen, camera_offset)

        # Draw player
        player.draw(screen, keys, camera_offset)

        # Update and draw fog of war
        fog.update((player.rect.centerx, player.rect.centery), camera_offset)
        fog.draw(screen)

        # Draw cheese count tracker
        screen.blit(cheese_sprite, (10, 10))  # Draw the cheese image
        cheese_count_text = font.render(f"x {cheese_count}", True, (255, 255, 255))  # White count
        screen.blit(cheese_count_text, (40, 10))  # Position next to cheese sprite

        prompt_text = tile_map.get_interaction_prompt(player.rect, camera_offset)
        if prompt_text:
            prompt_surface = tile_map.font.render(prompt_text, True, (255, 255, 255))
            prompt_pos = (SCREEN_WIDTH // 2 - prompt_surface.get_width() // 2, SCREEN_HEIGHT - 50)
            screen.blit(prompt_surface, prompt_pos)



        # Update display
        pygame.display.flip()
        clock.tick(60)
        e_pressed_last_frame = keys[pygame.K_e]

        await asyncio.sleep(0)

asyncio.run(main())
