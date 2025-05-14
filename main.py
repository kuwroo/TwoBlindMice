# entry point to game - game logic 
from sprites import *
from misc import *
import pygame
import sys

pygame.init()

# Set the screen dimensions
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("2 Blind Mice")

# Game clock (for controlling the frame rate)
clock = pygame.time.Clock()

def game_loop():
    running = True
    mouse = Mouse(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Create a Mouse object

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle player movement
        mouse.update()

        # Fill the screen with black (darkness)
        screen.fill(BLACK)

        # Draw the mouse on the screen
        mouse.draw(screen)

        # Update the display
        pygame.display.update()

        # Control the frame rate
        clock.tick(60)

    pygame.quit()
    sys.exit()

# Start the game loop
if __name__ == "__main__":
    game_loop()
