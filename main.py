import pygame
import sys
from misc import *
from player import *
from quest import *

pygame.init()

# --- Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2 Blind Mice")
clock = pygame.time.Clock()

# --- Player ---
player = Player(start_pos=(TILE_SIZE * 2, TILE_SIZE * 2))

# --- Trash Bin Setup ---
trash_bin = TrashBin(pos=(TILE_SIZE * 6, TILE_SIZE * 2))  # Placed rightward

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
    screen.fill((30, 30, 30))  # Dark background for now

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Movement Input ---
    keys = pygame.key.get_pressed()
    player.handle_input(keys)

    # --- Interact with E ---
    if keys[pygame.K_e]:
        if trash_bin.interact(player.rect):
            print("First Quest Starts!")  # Replace with quest logic later

    # --- Draw ---
    all_sprites.draw(screen)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
