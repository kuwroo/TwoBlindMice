import pygame
vec = pygame.math.Vector2
from misc import SCREEN_WIDTH, SCREEN_HEIGHT
from abc import ABC, abstractmethod
from movement import PlayerMovement

class Camera:
    def __init__(self, player):
        self.player = player
        self.offset = (0,0)
        self.offset_float = vec(0,0)
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
     
    def setmethod(self, method):
        """Set the camera movement method."""
        self.method = method
    
    def scroll(self):
        self.method.scroll()
        # Constant for camera movement sensitivity
class Camscroll(ABC):
    def __init__(self, camera, player):
        self.camera = camera
        self.player = player
        
    @abstractmethod
    def scroll(self):
        """Abstract method to be implemented by subclasses."""
        pass

class Follow(Camscroll):
    def __init__(self, camera, player):
        super().__init__(camera, player)

    def scroll(self):
        if self.player_x < SCREEN_WIDTH * 0.25:
            self.camera.offset_float.x = (self.camera.offset_float.x - self.player.speed) % self.camera.screen_width
        elif self.player_x > SCREEN_WIDTH * 0.75:
            self.camera.offset_float.x = (self.camera.offset_float.x + self.player.speed) % self.camera.screen_width
        if self.player_y < SCREEN_HEIGHT * 0.25:
            self.camera.offset_float.y = (self.camera.offset_float.y - self.player.speed) % self.camera.screen_height
        elif self.player_y > SCREEN_HEIGHT * 0.75:
            self.camera.offset_float.y = (self.camera.offset_float.y + self.player.speed) % self.camera.screen_height
        # Convert to integer for pixel offset
        self.camera.offset = (int(self.camera.offset_float.x), int(self.camera.offset_float.y))
      
class Border(Camscroll):
    def __init__(self, camera, player):
        super().__init__(camera, player)
    
    def scroll(self):
        if self.player_x < SCREEN_WIDTH * 0.25:
            self.camera.offset_float.x = (self.camera.offset_float.x - self.player.speed) % self.camera.screen_width
        elif self.player_x > SCREEN_WIDTH * 0.75:
            self.camera.offset_float.x = (self.camera.offset_float.x + self.player.speed) % self.camera.screen_width
        if self.player_y < SCREEN_HEIGHT * 0.25:
            self.camera.offset_float.y = (self.camera.offset_float.y - self.player.speed) % self.camera.screen_height
        elif self.player_y > SCREEN_HEIGHT * 0.75:
            self.camera.offset_float.y = (self.camera.offset_float.y + self.player.speed) % self.camera.screen_height
        # Convert to integer for pixel offset
        self.camera.offset = (int(self.camera.offset_float.x), int(self.camera.offset_float.y))
  
  
  
    
    def update_camera(self, player_x, player_y, player_velocity_x, player_velocity_y, screen_width, screen_height):
        """Update the camera to follow the player when near the screen edge."""
        screen_scroll_x = 0
        screen_scroll_y = 0

        # Horizontal camera movement
        if player_x < screen_width * 0.25:
            screen_scroll_x = player_velocity_x
        elif player_x > screen_width * 0.75:
            screen_scroll_x = player_velocity_x

        # Vertical camera movement (if needed)
        if player_y < screen_height * 0.25:
            screen_scroll_y = player_velocity_y
        elif player_y > screen_height * 0.75:
            screen_scroll_y = player_velocity_y

        # Update camera offsets
        self.offset_x += screen_scroll_x
        self.offset_y += screen_scroll_y

        # Return the scroll values for use in other parts of the game
        return screen_scroll_x, screen_scroll_y
    
    def scroll(self, player_x, player_y, screen_width, screen_height):
        """Scroll the camera to follow the player when near the screen edge."""
        if player_x < screen_width * 0.25:
            self.offset_x = player_x - screen_width * 0.25
        elif player_x > screen_width * 0.75:
            self.offset_x = player_x - screen_width * 0.75

        if player_y < screen_height * 0.25:
            self.offset_y = player_y - screen_height * 0.25
        elif player_y > screen_height * 0.75:
            self.offset_y = player_y - screen_height * 0.75