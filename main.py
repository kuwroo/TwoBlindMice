import pygame
import asyncio
from scenes import *
from scene_manager import SceneManager
from misc import SCREEN_WIDTH, SCREEN_HEIGHT
import pickle
import os

class GlobalSettings:
    def __init__(self):
        self.volume = 0.7
        self.music_volume = 0.5
        self.sfx_volume = 0.8
        self.controls = {
            'move_left': pygame.K_a,
            'move_right': pygame.K_d,
            'jump': pygame.K_SPACE,
            'attack': pygame.K_LSHIFT,
            'pause': pygame.K_ESCAPE
        }
        self.graphics = {
            'fullscreen': False,
            'vsync': True
        }
        self.save_file = "savegame.dat"
        
    def save_settings(self):
        try:
            with open("settings.dat", "wb") as f:
                pickle.dump({
                    'volume': self.volume,
                    'music_volume': self.music_volume,
                    'sfx_volume': self.sfx_volume,
                    'controls': self.controls,
                    'graphics': self.graphics
                }, f)
        except Exception as e:
            print(f"Failed to save settings: {e}")
    
    def load_settings(self):
        try:
            with open("settings.dat", "rb") as f:
                data = pickle.load(f)
                self.volume = data.get('volume', 0.7)
                self.music_volume = data.get('music_volume', 0.5)
                self.sfx_volume = data.get('sfx_volume', 0.8)
                self.controls = data.get('controls', self.controls)
                self.graphics = data.get('graphics', self.graphics)
        except Exception as e:
            print(f"Failed to load settings: {e}")
    
    def save_game(self, game_data):
        try:
            with open(self.save_file, "wb") as f:
                pickle.dump(game_data, f)
        except Exception as e:
            print(f"Failed to save game: {e}")
    
    def restart_game(self):
        """Restart the game by resetting settings and clearing all save files."""
        # Reset settings to defaults
        self.volume = 0.7
        self.music_volume = 0.5
        self.sfx_volume = 0.8
        self.controls = {
            'move_left': pygame.K_a,
            'move_right': pygame.K_d,
            'jump': pygame.K_SPACE,
            'attack': pygame.K_LSHIFT,
            'pause': pygame.K_ESCAPE
        }
        self.graphics = {
            'fullscreen': False,
            'vsync': True
        }
        
        # Clear all save files
        save_files = ["savegame.dat", "savegame.sav", "settings.dat"]
        for file in save_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"Deleted save file: {file}")
                except Exception as e:
                    print(f"Failed to delete {file}: {e}")
        
        print("Game restarted and all save files cleared.")
    
    def load_game(self):
        try:
            with open(self.save_file, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Failed to load game: {e}")
            return None

class GlobalSettingsMenu:
    def __init__(self, settings):
        self.settings = settings
        self.active = False
        self.current_tab = "Audio"
        self.tabs = ["Audio", "Controls", "Graphics", "Save/Load"]
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and self.active == True:
                self.active = False
                return "CLOSE_SETTINGS"
            elif event.key == pygame.K_TAB:
                # Cycle through tabs
                current_index = self.tabs.index(self.current_tab)
                self.current_tab = self.tabs[(current_index + 1) % len(self.tabs)]
            elif event.key == pygame.K_s and self.current_tab == "Save/Load":
                self.settings.save_settings()
            elif event.key == pygame.K_x and self.current_tab == "Save/Load":
                self.active = False
                return "RESTART_GAME"
        return None
    
    def draw(self, screen):
        if not self.active:
            return
            
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Menu background
        menu_width = 600
        menu_height = 400
        menu_x = (SCREEN_WIDTH - menu_width) // 2
        menu_y = (SCREEN_HEIGHT - menu_height) // 2
        
        pygame.draw.rect(screen, (50, 50, 50), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(screen, (100, 100, 100), (menu_x, menu_y, menu_width, menu_height), 3)
        
        # Title
        title_text = self.font.render("GLOBAL SETTINGS", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, menu_y + 30))
        screen.blit(title_text, title_rect)
        
        # Tabs
        tab_width = 120
        for i, tab in enumerate(self.tabs):
            tab_x = menu_x + 20 + i * (tab_width + 10)
            tab_y = menu_y + 70
            color = (150, 150, 150) if tab == self.current_tab else (100, 100, 100)
            pygame.draw.rect(screen, color, (tab_x, tab_y, tab_width, 30))
            tab_text = self.small_font.render(tab, True, (255, 255, 255))
            tab_rect = tab_text.get_rect(center=(tab_x + tab_width//2, tab_y + 15))
            screen.blit(tab_text, tab_rect)
        
        # Content based on current tab
        content_x = menu_x + 20
        content_y = menu_y + 120
        content_width = menu_width - 40
        
        if self.current_tab == "Audio":
            self.draw_audio_tab(screen, content_x, content_y, content_width)
        elif self.current_tab == "Controls":
            self.draw_controls_tab(screen, content_x, content_y, content_width)
        elif self.current_tab == "Graphics":
            self.draw_graphics_tab(screen, content_x, content_y, content_width)
        elif self.current_tab == "Save/Load":
            self.draw_save_load_tab(screen, content_x, content_y, content_width)
        
        # Instructions
        instructions = [
            "TAB: Switch tabs",
            "ESC: Close settings",
            "S: Save settings (in Save/Load tab)"
        ]
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, (200, 200, 200))
            screen.blit(text, (content_x, menu_y + menu_height - 60 + i * 20))
    
    def draw_audio_tab(self, screen, x, y, width):
        # Volume sliders
        labels = ["Master Volume", "Music Volume", "SFX Volume"]
        values = [self.settings.volume, self.settings.music_volume, self.settings.sfx_volume]
        
        for i, (label, value) in enumerate(zip(labels, values)):
            label_text = self.small_font.render(f"{label}: {int(value * 100)}%", True, (255, 255, 255))
            screen.blit(label_text, (x, y + i * 40))
            
            # Simple slider representation
            slider_width = 200
            slider_height = 10
            slider_x = x + 250
            slider_y = y + i * 40 + 5
            
            pygame.draw.rect(screen, (100, 100, 100), (slider_x, slider_y, slider_width, slider_height))
            pygame.draw.rect(screen, (0, 255, 0), (slider_x, slider_y, slider_width * value, slider_height))
    
    def draw_controls_tab(self, screen, x, y, width):
        controls = [
            ("Move Left", pygame.key.name(self.settings.controls['move_left']).upper()),
            ("Move Right", pygame.key.name(self.settings.controls['move_right']).upper()),
            ("Jump", pygame.key.name(self.settings.controls['jump']).upper()),
            ("Attack", pygame.key.name(self.settings.controls['attack']).upper()),
            ("Pause", pygame.key.name(self.settings.controls['pause']).upper())
        ]
        
        for i, (action, key) in enumerate(controls):
            action_text = self.small_font.render(f"{action}:", True, (255, 255, 255))
            key_text = self.small_font.render(key, True, (0, 255, 0))
            screen.blit(action_text, (x, y + i * 30))
            screen.blit(key_text, (x + 200, y + i * 30))
    
    def draw_graphics_tab(self, screen, x, y, width):
        options = [
            ("Fullscreen", self.settings.graphics['fullscreen']),
            ("VSync", self.settings.graphics['vsync'])
        ]
        
        for i, (option, value) in enumerate(options):
            option_text = self.small_font.render(f"{option}:", True, (255, 255, 255))
            value_text = self.small_font.render("ON" if value else "OFF", True, (0, 255, 0) if value else (255, 0, 0))
            screen.blit(option_text, (x, y + i * 30))
            screen.blit(value_text, (x + 200, y + i * 30))
    
    def draw_save_load_tab(self, screen, x, y, width):
        options = [
            "Press S to Save Settings",
            "Press L to Load Settings",
            "Press G to Save Game",
            "Press R to Load Game",
            "Press X to Restart Game"
        ]
        
        for i, option in enumerate(options):
            text = self.small_font.render(option, True, (255, 255, 255))
            screen.blit(text, (x, y + i * 30))

async def main():
    pygame.init()
    screen = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT], pygame.SRCALPHA, 32)
    pygame.display.set_caption("2 Blind Mice")
    clock = pygame.time.Clock()
    
    # Initialize global settings
    global_settings = GlobalSettings()
    global_settings.load_settings()
    
    # Create global settings menu
    settings_menu = GlobalSettingsMenu(global_settings)
    
    # Create scene manager and start with title scene
    scene_manager = SceneManager()
    title_scene = TitleScene(screen)
    game_scene = GameScene(screen)
    boss_scene = MouseGodBoss(screen)
    shrine_scene = ShrineScene(screen)
    scene_manager.switch_to(title_scene)
    
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            
            # Handle global settings menu
            if settings_menu.active:
                result = settings_menu.handle_event(event)
                if result == "CLOSE_SETTINGS":
                    settings_menu.active = False
                elif result == "RESTART_GAME":
                    # Clear save file and reset settings
                    global_settings.restart_game()
                    # Create fresh instances of scenes
                    title_scene = TitleScene(screen)
                    game_scene = GameScene(screen)
                    boss_scene = MouseGodBoss(screen)
                    # Switch back to title scene
                    scene_manager.switch_to(title_scene)
                    settings_menu.active = False
                continue

            # Handle global ESC key for settings
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not settings_menu.active == True:
                settings_menu.active = True
                continue
                
            # Let current scene handle its specific events
            if scene_manager.current_scene:
                result = scene_manager.current_scene.handle_event(event)
                if result == "SWITCH_TO_GAME":
                    game_scene = GameScene(screen)
                    scene_manager.switch_to(game_scene)
                elif result == "ENTER_SHRINE":
                    shrine_scene = ShrineScene(screen)
                    scene_manager.switch_to(shrine_scene)
                elif result == "ENTER_BOSS":
                    current_scene = scene_manager.current_scene
                    if hasattr(current_scene, "save_game"):
                        current_scene.save_game()
                    boss_scene = MouseGodBoss(screen)
                    scene_manager.push(boss_scene)
                    break
                elif result == "ENDING":
                    ending_scene = Ending(screen)
                    scene_manager.switch_to(ending_scene)
                elif result == "FINAL_ENDING":
                    final_ending_scene = FinalEnding(screen)
                    scene_manager.switch_to(final_ending_scene)
                elif result == "OPEN_GLOBAL_SETTINGS":
                    settings_menu.active = True

        # Update current scene
        if scene_manager.current_scene and not settings_menu.active:
            update_result = scene_manager.current_scene.update()
            if update_result == "SWITCH_TO_GAME":
                game_scene = GameScene(screen)
                scene_manager.switch_to(game_scene)
            if update_result == "POP_SCENE":
                scene_manager.pop()

        # Draw current scene
        screen.fill((0, 0, 0))
        if scene_manager.current_scene:
            scene_manager.current_scene.draw(screen)
        
        # Draw global settings menu on top if active
        if settings_menu.active:
            settings_menu.draw(screen)
        
        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)
    
    # Save settings before quitting
    global_settings.save_settings()
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())