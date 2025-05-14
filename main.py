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

# Game logic 
def game_loop():
    pass  # Placeholder for game loop logic

if __name__ == "__main__":
    game_loop()