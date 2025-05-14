import pygame
import sys
from scenes import SceneManager
from game_assets import *

pygame.init()

# --- Setup ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2 Blind Mice")
clock = pygame.time.Clock()

# --- Scene Manager --- 
scene_manager = SceneManager(screen)

# --- Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        scene_manager.handle_event(event)  # Handle inputs like key presses
    
    scene_manager.update()  # Update the current scene (intro, gameplay, etc.)
    scene_manager.draw()  # Draw the current scene on the screen
    pygame.display.flip()  # Update display with the new frame
    clock.tick(FPS)  # Control the frame rate

pygame.quit()
sys.exit()
