import pygame
import textwrap
from misc import SCREEN_WIDTH, SCREEN_HEIGHT

SCALE = 4

class DialogueView:
    def __init__(self, font_path, raw_text):
        self.font = pygame.font.Font(font_path, 24)
        self.dialogue_boxes = self.parse_dialogue(raw_text)
        self.current_box_index = 0

        self.surface = pygame.image.load("resources/dialogue_box.png").convert_alpha()
        self.surface = pygame.transform.scale(self.surface, (200 * SCALE, 150 * SCALE))

        self.char_delay = 30  # ms between characters
        self.load_text_box(self.dialogue_boxes[self.current_box_index])
        self.can_close = False
        

    def parse_dialogue(self, raw_dialogue, max_chars_per_box=120, max_chars_per_line=50):
        # Step 1: Manually split by new box delimiter first
        raw_boxes = raw_dialogue.split('//')

        text_boxes = []

        for box_text in raw_boxes:
            raw_lines = box_text.replace('/n', '\n').split('\n')
            wrapped_lines = []
            for line in raw_lines:
                wrapped = textwrap.wrap(line.strip(), width=max_chars_per_line)
                wrapped_lines.extend(wrapped)

            # Optional: auto split further if too many chars in one box
            current_box = []
            current_length = 0
            for line in wrapped_lines:
                line_length = len(line)
                if current_length + line_length > max_chars_per_box and current_box:
                    text_boxes.append(current_box)
                    current_box = [line]
                    current_length = line_length
                else:
                    current_box.append(line)
                    current_length += line_length

            if current_box:
                text_boxes.append(current_box)

        return text_boxes


    def load_text_box(self, lines):
        self.current_text_box = lines
        self.visible_text = []
        self.char_index = 0
        self.line_index = 0
        self.last_char_time = pygame.time.get_ticks()
        self.typing = True

    def skip_typing(self):
        self.visible_text = self.current_text_box[:]
        self.typing = False


    def next_box(self):
        if self.current_box_index + 1 < len(self.dialogue_boxes):
            self.current_box_index += 1
            self.load_text_box(self.dialogue_boxes[self.current_box_index])
        else:
            print("End of dialogue.")
            self.typing = False  # Optional: signal that dialogue is finished
            self.can_close = True  # Allow closing the dialogue box
    def handle_input(self, key):
        if key == pygame.K_SPACE:
            if self.typing:
                self.skip_typing()
                return "SKIPPED"
            elif not self.can_close:
                self.next_box()
                return "NEXT_BOX"
        elif key == pygame.K_e:
            if self.can_close:
                return "CLOSE"
        return "NO_ACTION"
    
    

    def update(self):
        if not self.typing:
            return

        now = pygame.time.get_ticks()
        if now - self.last_char_time > self.char_delay:
            self.last_char_time = now
            current_line = self.current_text_box[self.line_index]

            if self.line_index >= len(self.visible_text):
                self.visible_text.append("")

            if self.char_index < len(current_line):
                self.visible_text[self.line_index] += current_line[self.char_index]
                self.char_index += 1
            else:
                if self.line_index + 1 < len(self.current_text_box):
                    self.line_index += 1
                    self.char_index = 0
                else:
                    self.typing = False
                    if self.current_box_index == len(self.dialogue_boxes) - 1:
                        self.can_close = True

    def draw(self, screen):
        x = 0
        y = 30

        screen.blit(self.surface, (x, y))

        # Draw visible lines of text
        for i, line in enumerate(self.visible_text):
            text_surface = self.font.render(line, True, (255, 255, 255))
            screen.blit(text_surface, (80, 430 + i * 40))
            
        
        if not self.typing and not self.can_close:
            # Optional: show "[SPACE] Skip"
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                skip = self.font.render("Press SPACE", True, (255, 255, 255))
                screen.blit(skip, (SCREEN_WIDTH - 230, SCREEN_HEIGHT - 100))
        elif self.can_close:
            # Show "[E] to close"
            if (pygame.time.get_ticks() // 500) % 2 == 0:
                close = self.font.render("Press E", True, (255, 255, 255))
                screen.blit(close, (SCREEN_WIDTH - 200, SCREEN_HEIGHT - 100))



def test_dialogue_view():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Dialogue View Test")
    clock = pygame.time.Clock()

    font_path = "resources/Minecraft.ttf"
    dialogue_text = "Hello, Mouse!/nWelcome to the sewer. This is a very long sentence that should wrap and split over multiple boxes. kjbfkjs dfkjad fjhadsfjahsdfk jaskjfad kjhfakjdhfjkahjfah jkajhkafafd //Press E to continue."

    dialogue_box = DialogueView(font_path, dialogue_text)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if dialogue_box.typing:
                        dialogue_box.skip_typing()
                    elif dialogue_box.visible_text:
                        dialogue_box.next_box()

        screen.fill((50, 50, 50))
        dialogue_box.update()
        dialogue_box.draw(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

test_dialogue_view()