import pygame
from misc import *
from player import *

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
        # ... init player, cheese count, world
        self.trash_bin = TrashBin((tile_x, tile_y))
        self.cheese_count = 1

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update()

        if keys[pygame.K_e]:
            if self.player.rect.colliderect(self.trash_bin.rect):
                self.start_quest()

    def draw(self):
        screen.fill((0, 0, 0))
        self.player_group.draw(screen)
        screen.blit(self.trash_bin.image, self.trash_bin.rect)
        draw_cheese_counter(screen, self.cheese_count)

    def start_quest(self):
        print("Quest started! Find the second cheese...")
        # Trigger a scene/dialogue/quest marker/etc.
