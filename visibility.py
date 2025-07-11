import pygame
from misc import SCREEN_WIDTH, SCREEN_HEIGHT


class FogOfWar:
    def __init__(self):
        self.visibility_radius = 150
        self.fog_light = pygame.image.load("resources/fog.png").convert_alpha()
        self.fog_light = pygame.transform.scale(self.fog_light, (self.visibility_radius * 2, self.visibility_radius * 2))   
        self.fog_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
    def update(self, player_pos, camera_offset):
        # Clear the fog surface
        self.fog_surface.fill((0, 0, 0, 255))  # Semi-transparent black
        
        # Calculate player's position on screen
        screen_x = player_pos[0] - camera_offset.x
        screen_y = player_pos[1] - camera_offset.y
        
        # Draw the fog light around the player (NOT WORKING)
        fog_rect = self.fog_light.get_rect(center=(screen_x, screen_y))
        self.fog_surface.blit(self.fog_light, fog_rect.topleft)
        # Create a circle mask around the player (WORKS FOR NOW)
        layers = 25
        for i in range(layers, 0, -1):
            alpha = int(255 * (i / layers) ** 2)  # quadratic falloff for smoother glow
            radius = int(self.visibility_radius * (i / layers))
            pygame.draw.circle(
                self.fog_surface,
                (0, 0, 0, alpha),  # black with varying alpha
                (int(screen_x), int(screen_y)),
                radius
            )
        
    def draw(self, screen):
        # Draw the fog layer over the game screen
        screen.blit(self.fog_surface, (0, 0))