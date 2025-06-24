import pygame
from tilemap import resource_path

class Button:
    def __init__(self, x, y, width, height, text, font_size=36, color=(200, 200, 200), hover_color=(150, 150, 150), text_color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.original_rect = self.rect.copy()  # Store original position
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        
        # Initialize font
        try:
            self.font = pygame.font.Font(None, font_size)  # Use default font
        except pygame.error:
            print("Error loading font, using system default")
            self.font = pygame.font.SysFont(None, font_size)
        
    def update_position(self, camera_offset):
        # Update button position based on camera
        self.rect.x = self.original_rect.x - camera_offset.x
        self.rect.y = self.original_rect.y - camera_offset.y
        
    def draw(self, surface):
        # Draw button background
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2)  # border
        
        # Draw text
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            # Convert mouse position to button space
            self.is_hovered = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                if self.is_hovered:
                    return True
        return False