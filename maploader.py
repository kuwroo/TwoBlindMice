import pygame

class MapLoader:
    def __init__(self, map_path):
        self.map_path = map_path
        self.background = None

    def load_map(self):
        """Load the map background image."""
        self.background = pygame.image.load(self.map_path).convert()

    def draw_map(self, screen):
        """Draw the map background onto the screen."""
        if self.background:
            screen.blit(self.background, (0, 0))

