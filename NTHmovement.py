import pygame
#from camera import Camera  # Import the Camera class

class PlayerMovement(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, ground_height, scale_factor=3):
        super().__init__()  # Initialize the Sprite class
        self.SCREEN_WIDTH = screen_width
        self.SCREEN_HEIGHT = screen_height
        self.GROUND_HEIGHT = ground_height
        self.SCALE_FACTOR = scale_factor

        self.PLAYER_WIDTH = 50
        self.PLAYER_HEIGHT = 50
        self.PLAYER_SPEED = 5
        self.JUMP_POWER = 15
        self.GRAVITY = 1

        self.player_x = self.SCREEN_WIDTH // 2
        self.player_y = self.SCREEN_HEIGHT - self.PLAYER_HEIGHT
        self.player_velocity_x = 0
        self.player_velocity_y = 0
        self.is_jumping = False
        self.on_ground = True
        self.on_ladder = False  # Flag to indicate if the player is on a ladder
        self.at_ladder = False  # Flag to indicate if the player is near a ladder

        self.current_frame = 0
        self.frame_timer = 0
        self.frame_delay = 5
        self.last_direction_left = False

        self.idle_frames = self.load_spritesheet('resources/idle.png', 4, 32, 32)
        self.movement_frames = self.load_spritesheet('resources/MOUSE.png', 8, 32, 32)

        self.idle_frames = [pygame.transform.scale(frame, (self.PLAYER_WIDTH * self.SCALE_FACTOR, self.PLAYER_HEIGHT * self.SCALE_FACTOR)) for frame in self.idle_frames]
        self.movement_frames = [pygame.transform.scale(frame, (self.PLAYER_WIDTH * self.SCALE_FACTOR, self.PLAYER_HEIGHT * self.SCALE_FACTOR)) for frame in self.movement_frames]

        # Set initial image and rect for compatibility with sprite groups
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.rect.topleft = (self.player_x, self.player_y)

       #self.camera = Camera()  # Initialize the Camera class

    def load_spritesheet(self, image_path, frame_count, frame_width, frame_height):
        spritesheet = pygame.image.load(image_path)
        frames = []
        for i in range(frame_count):
            frame = spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frames.append(frame)
        return frames

    def handle_input(self, keys):
        self.player_velocity_x = 0
        if keys[pygame.K_a]:  # Change to 'A' for left
            self.player_velocity_x = -self.PLAYER_SPEED
            self.last_direction_left = True
        if keys[pygame.K_d]:  # Change to 'D' for right
            self.player_velocity_x = self.PLAYER_SPEED
            self.last_direction_left = False

        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:  # Allow both Space and W for jump
            self.player_velocity_y = -self.JUMP_POWER
            self.is_jumping = True
            self.on_ground = False
            
        if  self.at_ladder:
            if keys[pygame.K_w]:
                self.climbing = True  # Set climbing flag
                self.player_velocity_y = -self.PLAYER_SPEED  # Move up the ladder
                self.on_ladder = True  # Set a flag to indicate the player is on a ladder
            else:
                self.climbing = False
                if self.on_ladder:
                    self.player_velocity_y = 0
            
            
            

    def apply_gravity(self):
        if not self.on_ground:
            self.player_velocity_y += self.GRAVITY

    def update_position(self):
        self.player_x += self.player_velocity_x
        self.player_y += self.player_velocity_y

        if self.player_y >= self.SCREEN_HEIGHT - self.PLAYER_HEIGHT - self.GROUND_HEIGHT:
            self.player_y = self.SCREEN_HEIGHT - self.PLAYER_HEIGHT - self.GROUND_HEIGHT
            self.player_velocity_y = 0
            self.on_ground = True
        # Adjust the rect position for the sprite
        self.rect.topleft = (self.player_x, self.player_y)

    def update_animation(self, keys):
        if self.on_ground and not (keys[pygame.K_a] or keys[pygame.K_d]):
            if self.current_frame >= len(self.idle_frames):
                self.current_frame = 0
            self.frame_timer += 1
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.idle_frames)
        else:
            if self.current_frame >= len(self.movement_frames):
                self.current_frame = 0
            self.frame_timer += 1
            if self.frame_timer >= self.frame_delay:
                self.frame_timer = 0
                self.current_frame = (self.current_frame + 1) % len(self.movement_frames)

    def draw(self, screen, keys):
        if self.on_ground and not (keys[pygame.K_a] or keys[pygame.K_d]):
            if self.last_direction_left:
                flipped_idle_frame = pygame.transform.flip(self.idle_frames[self.current_frame], True, False)
                screen.blit(flipped_idle_frame, (self.player_x, self.player_y))
            else:
                screen.blit(self.idle_frames[self.current_frame], (self.player_x, self.player_y))
        else:
            if keys[pygame.K_a]:
                flipped_frame = pygame.transform.flip(self.movement_frames[self.current_frame], True, False)
                screen.blit(flipped_frame, (self.player_x, self.player_y))
            else:
                screen.blit(self.movement_frames[self.current_frame], (self.player_x, self.player_y))