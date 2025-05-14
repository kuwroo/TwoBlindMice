# store sprite classes eg. mouse, cheese, NPC, enemy
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

BLACK = (0, 0, 0)

import pygame

class Mouse:
    def __init__(self, x, y):
        # Initialize the mouse's position, size, and color
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.color = (255, 255, 0)  # Yellow color for the mouse
        self.speed = 5

    def update(self):
        # Update mouse position based on key presses
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.x += self.speed
        if keys[pygame.K_UP]:
            self.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.y += self.speed

    def draw(self, screen):
        # Draw the mouse as a rectangle (could be replaced with sprite later)
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
