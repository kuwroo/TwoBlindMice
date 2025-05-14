import pygame
SCREEN_WIDTH = 480
SCREEN_HEIGHT = 600

BLACK = (0, 0, 0)

class Mouse:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.color = (255, 255, 0)
        self.speed = 5
        self.collected_cheese = 0

    def update(self):
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
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

    def collect_cheese(self, cheese):
        if (self.x < cheese.x + cheese.size and
            self.x + self.width > cheese.x and
            self.y < cheese.y + cheese.size and
            self.y + self.height > cheese.y):
            self.collected_cheese += 1
            cheese.collected = True  # Mark cheese as collected

class Cheese:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 30  # Cheese size
        self.color = (255, 255, 255)  # White cheese color
        self.collected = False  # Flag to track if cheese is collected

    def draw(self, screen):
        if not self.collected:
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)
