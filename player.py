import pygame
import random
import time
import math
from misc import *


# Contains abstract classes for all sprites (Player, NPC, Cheese, etc.)

import pygame
from misc import TILE_SIZE

class Player(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.image.fill((200, 200, 255))  # Placeholder: light blue square for now
        self.rect = self.image.get_rect(topleft=pos)

        self.direction = pygame.math.Vector2(0, 0)
        self.speed = TILE_SIZE  # Grid-based, move one tile at a time
        self.move_cooldown = 150  # milliseconds
        self.last_move_time = 0

        # Jump-related attributes
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_strength = -10
        self.on_ground = True

    def handle_input(self, keys, current_time):
        if current_time - self.last_move_time < self.move_cooldown:
            return

        self.direction.x = 0

        # Vertical movement (optional, if needed for other mechanics)
        if keys[pygame.K_s]:
            self.direction.y = 1

        # Horizontal movement
        if keys[pygame.K_a]:
            self.direction.x = -1
        elif keys[pygame.K_d]:
            self.direction.x = 1

        # Jump with space bar or W key
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.velocity_y = self.jump_strength
            self.on_ground = False

        if self.direction.length_squared() != 0:
            self.move()
            self.last_move_time = current_time

    def move(self):
        self.rect.x += self.direction.x * self.speed

    def apply_gravity(self):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Simulate ground collision (example: ground at y = 300)
        if self.rect.bottom >= 300:  # Replace 300 with your ground level
            self.rect.bottom = 300
            self.velocity_y = 0
            self.on_ground = True

    def update(self, keys, current_time):
        self.handle_input(keys, current_time)
        self.apply_gravity()

# first quest 
class TrashBin(pygame.sprite.Sprite):
    def __init__(self, pos, size=(32, 64)):
        super().__init__()
        # Make the sprite invisible but interactive
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pos)

    def interact(self, player_rect):
        return self.rect.colliderect(player_rect)