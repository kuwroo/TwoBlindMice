import pygame
import sys
from misc import *
from movement import *
from quest import *
# from dialogue import Dialogue  # Commented out for testing
# import pygame_gui  # Commented out for testing
from maploader import MapLoader
from player import TrashBin  # Import TrashBin class


pygame.init()

# --- Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2 Blind Mice")
clock = pygame.time.Clock()
# manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))  # Commented out for testing


# Initialize MapLoader
map_loader = MapLoader("sewermap.png")
map_loader.load_map()

# Create an instance of PlayerMovement
player = PlayerMovement(SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_HEIGHT)

# --- Trash Bin Setup ---
trash_bin = TrashBin((TILE_SIZE * 11, TILE_SIZE * 20))  # Placed rightward

# --- Sprite Groups ---
all_sprites = pygame.sprite.Group()
interactables = pygame.sprite.Group()

all_sprites.add(player)
all_sprites.add(trash_bin)
interactables.add(trash_bin)

# --- Cheese Count ---
cheese_count = 1

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Pass events to pygame_gui
        # manager.process_events(event)  # Commented out for testing

    # --- Movement Input ---
    keys = pygame.key.get_pressed()
    player.handle_input(keys)
    player.apply_gravity()
    player.update_position()
    player.update_animation(keys)

    # --- Interact with E ---
    if keys[pygame.K_e]:
        if trash_bin.interact(player.rect):
            print("First Quest Starts!")  # Placeholder for dialogue

    # --- Update ---
    # dialogue.update(time_delta)  # Update the dialogue box  # Commented out for testing

    # --- Draw ---
    screen.fill((30, 30, 30))  # Clear the screen
    map_loader.draw_map(screen)  # Draw the map background
    all_#sprites.draw(screen)
    
    # Draw player
    player.draw(screen, keys)
    # dialogue.draw()  # Draw the dialogue box  # Commented out for testing

        # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)


pygame.quit()
sys.exit()
