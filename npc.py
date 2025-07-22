import pygame
from utils import resource_path
from spritesheet_loader import load_spritesheet
from dialogueview import DialogueView


class NPC():
    def __init__(self, x, y, name, dialogue_text):
        self.rect = pygame.Rect(x, y, 32, 64)  # More reasonable NPC size
        self.name = name
        # Load sprite frames
        self.sprite_frames = load_spritesheet(f'resources/{name}.png', 4, 32, 32)
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_delay = 200  # Milliseconds between frame changes

        # Create dialogue box
        font_path = "resources/Minecraft.ttf"
        self.dialogue = DialogueView(font_path, dialogue_text)
        self.showing_dialogue = False

    def update(self, current_time):
        # Animate NPC
        if current_time - self.animation_timer > self.animation_delay:
            self.current_frame = (self.current_frame + 1) % len(self.sprite_frames)
            self.animation_timer = current_time

    def draw(self, screen, camera_offset):
        # Draw NPC sprite
        screen_x = self.rect.x - camera_offset.x
        screen_y = self.rect.y - camera_offset.y
        screen.blit(self.sprite_frames[self.current_frame], (screen_x, screen_y))

        # Draw dialogue if active
        if self.showing_dialogue:
            self.dialogue.draw(screen)

    def interact(self):
        """Toggle dialogue when interacting with NPC"""
        self.showing_dialogue = not self.showing_dialogue

    def is_near_player(self, player_rect, interaction_distance=100):
        """Check if player is within interaction distance"""
        return self.rect.inflate(interaction_distance, interaction_distance).colliderect(player_rect)

