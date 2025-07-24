import pygame
class SpriteSheet:
    def __init__(self, filename):
        self.spritesheet = pygame.image.load(filename).convert_alpha()

    def get_frame(self, frame, width, height, scale=1):
        """Extract a single frame from the spritesheet."""
        x = frame * width  # Calculate x position based on frame index
        y = 0  # Single row, so y is always 0
        frame_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        frame_surface.blit(self.spritesheet, (0, 0), (x, y, width, height))
        if scale != 1:
            frame_surface = pygame.transform.scale(frame_surface, (width * scale, height * scale))
        return frame_surface
    
