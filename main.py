import pygame
import sys
from misc import *
from player import *
from quest import *
from dialogue import Dialogue
import pygame_gui
from map_loader import TiledMap


pygame.init()
tiled_map = TiledMap("C:\Users\jacel\Documents\level1_beginning.tmx")  # Replace with your map filename

# --- Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2 Blind Mice")
clock = pygame.time.Clock()
manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT))

# --- Dialogue ---
dialogue = Dialogue(screen, manager)  # Initialize the Dialogue class

# --- Player ---
player = Player(start_pos=(TILE_SIZE * 2, TILE_SIZE * 2))

# --- Trash Bin Setup ---
trash_bin = TrashBin(pos=(TILE_SIZE * 11, TILE_SIZE * 20))  # Placed rightward

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
    time_delta = clock.tick(60) / 1000.0  # Time in seconds since last frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
            # Pass events to pygame_gui
        manager.process_events(event)

    # --- Movement Input ---
    keys = pygame.key.get_pressed()
    player.handle_input(keys)

    # --- Interact with E ---
    if keys[pygame.K_e]:
        if trash_bin.interact(player.rect):
            dialogue.show_dialogue("First Quest Starts!")  # Show dialogue

    # --- Update ---
    dialogue.update(time_delta)  # Update the dialogue box

    # --- Draw ---
    screen.fill((30, 30, 30))  # Clear the screen
    tiled_map.draw(screen)
    all_sprites.draw(screen)
    dialogue.draw()  # Draw the dialogue box
    pygame.display.flip()

pygame.quit()
sys.exit()
