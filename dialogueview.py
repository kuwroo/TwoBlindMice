import pygame
from misc import SCREEN_WIDTH, SCREEN_HEIGHT

#make dialogue box myself, show with bg?
SCALE = 4
class DialogueView:
    def __init__(self, font_path, text):
        self.font = pygame.font.Font(font_path, 20)
        self.text = text
        self.surface = pygame.image.load("resources/dialogue_box.png").convert_alpha()
        self.surface = pygame.transform.scale(self.surface, (200 * SCALE, 150 * SCALE))
        self.render_text()

    def render_text(self):
        lines = self.text.split('\n')
        y_offset = 400  # Padding from the top
        for line in lines:
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.surface.blit(text_surface, (75, y_offset))  # Padding from the left
            y_offset += text_surface.get_height() + 5 * SCALE  # Line spacing

    def draw(self, screen):
        screen.blit(self.surface, (SCREEN_WIDTH // 2 - self.surface.get_width() // 2,
                                   SCREEN_HEIGHT - self.surface.get_height() + 2 * SCALE))
                                 
        
import pygame
from dialogueview import DialogueView
from misc import SCREEN_WIDTH, SCREEN_HEIGHT

def test_dialogue_view():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dialogue View Test")
    clock = pygame.time.Clock()

    # Load a font
    font = pygame.font.Font(None, 36)

    # Create a DialogueView instance
    font_path = "resources/Minecraft.ttf"  # Replace with your font path
    dialogue_text = "Hello, Mouse!\nWelcome to the sewer.\nPress E to continue."
    dialogue_box = DialogueView(font_path, dialogue_text)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill((50, 50, 50))

        # Draw the dialogue box
        dialogue_box.draw(screen)

        # Update the display
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    test_dialogue_view()