# #fireball quest (final bossfight)

# """
# - healthbar
# - attack animation
# - fireball graphics
# - big boss graphics and animations
# - fireball hit detection
# - all sound effects
# - fireball hit effect
# - fireball hit damage
# - fireball hit quest completion
# - fireball hit quest failure
# - fireball hit quest progress
# - fireball hit quest restart

# - death animation
# - death sound

import pygame
import math
import random
import sys
from player import PlayerMovement
from misc import SCREEN_HEIGHT, SCREEN_WIDTH


class MouseGodBoss:
    def __init__(self):
        pygame.init()
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Mouse God Boss Battle")
        self.clock = pygame.time.Clock()
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.RED = (255, 50, 50)
        self.ORANGE = (255, 165, 0)
        self.YELLOW = (255, 255, 0)
        self.BLUE = (100, 150, 255)
        self.PURPLE = (150, 50, 200)
        self.GRAY = (128, 128, 128)
        self.DARK_RED = (150, 0, 0)
        
        # Game state
        self.game_state = "playing"  # "playing", "dead", "victory", "paused"
        self.pause_menu_active = False
        self.settings_font = pygame.font.Font(None, 48)
        self.settings_small_font = pygame.font.Font(None, 32)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        

        self.boss_frames = self.load_spritesheet('resources/boss.png', 2, 200, 150)
        self.boss_frames = [pygame.transform.scale(frame, (800, 600)) for frame in self.boss_frames]
        
        self.attack_frames = self.load_spritesheet('resources/attack.png', 7, 32, 32)
        self.attack_frames = [pygame.transform.scale(frame, (32*4, 32*4)) for frame in self.attack_frames]
        
        self.death_frames = self.load_spritesheet('resources/death.png', 7, 32, 32)
        self.deahth_frames = [pygame.transform.scale(frame, (32*4, 32*4)) for frame in self.death_frames]

        # Animation state variables
        self.boss_current_frame = 0
        
        self.is_attacking = False
        self.frame_timer = 0
        self.frame_delay = 6 # Delay for boss animation frames
        self.death_anim_index = 0
        self.death_anim_timer = 0
        self.is_boss_dead = False
        
        
        self.init_game()
    
    def init_game(self):
        # Player
        self.player = PlayerMovement(self.WIDTH, self.HEIGHT, self.WIDTH)
        
    
        self.player.PLAYER_SPEED = 7
        self.player.PLAYER_JUMP_POWER = 1
        self.player.player_x = self.WIDTH // 2
        self.player.player_y = 400
        self.player.rect.topleft = (self.player.player_x, self.player.player_y)
        self.player_attack_cooldown = 0
        self.player_attacking = False
        self.player.allow_attack = True
        
        
      
        # Mouse God Boss
        self.boss = {
            'x': self.WIDTH // 2 - 150,
            'y': 200,
            'width': 700,
            'height':500,
            'health': 100,
            'max_health': 100,
            'shoot_cooldown': 0,
            'move_timer': 0,
            'move_direction': 1,
            'phase': 1 
        # Gets harder as health decreases
        }
        self.boss['x'] = (self.WIDTH - self.boss_frames[0].get_width()) // 2
        self.boss['y'] = 0
        self.boss_rect = pygame.Rect(self.boss['x'], self.boss['y'], self.boss['width'], self.boss['height'])
        self.boss_rect.topleft = (self.boss['x'], self.boss['y'])
        
        # Projectiles
        self.fire_cheeseballs = []
        
    def load_spritesheet(self, image_path, frame_count, frame_width, frame_height):
        spritesheet = pygame.image.load(image_path)
        frames = []
        for i in range(frame_count):
            frame = spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
            frames.append(frame)
        return frames    
    
    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "paused"
                        self.pause_menu_active = True
                    elif self.game_state == "paused":
                        self.game_state = "playing"
                        self.pause_menu_active = False
                elif event.key == pygame.K_g and self.game_state == "paused":
                    return "OPEN_GLOBAL_SETTINGS"
                elif event.key == pygame.K_q and self.game_state == "paused":
                    return False  # Quit game
                elif event.key == pygame.K_r and self.game_state != "playing":
                    self.restart_game()
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT and self.game_state == "playing":
                    self.try_player_attack()
        return True

    def try_player_attack(self):
        # Only allow attack if cooldown is 0 and player is near boss
        if self.player_attack_cooldown == 0:
            player_rect = self.player.rect
            # Base size of sword
            sword_width = 10
            sword_height = 32

            # Position: top-right corner of player
            sword_x = player_rect.right
            sword_y = player_rect.top

            # Create sword hitbox
            sword_hitbox = pygame.Rect(sword_x, sword_y, sword_width, sword_height)

            # Inflate the hitbox (expand in all directions)
            sword_hitbox = sword_hitbox.inflate(64 * 3, 64 * 3)

            boss_rect = self.boss_rect
            # Check if player is close enough to boss (simple collision or range check)
            attack_range = 60
            if sword_hitbox.colliderect(boss_rect.inflate(attack_range, attack_range)):
                self.player_attacking = True
                self.boss['health'] -= 5
                self.player_attack_cooldown = 30  # Cooldown frames
                if self.boss['health'] <= 0:
                    self.game_state = "victory"

    def update_player(self):
        if self.game_state != "playing":
            return
        floor_rects = [pygame.Rect(0, 500, self.WIDTH, 100)]  # Ground at y=500
        ladder_rects = []
        keys = pygame.key.get_pressed()
        self.player.update_position(floor_rects, ladder_rects)
        self.player.update_animation(keys)
        self.player.apply_gravity()
        if self.player_attack_cooldown > 0:
            self.player_attack_cooldown -= 1
        else:
            self.player_attacking = False

    def update_boss(self):
        

        if self.game_state != "playing":
            return
        # Boss movement (side to side)
        self.boss['move_timer'] += 1
        if self.boss['move_timer'] % 120 == 0:
            self.boss['move_direction'] *= -1
        self.boss['x'] += self.boss['move_direction'] * 2
        if self.boss['x'] <= 0 or self.boss['x'] >= self.WIDTH - self.boss['width']:
            self.boss['move_direction'] *= -1
        self.boss_rect.topleft = (self.boss['x'], self.boss['y'])
        # Determine boss phase based on health
        health_percent = self.boss['health'] / self.boss['max_health']
        if health_percent > 0.66:
            self.boss['phase'] = 1
            shoot_delay = 60
        elif health_percent > 0.33:
            self.boss['phase'] = 2
            shoot_delay = 40
        else:
            self.boss['phase'] = 3
            shoot_delay = 30
        # Boss shooting
        if self.boss['shoot_cooldown'] <= 0:
            self.shoot_fire_cheeseball()
            self.boss['shoot_cooldown'] = shoot_delay
        else:
            self.boss['shoot_cooldown'] -= 1

    def shoot_fire_cheeseball(self):
        # Fireball spawns from boss mouth (center top of boss sprite)
        mouth_x = self.boss['x'] + 400  # 800 / 2
        mouth_y = self.boss['y'] + 170 
        dx = self.player.player_x + self.player.PLAYER_WIDTH // 2 - mouth_x
        dy = self.player.player_y + self.player.PLAYER_HEIGHT // 2 - mouth_y
        angle = math.atan2(dy, dx)
        if self.boss['phase'] >= 2:
            angle += random.uniform(-0.3, 0.3)
        speed = 3 + self.boss['phase']
        cheeseball = {
            'x': mouth_x,
            'y': mouth_y,
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'size': 35,  # Larger fireballs
            'trail': []
        }
        self.fire_cheeseballs.append(cheeseball)
        if self.boss['phase'] == 3 and random.random() < 0.4:
            for i in range(2):
                extra_angle = angle + random.uniform(-0.8, 0.8)
                extra_cheeseball = {
                    'x': mouth_x,
                    'y': mouth_y,
                    'vx': math.cos(extra_angle) * speed,
                    'vy': math.sin(extra_angle) * speed,
                    'size': 48,
                    'trail': []
                }
                self.fire_cheeseballs.append(extra_cheeseball)

    def update_projectiles(self):
        for cheeseball in self.fire_cheeseballs[:]:
            cheeseball['trail'].append((cheeseball['x'], cheeseball['y']))
            if len(cheeseball['trail']) > 8:
                cheeseball['trail'].pop(0)
            cheeseball['x'] += cheeseball['vx']
            cheeseball['y'] += cheeseball['vy']
            if (cheeseball['x'] < -100 or cheeseball['x'] > self.WIDTH + 100 or
                cheeseball['y'] < -100 or cheeseball['y'] > self.HEIGHT + 100):
                self.fire_cheeseballs.remove(cheeseball)
                
    def check_collisions(self):
        if self.game_state != "playing":
            return
        def get_shrunk_hitbox(rect, shrink=0.6):
            w = int(rect.width * shrink)
            h = int(rect.height * shrink)
            return pygame.Rect(
                rect.centerx - w // 2,
                rect.centery - h // 2,
                w, h
            )
        player_rect = get_shrunk_hitbox(self.player.rect, shrink=0.6)

        for cheeseball in self.fire_cheeseballs:
            cheeseball_rect = pygame.Rect(cheeseball['x'] - cheeseball['size']//2,
                                        cheeseball['y'] - cheeseball['size']//2,
                                        cheeseball['size']*0.4, cheeseball['size']*0.4)
            if player_rect.colliderect(cheeseball_rect):
                self.game_state = "dead"
                return

    def draw(self):
        self.screen.fill((20, 10, 40))
        for i in range(50):
            x = (i * 123) % self.WIDTH
            y = (i * 456) % self.HEIGHT
            pygame.draw.circle(self.screen, (100, 100, 150), (x, y), 1)
        
        if self.game_state == "playing":
            self.draw_game()
        elif self.game_state == "paused":
            self.draw_game()  # Draw the game in background
            self.draw_pause_menu()  # Draw pause menu on top
        elif self.game_state == "dead":
            self.draw_game_over()
        elif self.game_state == "victory":
            self.draw_victory()
        
        pygame.display.flip()

    def draw_game(self):
        # Draw ground
        pygame.draw.rect(self.screen, (60, 40, 20), (0, 500, self.WIDTH, 100))
        # Draw player (mouse avatar)
        
        # Boss death animation
        if self.boss['health'] <= 0:
            self.is_boss_dead = True
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            if not self.is_boss_dead:
                self.boss_current_frame += 1

        frame_index = self.boss_current_frame % len(self.boss_frames)
        frame = self.boss_frames[frame_index]
        self.screen.blit(frame, (self.boss['x'], self.boss['y']))
        # Draw fire cheeseballs with trails
        for cheeseball in self.fire_cheeseballs:
            for i, (tx, ty) in enumerate(cheeseball['trail']):
                alpha = (i + 1) / len(cheeseball['trail'])
                trail_size = int(cheeseball['size'] * alpha * 0.5)
                if trail_size > 0:
                    pygame.draw.circle(self.screen, self.ORANGE, (int(tx), int(ty)), trail_size)
            pygame.draw.circle(self.screen, self.YELLOW,
                             (int(cheeseball['x']), int(cheeseball['y'])), 
                             cheeseball['size'])
            pygame.draw.circle(self.screen, self.ORANGE,
                             (int(cheeseball['x']), int(cheeseball['y'])), 
                             cheeseball['size'] - 8)
            pygame.draw.circle(self.screen, self.RED,
                             (int(cheeseball['x']), int(cheeseball['y'])), 
                             cheeseball['size'] - 16)
        self.player.draw(self.screen, pygame.key.get_pressed(), pygame.Vector2(0, 0))
        # Player attack animation
        self.draw_ui()

    def draw_ui(self):
        bar_width = 300
        bar_height = 20
        bar_x = (self.WIDTH - bar_width) // 2
        bar_y = 20
        pygame.draw.rect(self.screen, self.BLACK, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(self.screen, self.RED, (bar_x, bar_y, bar_width, bar_height))
        health_percent = max(0, self.boss['health'] / self.boss['max_health'])
        fill_width = int(bar_width * health_percent)
        pygame.draw.rect(self.screen, self.ORANGE, (bar_x, bar_y, fill_width, bar_height))
        health_text = self.small_font.render(
            f"Mouse God Health: {self.boss['health']}/{self.boss['max_health']}", 
            True, self.WHITE)
        text_rect = health_text.get_rect(center=(self.WIDTH//2, bar_y - 15))
        self.screen.blit(health_text, text_rect)
        phase_text = self.small_font.render(f"Phase {self.boss['phase']}", True, self.RED)
        self.screen.blit(phase_text, (bar_x + bar_width + 10, bar_y))
        instructions = [
            "WASD/Arrow Keys: Move",
            "Space: Attack",
            "Avoid the fire-cheeseballs!"
        ]
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.WHITE)
            self.screen.blit(text, (10, self.HEIGHT - 80 + i * 25))

    def draw_game_over(self):
        self.screen.fill((40, 0, 0))
        game_over_text = self.font.render("YOU HAVE BEEN CHEESED!", True, self.RED)
        text_rect = game_over_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 - 50))
        self.screen.blit(game_over_text, text_rect)
        subtitle = self.small_font.render("The Mouse God's fire-cheeseballs were too much!", 
                                        True, self.WHITE)
        text_rect = subtitle.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
        self.screen.blit(subtitle, text_rect)
        restart_text = self.small_font.render("Press R to try again", True, self.WHITE)
        text_rect = restart_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 50))
        self.screen.blit(restart_text, text_rect)

    def draw_victory(self):
        self.screen.fill((0, 40, 0))
        victory_text = self.font.render("VICTORY!", True, self.YELLOW)
        text_rect = victory_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 - 50))
        self.screen.blit(victory_text, text_rect)
        subtitle = self.small_font.render("You have defeated the Mouse God!", True, self.WHITE)
        text_rect = subtitle.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
        self.screen.blit(subtitle, text_rect)
        restart_text = self.small_font.render("Press R to play again", True, self.WHITE)
        text_rect = restart_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 50))
        self.screen.blit(restart_text, text_rect)

    def draw_pause_menu(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Menu background
        menu_width = 400
        menu_height = 350  # Increased height for new option
        menu_x = (self.WIDTH - menu_width) // 2
        menu_y = (self.HEIGHT - menu_height) // 2
        
        pygame.draw.rect(self.screen, (50, 50, 50), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, (100, 100, 100), (menu_x, menu_y, menu_width, menu_height), 3)
        
        # Menu title
        title_text = self.settings_font.render("PAUSED", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.WIDTH//2, menu_y + 50))
        self.screen.blit(title_text, title_rect)
        
        # Menu options
        options = [
            "Press ESC to Resume",
            "Press R to Restart Game",
            "Press G for Global Settings",
            "Press Q to Quit"
        ]
        
        for i, option in enumerate(options):
            option_text = self.settings_small_font.render(option, True, self.WHITE)
            option_rect = option_text.get_rect(center=(self.WIDTH//2, menu_y + 120 + i * 40))
            self.screen.blit(option_text, option_rect)

    def restart_game(self):
        self.game_state = "playing"
        self.pause_menu_active = False
        self.is_boss_dead = False
        self.boss_current_frame = 0
        self.frame_timer = 0
        self.death_anim_index = 0
        self.death_anim_timer = 0
        self.player_attacking = False
        self.player_attack_cooldown = 0
        self.player.allow_attack = True
        self.fire_cheeseballs.clear()
        self.init_game()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            if self.game_state == "playing":
                self.update_player()
                self.update_boss()
                self.update_projectiles()
                self.check_collisions()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = MouseGodBoss()
    game.run()
        
