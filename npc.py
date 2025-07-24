import pygame
from utils import resource_path
from spritesheet_loader import load_spritesheet
from dialogueview import DialogueView


class NPC():
    def __init__(self, x, y, name, dialogue_text):
        print(f"Initializing NPC: {name} at position ({x}, {y})")
        self.rect = pygame.Rect(x, y, 32, 64)  # More reasonable NPC size
        self.name = name
        # Load sprite frames
        sprite_path = f'resources/{name}.png'
        print(f"Loading spritesheet from: {sprite_path}")
        self.sprite_frames = load_spritesheet(f'resources/{name}.png', 4, 32, 32)
        self.sprite_frames = [pygame.transform.scale(frame, (32*4, 32*4)) for frame in self.sprite_frames]
        
        # Animation variables
        self.current_frame = 0
        self.frame_timer = 0
        self.FRAME_DURATION = 100  # milliseconds per frame
        self.idle_frames = self.sprite_frames  # Store idle animation frames
        self.current_animation = self.idle_frames
        
        # Create dialogue box
        font_path = "resources/Minecraft.ttf"
        self.original_dialogue_text = dialogue_text
        self.dialogue = DialogueView(font_path, self.original_dialogue_text)
        self.showing_dialogue = False

    def update(self, current_time):
        # Update animation frame
        if current_time - self.frame_timer > self.FRAME_DURATION:
            self.frame_timer = current_time
            self.current_frame = (self.current_frame + 1) % len(self.current_animation)

        # Update dialogue
        if self.showing_dialogue:
            self.dialogue.update()



    def draw(self, screen, camera_offset):
        # Draw NPC sprite using current animation frame
        screen_x = self.rect.x - camera_offset.x
        screen_y = self.rect.y - camera_offset.y
        current_sprite = self.current_animation[self.current_frame]
        screen.blit(current_sprite, (screen_x, screen_y))

        # Draw dialogue if active
        if self.showing_dialogue:
            self.dialogue.draw(screen)

    def interact(self):
        """Always restart dialogue when interacting"""
        font_path = "resources/Minecraft.ttf"
        self.dialogue = DialogueView(font_path, self.original_dialogue_text)
        self.showing_dialogue = True
        
            

    def is_near_player(self, player_rect, interaction_distance=100):
        """Check if player is within interaction distance"""
        return self.rect.inflate(interaction_distance, interaction_distance).colliderect(player_rect)


