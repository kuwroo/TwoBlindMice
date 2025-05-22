# Helper functions like fog, collision checks, and managing game state transitions.
import pygame
TILE_SIZE = 64  # or whatever size you're using
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GROUND_HEIGHT = 240

FPS = 60

def draw_cheese_counter(screen, count):
    font = pygame.font.Font(None, 36)
    cheese_icon = pygame.image.load("assets/cheese.png")
    screen.blit(cheese_icon, (20, 20))
    text = font.render(f"x {count}", True, (255, 255, 255))
    screen.blit(text, (60, 25))

