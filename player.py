import pygame
from misc import *
from spritesheet_loader import load_spritesheet


class PlayerMovement(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, map_width):
        super().__init__() 

        # Initialize the Sprite class
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.TILE_SIZE = 32
        self.MAP_WIDTH_IN_TILES = MAP_WIDTH_IN_TILES  # Or pass this from outside
        self.WORLD_WIDTH = map_width  


        # Player details 
        self.PLAYER_WIDTH = 50
        self.PLAYER_HEIGHT = 50
        self.PLAYER_SPEED = 5
        self.JUMP_POWER = 15
        self.CLIMB_SPEED = 4

        # Physics constants
        self.GRAVITY = 0.5
        self.TERMINAL_VELOCITY = 10
        self.is_jumping = False
        self.on_ground = False
        self.at_ladder = False  # Flag to indicate if the player is near a ladder
        self.on_ladder = False  # Flag to indicate if the player is on a ladder
        self.climbing = False
        self.allow_attack = False  # default = no attacking
        self.is_attacking = False

        # Initial player position and velocity
        self.player_x = 300
        self.player_y = screen_height // 2  # Start in middle of screen, will fall to floor
        self.player_velocity_x = 0
        self.player_velocity_y = 0
        self.can_move = True

        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 5
        self.last_direction_left = False
        
        # Load and scale animation frames
        self.idle_frames = self.load_spritesheet('resources/idle.png', 4, 32, 32)
        self.movement_frames = self.load_spritesheet('resources/MOUSE.png', 8, 32, 32)
        self.climbing_frames = self.load_spritesheet('resources/CLIMB.png', 8, 32, 32)
        # Ensure current_frame is within bounds of both animations
        self.idle_frame_count = len(self.idle_frames)
        self.movement_frame_count = len(self.movement_frames)
        self.climbing_frame_count = len(self.climbing_frames)
        
        self.idle_frames = [pygame.transform.scale(frame, (self.PLAYER_WIDTH * 3, self.PLAYER_HEIGHT * 3)) for frame in self.idle_frames]
        self.movement_frames = [pygame.transform.scale(frame, (self.PLAYER_WIDTH * 3, self.PLAYER_HEIGHT * 3)) for frame in self.movement_frames]
        self.climbing_frames = [pygame.transform.scale(frame, (self.PLAYER_WIDTH * 3, self.PLAYER_HEIGHT * 3)) for frame in self.climbing_frames]
        
        # Set initial image and rect
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.player_x, self.player_y)

       #self.camera = Camera()  # Initialize the Camera class

        # Collision box size (smaller than sprite)
        self.COLLISION_WIDTH = self.PLAYER_WIDTH * 1.5  # Make hitbox 2/3 of sprite width
        self.COLLISION_HEIGHT = self.PLAYER_HEIGHT * 1.5  # Make hitbox 2/3 of sprite height


    def handle_input(self, keys):
        self.player_velocity_x = 0
        if keys[pygame.K_a] and self.player_x > self.PLAYER_SPEED:  # Change to 'A' for left
            self.player_velocity_x = -self.PLAYER_SPEED
            self.last_direction_left = True
        if keys[pygame.K_d] and self.player_x < self.WORLD_WIDTH - self.PLAYER_WIDTH - self.PLAYER_SPEED:  # Change to 'D' for right
            self.player_velocity_x = self.PLAYER_SPEED
            self.last_direction_left = False

        if keys[pygame.K_SPACE] and self.on_ground or keys[pygame.K_w] and self.on_ground:  # Allow both Space and W for jump
            self.player_velocity_y = -self.JUMP_POWER
            self.is_jumping = True
            self.on_ground = False
        
        if self.allow_attack:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:  # Allow shift key for attack  # Allow shift key for attack
                self.is_attacking = True
        else:
            self.is_attacking = False
    # Ladder movement
        if self.at_ladder:
            self.is_jumping = False
            if keys[pygame.K_w]:
                self.climbing = True
                self.player_velocity_y = -self.CLIMB_SPEED
                self.on_ladder = True
            elif self.on_ground and keys[pygame.K_s]:
                self.climbing = False
                self.on_ladder = False
                self.player_velocity_y = 0
            elif keys[pygame.K_s] and not self.on_ground:  # Only allow climbing down if not on ground
                self.climbing = True
                self.player_velocity_y = self.CLIMB_SPEED
                self.on_ladder = True
            else:
                if self.on_ladder:
                    self.player_velocity_y = 0
        else:
            self.climbing = False
            self.on_ladder = False
            
        
            

    def apply_gravity(self):
        if not self.on_ground and not self.on_ladder:
            self.player_velocity_y = min(self.player_velocity_y + self.GRAVITY, self.TERMINAL_VELOCITY)

    def check_floor_collision(self, floor_rects):
        next_y = self.player_y + self.player_velocity_y
        # Center the collision box within the sprite
        collision_x = self.player_x + (self.PLAYER_WIDTH * 3 - self.COLLISION_WIDTH) // 2
        collision_y = next_y + (self.PLAYER_HEIGHT * 3 - self.COLLISION_HEIGHT) // 2
        
        player_rect = pygame.Rect(
            collision_x,
            collision_y,
            self.COLLISION_WIDTH,
            self.COLLISION_HEIGHT
        )
        self.on_ground = False
        
        for floor in floor_rects:
            if player_rect.colliderect(floor):
                if self.player_velocity_y > 0:  # Moving down
                    # Align bottom of collision box with floor top
                    self.player_y = floor.top - self.COLLISION_HEIGHT - (self.PLAYER_HEIGHT * 3 - self.COLLISION_HEIGHT) // 2
                    self.player_velocity_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                    return True
                elif self.player_velocity_y < 0:  # Moving up
                    self.player_y = floor.bottom - (self.PLAYER_HEIGHT * 3 - self.COLLISION_HEIGHT) // 2
                    self.player_velocity_y = 0
                    return True
        return False

    def check_wall_collision(self, floor_rects):
        # Create collision rect at next horizontal position with smaller hitbox
        next_x = self.player_x + self.player_velocity_x
        # Center the collision box within the sprite
        collision_x = next_x + (self.PLAYER_WIDTH * 3 - self.COLLISION_WIDTH) // 2
        collision_y = self.player_y + (self.PLAYER_HEIGHT * 3 - self.COLLISION_HEIGHT) // 2
        
        player_rect = pygame.Rect(
            collision_x,
            collision_y,
            self.COLLISION_WIDTH,
            self.COLLISION_HEIGHT
        )
        
        for floor in floor_rects:
            if player_rect.colliderect(floor):
                if self.player_velocity_x > 0:  # Moving right
                    self.player_x = floor.left - (self.PLAYER_WIDTH * 3) + (self.PLAYER_WIDTH * 3 - self.COLLISION_WIDTH) // 2
                    return True
                elif self.player_velocity_x < 0:  # Moving left
                    self.player_x = floor.right - (self.PLAYER_WIDTH * 3 - self.COLLISION_WIDTH) // 2
                    return True
        return False
    
    def check_ladder_collision(self, ladder_rects):
        """Check if player is touching a ladder"""
        collision_rect = pygame.Rect(
            self.player_x + (self.PLAYER_WIDTH * 3 - self.COLLISION_WIDTH) // 2,
            self.player_y + (self.PLAYER_HEIGHT * 3 - self.COLLISION_HEIGHT) // 2,
            self.COLLISION_WIDTH,
            self.COLLISION_HEIGHT
        )
        
        self.at_ladder = False
        for ladder in ladder_rects:
            if collision_rect.colliderect(ladder) and not self.on_ground:
                self.at_ladder = True
                return True
        return False

    def update_position(self, floor_rects, ladder_rects):
        if not self.can_move:
            self.player_velocity_x = 0
            self.player_velocity_y = 0
        # Check ladder collision first
        self.check_ladder_collision(ladder_rects)
        if self.on_ladder:
            # If on ladder, only move vertically
            self.player_y += self.player_velocity_y
        
        # Check and handle wall collisions first
        if not self.check_wall_collision(floor_rects):
            self.player_x += self.player_velocity_x
        
        # Apply gravity and check floor collisions
        if not self.check_floor_collision(floor_rects):
            self.on_ground = False
            self.player_y += self.player_velocity_y
        # Update sprite rect position
        self.rect.topleft = (self.player_x, self.player_y)
        
    
    
    def get_air_sprite(self):
        def map_value(value, from_min, from_max, to_min, to_max):
            if from_max - from_min == 0:
                return to_min
            return ((value - from_min) / (from_max - from_min)) * (to_max - to_min) + to_min

        def clamp(value, min_val, max_val):
            return max(min_val, min(value, max_val))
        
        if not self.jumping_frames:
            return 0

        max_index = len(self.jumping_frames) - 1
        mapped = map_value(self.player_velocity_y, -self.JUMP_POWER, self.JUMP_POWER, 0, max_index)
        return int(clamp(mapped, 0, max_index))

    def update_animation(self, keys):
        # Check if we should use idle animation
        is_idle = self.player_velocity_x == 0 and not self.on_ladder and not self.is_jumping

        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            if is_idle:
                self.current_frame = (self.current_frame + 1) % self.idle_frame_count
            elif self.on_ladder:
                self.current_frame = (self.current_frame + 1) % self.climbing_frame_count
            else:
                self.current_frame = (self.current_frame + 1) % self.movement_frame_count
        
    def draw(self, screen, keys, camera_offset):
        draw_x = self.player_x - camera_offset.x
        draw_y = self.player_y - camera_offset.y  # Added 32 pixels (1 tile height) to move sprite down
        
        # Check if we should use idle animation
        is_idle = self.player_velocity_x == 0 and not self.on_ladder
        
        
        if is_idle:
            frame_index = self.current_frame % self.idle_frame_count
            frame = self.idle_frames[frame_index]
            if self.last_direction_left:
                frame = pygame.transform.flip(frame, True, False)
        elif self.on_ladder:
            frame_index = self.current_frame % self.climbing_frame_count
            frame = self.climbing_frames[frame_index]    
        else:
            frame_index = self.current_frame % self.movement_frame_count
            frame = self.movement_frames[frame_index]
            if self.player_velocity_x < 0:  # Moving left
                frame = pygame.transform.flip(frame, True, False)
            elif self.player_velocity_x == 0 and self.last_direction_left:
                frame = pygame.transform.flip(frame, True, False)
        
        # Center the sprite horizontally at draw position
        sprite_rect = frame.get_rect()
        sprite_rect.midbottom = (
            draw_x + (self.PLAYER_WIDTH * 1.5),  # Center horizontally
            draw_y + (self.PLAYER_HEIGHT * 3)    # Bottom aligned with collision point
        )
        screen.blit(frame, sprite_rect)


