import pygame
from utils import resource_path

class SpriteSheet:
    def __init__(self, filename):
        """Initialize spritesheet with a filename."""
        try:
            self.spritesheet = pygame.image.load(resource_path(filename)).convert_alpha()
        except pygame.error as e:
            print(f"Couldn't load spritesheet: {filename}")
            print(f"Error: {e}")
            # Create an empty surface as fallback
            self.spritesheet = pygame.Surface((32, 32), pygame.SRCALPHA)

    def get_frame(self, frame, width, height, scale=1):
        """Extract a single frame from the spritesheet."""
        x = frame * width
        y = 0  # Single row spritesheets only
        frame_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        frame_surface.blit(self.spritesheet, (0, 0), (x, y, width, height))
        
        if scale != 1:
            frame_surface = pygame.transform.scale(frame_surface, 
                                                (int(width * scale), 
                                                 int(height * scale)))
        return frame_surface

    def get_all_frames(self, frame_count, frame_width, frame_height, scale=1):
        """Get all frames from the spritesheet."""
        frames = []
        for i in range(frame_count):
            frame = self.get_frame(i, frame_width, frame_height, scale)
            frames.append(frame)
        return frames

def load_spritesheet(filename, frame_count, frame_width, frame_height, scale=1):
    """Helper function to quickly load all frames from a spritesheet."""
    sheet = SpriteSheet(filename)
    return sheet.get_all_frames(frame_count, frame_width, frame_height, scale)

