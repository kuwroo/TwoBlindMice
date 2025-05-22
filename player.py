import pygame
import random
import time
import math
from misc import *
from spritesheet_loader import SpriteSheet


# Contains abstract classes for all sprites (Player, NPC, Cheese, etc.)

import pygame
from misc import TILE_SIZE

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # Load the movement spritesheet
        self.movement_sprite_sheet = SpriteSheet("resources/MOUSE.png")
        self.movement_frames = [self.movement_sprite_sheet.get_frame(i, 32, 32) for i in range(8)]

        # Load the idle spritesheet
        self.idle_sprite_sheet = SpriteSheet("resources/IDLE.png")
        self.idle_frames = [self.idle_sprite_sheet.get_frame(i, 32, 32) for i in range(4)]

        # Scale all movement and idle frames to make them larger
        scale_factor = 3  # Adjust this factor as needed
        self.movement_frames = [
            pygame.transform.scale(frame, (frame.get_width() * scale_factor, frame.get_height() * scale_factor))
            for frame in self.movement_frames
        ]
        self.idle_frames = [
            pygame.transform.scale(frame, (frame.get_width() * scale_factor, frame.get_height() * scale_factor))
            for frame in self.idle_frames
        ]

        # Precompute flipped frames
        self.movement_frames_flipped = [
            pygame.transform.flip(frame, True, False) for frame in self.movement_frames
        ]
        self.idle_frames_flipped = [
            pygame.transform.flip(frame, True, False) for frame in self.idle_frames
        ]

        # Animation attributes
        self.current_frames = self.idle_frames  # Start with idle frames
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 1000  # Milliseconds between frames

        # Set initial image and rect
        self.image = self.current_frames[self.current_frame]
        self.rect = self.image.get_rect(topleft=pos)

        # Update the initial image and rect to match the new size
        self.image = pygame.transform.scale(self.image, (self.image.get_width() * scale_factor, self.image.get_height() * scale_factor))
        self.rect = self.image.get_rect(topleft=pos)  # Update the rect to match the new size

        self.direction = pygame.math.Vector2(0, 0)
        self.speed = TILE_SIZE/15  # Grid-based, move one tile at a time
        self.move_cooldown = 50  # milliseconds
        self.last_move_time = 0

        # Jump-related attributes
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_strength = -50
        self.on_ground = True

        # Initialize facing direction
        self.facing_left = False

    def handle_input(self, keys, current_time):
        if current_time - self.last_move_time < self.move_cooldown:
            return

        self.direction.x = 0

# Vertical movement (optional, if needed for other mechanics)
        if keys[pygame.K_s]:
            self.direction.y = 1

        # Horizontal movement
        if keys[pygame.K_a]:
            self.facing_left = True
            self.direction.x = -3
        elif keys[pygame.K_d]:
            self.facing_left = False
            self.direction.x = 3
            
            

        # Jump with space bar or W key
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            print("Jump triggered")  # Debugging
            self.velocity_y = self.jump_strength
            self.on_ground = False

        #Update facing direction
        # if self.direction.x < 0:
        #     self.facing_left = True
        # elif self.direction.x >= 0:
        #     self.facing_left = False

        # Update current frames based on direction without overwriting original frames
        if self.facing_left:
            if self.direction.x == 0:
                self.current_frames = self.idle_frames_flipped  
            else:
                self.current_frames = self.movement_frames_flipped 
        else:
            self.current_frames = self.movement_frames if self.direction.x != 0 else self.idle_frames
    

        if self.direction.length_squared() != 0:
            self.move()
            self.last_move_time = current_time
        else:
            self.set_idle_animation()

      
    def move(self):
        """Move the player based on the current direction."""
        self.rect.x += self.direction.x * self.speed
        self.set_movement_animation()  # Trigger movement animation
        self.animate()  # Update the animation frame

    def set_movement_animation(self):
        """Switch to movement animation frames."""
        if self.current_frames != self.movement_frames:
            self.current_frames = self.movement_frames
            self.current_frame = 0  # Reset to the first frame
        self.animate()  # Revert to previous logic

    def set_idle_animation(self):
        """Switch to idle animation frames."""
        if self.current_frames != self.idle_frames:
            self.current_frames = self.idle_frames
            self.current_frame = 0  # Reset to the first frame
            self.frame_delay = 1000  # Set frame delay for idle animation
        self.animate()  # Update the animation frame

    def animate(self):
        """Update the current frame for animation."""
        self.frame_timer += pygame.time.get_ticks() % 1000  # Revert to previous logic
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.current_frames)
            self.image = self.current_frames[self.current_frame]

    def apply_gravity(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Debugging: Print gravity-related values
        print(f"Velocity Y: {self.velocity_y}, Rect Y: {self.rect.y}, On Ground: {self.on_ground}")

        # Simulate ground collision (example: ground at y = 300)
        if self.rect.bottom >= 250:  # Replace 300 with your ground level
            self.rect.bottom = 250
            self.velocity_y = 0
            self.on_ground = True

    def update(self, keys, current_time):
        self.handle_input(keys, current_time)
        self.apply_gravity()
        self.animate()  # Revert to previous logic

# first quest 
class TrashBin(pygame.sprite.Sprite):
    def __init__(self, pos, size=(32, 64)):
        super().__init__()
        # Make the sprite invisible but interactive
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)

    def interact(self, player_rect):
        return self.rect.colliderect(player_rect)