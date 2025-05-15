import pygame
from misc import *
from player import *

class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_scene = None

    def change_scene(self, new_scene):
        self.current_scene = new_scene

    def handle_event(self, event):
        if self.current_scene:
            self.current_scene.handle_event(event)

    def update(self):
        if self.current_scene:
            self.current_scene.update()

    def draw(self):
        if self.current_scene:
            self.current_scene.draw()

class StartMenu:
    def __init__(self, screen, scene_manager):
        self.screen = screen
        self.scene_manager = scene_manager
        self.font = pygame.font.Font(None, 64)
        self.text = self.font.render("Press SPACE to Start", True, (255, 255, 255))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.scene_manager.change_scene(IntroScene(self.screen, self.scene_manager))

    def update(self):
        pass

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.text, (SCREEN_WIDTH // 2 - self.text.get_width() // 2, SCREEN_HEIGHT // 2))

class IntroScene:
    def __init__(self, screen, scene_manager):
        self.screen = screen
        self.scene_manager = scene_manager
        self.timer = 0  # For a fake animation duration

    def handle_event(self, event):
        pass

    def update(self):
        self.timer += 1
        if self.timer > 180:  # 3 seconds at 60fps
            self.scene_manager.change_scene(GameplayScene(self.screen, self.scene_manager))

    def draw(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 48)
        text = font.render("Intro Animation Playing...", True, (255, 255, 255))
        self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))

class GameplayScene:
    def __init__(self, screen, scene_manager):
        self.screen = screen
        self.scene_manager = scene_manager
        self.background = pygame.image.load("sprites/background.png").convert()
        self.player = Player((TILE_SIZE * 2, TILE_SIZE * 2))
        self.trash_bin = TrashBin((TILE_SIZE * 11, TILE_SIZE * 8))  # Adjust position

        self.player_group = pygame.sprite.Group(self.player)

    def handle_event(self, event):
        pass  # You can add other interactions later

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update()

        if keys[pygame.K_e]:
            if self.player.rect.colliderect(self.trash_bin.rect):
                print("Quest started from trash bin!")

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        self.screen.blit(self.trash_bin.image, self.trash_bin.rect)
        self.player_group.draw(self.screen)