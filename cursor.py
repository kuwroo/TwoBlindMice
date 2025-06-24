import pygame

class Cursor:
    def __init__(self):
        self.image = pygame.image.load("resources/cursor.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (32 * 3, 32 * 3))  # Scale by 3 to match mouse sprite
        self.screen = pygame.display.get_surface()
        self.rect = self.image.get_rect()
        self.is_mouse = True
        pygame.mouse.set_visible(False)  # Hide the system cursor

    def update(self):
        if self.is_mouse:
            pos = pygame.mouse.get_pos()
            self.rect.center = pos
        else:
            pygame.mouse.set_visible(True)  # Show system cursor when custom cursor is disabled

    def draw(self):
        if self.is_mouse:
            self.screen.blit(self.image, self.rect)