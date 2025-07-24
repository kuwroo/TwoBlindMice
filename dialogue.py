import pygame
import pygame_gui

class Dialogue:
    def __init__(self, screen, manager, font_size=24, box_color=(0, 0, 0), text_color=(255, 255, 255)):
        self.screen = screen
        self.manager = manager
        self.font_size = font_size
        self.box_color = box_color
        self.text_color = text_color

        # Calculate position for the dialogue box at the bottom of the screen
        screen_width, screen_height = self.screen.get_size()
        box_width = screen_width - 100  # Leave some padding on the sides
        box_height = 150  # Fixed height for the dialogue box
        box_x = 50  # Centered horizontally with padding
        box_y = screen_height - box_height - 20  # Positioned at the bottom with padding

        # Dialogue box UI element
        self.dialogue_box = pygame_gui.elements.UITextBox(
            html_text="",
            relative_rect=pygame.Rect((box_x, box_y), (box_width, box_height)),
            manager=self.manager,
            object_id="#dialogue_box"
        )
        self.dialogue_box.hide()  # Initially hidden

    def show_dialogue(self, text):
        """Display the dialogue box with the given text."""
        self.dialogue_box.set_text(text)
        self.dialogue_box.show()

    def hide_dialogue(self):
        """Hide the dialogue box."""
        self.dialogue_box.hide()

    def update(self, time_delta):
        """Update the dialogue box (required for pygame_gui)."""
        self.manager.update(time_delta)

    def draw(self):
        """Draw the dialogue box (required for pygame_gui)."""
        self.manager.draw_ui(self.screen)

