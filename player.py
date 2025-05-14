import pygame
import random
import time
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Contains abstract classes for all sprites (Player, NPC, Cheese, etc.)

class Player:
    def __init__(self, screen):
        self.screen = screen
        self.x, self.y = 100, 100  # Starting position
        self.speed = 5  # Movement speed
        self.inventory = []
        self.is_interacting = False  # Interaction state

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_s]:
            self.y += self.speed
        if keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_d]:
            self.x += self.speed

        # Check interaction (press E)
        if pygame.key.get_pressed()[pygame.K_e]:
            self.is_interacting = True
        else:
            self.is_interacting = False

    def draw(self):
        pygame.draw.rect(self.screen, (255, 255, 255), (self.x, self.y, 32, 32))  # Placeholder for player

    def add_to_inventory(self, item):
        self.inventory.append(item)


class SnakeNPC:
    def __init__(self, screen):
        self.screen = screen
        self.x, self.y = 400, 300  # Position of the snake
        self.radius = 50  # Interaction radius
        self.challenge_active = False
        self.challenge_sequence = []
        self.player_input = []
        self.start_time = 0
        self.time_limit = 3  # 3 seconds to complete rhythm

    def is_interacting_with(self, player):
        # Check if the player is close enough to interact with the snake
        return abs(player.x - self.x) < self.radius and abs(player.y - self.y) < self.radius

    def challenge_player(self, player):
        if not self.challenge_active:
            # Start the challenge if not already active
            self.start_challenge()

        if self.challenge_active:
            # Collect player input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player_input.append("LEFT")
            elif keys[pygame.K_RIGHT]:
                self.player_input.append("RIGHT")
            elif keys[pygame.K_UP]:
                self.player_input.append("UP")
            elif keys[pygame.K_DOWN]:
                self.player_input.append("DOWN")

            # Check if the player completed the sequence or time ran out
            if time.time() - self.start_time > self.time_limit:
                self.end_challenge(False)  # Time ran out, challenge failed

            # If the player has finished their input
            if len(self.player_input) == len(self.challenge_sequence):
                self.check_input(player)

    def start_challenge(self):
        self.challenge_active = True
        self.challenge_sequence = [random.choice(["LEFT", "RIGHT", "UP", "DOWN"]) for _ in range(3)]  # 3 arrow keys in sequence
        self.player_input = []
        self.start_time = time.time()  # Start the timer

        print("Rhythm Challenge started! Press the keys in sequence.")

    def check_input(self, player):
        if self.player_input == self.challenge_sequence:
            print("Success! You matched the rhythm.")
            player.add_to_inventory('Cheese')  # Give cheese to the player
            self.end_challenge(True)
        else:
            print("You failed! Try again.")
            self.end_challenge(False)

    def end_challenge(self, success):
        self.challenge_active = False
        if success:
            print("You won the rhythm game and earned cheese!")
        else:
            print("Challenge failed! Better luck next time.")

        # Reset player input for the next challenge
        self.player_input = []

    def draw(self):
        pygame.draw.circle(self.screen, (0, 255, 0), (self.x, self.y), self.radius)  # Snake (just a circle)