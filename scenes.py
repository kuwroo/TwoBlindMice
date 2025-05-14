import pygame
from game_assets import *

class Scene:
    def __init__(self, screen):
        self.screen = screen
    
    def handle_event(self, event):
        pass
    
    def update(self):
        pass
    
    def draw(self):
        pass

class StartMenu(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        self.font = pygame.font.Font(None, 48)
        self.title_text = self.font.render("2 Blind Mice", True, (255, 255, 255))
        self.start_text = self.font.render("Press Enter to Start", True, (255, 255, 255))
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:  # Player presses Enter to start game
                self.start_game()

    def start_game(self):
        # Transition to Intro Scene (you can replace this with your animation file)
        scene_manager.change_scene(IntroScene(self.screen))  # Scene transition

    def update(self):
        pass

    def draw(self):
        self.screen.fill((0, 0, 0))  # Fill screen with black
        self.screen.blit(self.title_text, (SCREEN_WIDTH // 2 - self.title_text.get_width() // 2, 100))
        self.screen.blit(self.start_text, (SCREEN_WIDTH // 2 - self.start_text.get_width() // 2, 300))


class IntroScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        self.animation_completed = False  # Flag to track if animation is finished
    
    def handle_event(self, event):
        pass  # No events during the intro animation

    def update(self):
        if not self.animation_completed:
            self.play_intro_animation()  # Play the animation
        else:
            # Transition to gameplay after animation
            scene_manager.change_scene(GameplayScene(self.screen))  # Scene transition to gameplay

    def play_intro_animation(self):
        # Here you will add your animation code or call external files (as per your design)
        # This could call functions from an external file (e.g., intro_animation.py)
        pass

    def draw(self):
        # Draw animation or the loading screen
        if not self.animation_completed:
            # Here you can display a placeholder while the animation is running
            self.screen.fill((0, 0, 0))
            font = pygame.font.Font(None, 36)
            text = font.render("Loading Intro Animation...", True, (255, 255, 255))
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
        else:
            # Once animation is complete, the game proceeds to gameplay
            pass


class GameplayScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        # Initialize the gameplay elements like player, environment, etc.
    
    def handle_event(self, event):
        # Handle player input during gameplay
        pass
    
    def update(self):
        # Update game elements like player movement, physics, etc.
        pass
    
    def draw(self):
        self.screen.fill((0, 0, 0))  # Black background for gameplay
        # Draw gameplay elements like the player, environment, etc.
        pass


class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_scene = StartMenu(screen)  # Set initial scene to Start Menu
    
    def change_scene(self, new_scene):
        self.current_scene = new_scene  # Change to the new scene
    
    def handle_event(self, event):
        self.current_scene.handle_event(event)
    
    def update(self):
        self.current_scene.update()
    
    def draw(self):
        self.current_scene.draw()
