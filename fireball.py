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
        self.game_state = "playing"  # "playing", "dead", "victory"
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.init_game()
    
    def init_game(self):
        # Player
        self.player = {
            'x': self.WIDTH // 2,
            'y': self.HEIGHT - 100,
            'size': 20,
            'speed': 5,
            'attack_cooldown': 0
        }
        
        # Mouse God Boss
        self.boss = {
            'x': self.WIDTH // 2,
            'y': 100,
            'size': 60,
            'health': 100,
            'max_health': 100,
            'shoot_cooldown': 0,
            'move_timer': 0,
            'move_direction': 1,
            'phase': 1  # Gets harder as health decreases
        }
        
        # Projectiles
        self.fire_cheeseballs = []
        self.player_bullets = []
        
        # Input tracking
        self.keys = {
            'w': False, 'a': False, 's': False, 'd': False,
            'up': False, 'left': False, 'down': False, 'right': False,
            'space': False
        }
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w: self.keys['w'] = True
                elif event.key == pygame.K_a: self.keys['a'] = True
                elif event.key == pygame.K_s: self.keys['s'] = True
                elif event.key == pygame.K_d: self.keys['d'] = True
                elif event.key == pygame.K_UP: self.keys['up'] = True
                elif event.key == pygame.K_LEFT: self.keys['left'] = True
                elif event.key == pygame.K_DOWN: self.keys['down'] = True
                elif event.key == pygame.K_RIGHT: self.keys['right'] = True
                elif event.key == pygame.K_SPACE: self.keys['space'] = True
                elif event.key == pygame.K_r and self.game_state != "playing":
                    self.restart_game()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w: self.keys['w'] = False
                elif event.key == pygame.K_a: self.keys['a'] = False
                elif event.key == pygame.K_s: self.keys['s'] = False
                elif event.key == pygame.K_d: self.keys['d'] = False
                elif event.key == pygame.K_UP: self.keys['up'] = False
                elif event.key == pygame.K_LEFT: self.keys['left'] = False
                elif event.key == pygame.K_DOWN: self.keys['down'] = False
                elif event.key == pygame.K_RIGHT: self.keys['right'] = False
                elif event.key == pygame.K_SPACE: self.keys['space'] = False
        
        return True
    
    def update_player(self):
        if self.game_state != "playing":
            return
        
        # Movement
        if self.keys['w'] or self.keys['up']:
            self.player['y'] = max(0, self.player['y'] - self.player['speed'])
        if self.keys['s'] or self.keys['down']:
            self.player['y'] = min(self.HEIGHT - self.player['size'], 
                                 self.player['y'] + self.player['speed'])
        if self.keys['a'] or self.keys['left']:
            self.player['x'] = max(0, self.player['x'] - self.player['speed'])
        if self.keys['d'] or self.keys['right']:
            self.player['x'] = min(self.WIDTH - self.player['size'], 
                                 self.player['x'] + self.player['speed'])
        
        # Attack cooldown
        if self.player['attack_cooldown'] > 0:
            self.player['attack_cooldown'] -= 1
        
        # Shooting
        if self.keys['space'] and self.player['attack_cooldown'] <= 0:
            self.player_bullets.append({
                'x': self.player['x'] + self.player['size'] // 2,
                'y': self.player['y'],
                'speed': 8,
                'size': 5
            })
            self.player['attack_cooldown'] = 15
    
    def update_boss(self):
        if self.game_state != "playing":
            return
        
        # Boss movement (side to side)
        self.boss['move_timer'] += 1
        if self.boss['move_timer'] % 120 == 0:  # Change direction every 2 seconds
            self.boss['move_direction'] *= -1
        
        self.boss['x'] += self.boss['move_direction'] * 2
        if self.boss['x'] <= 50 or self.boss['x'] >= self.WIDTH - 50:
            self.boss['move_direction'] *= -1
        
        # Determine boss phase based on health
        health_percent = self.boss['health'] / self.boss['max_health']
        if health_percent > 0.66:
            self.boss['phase'] = 1
            shoot_delay = 60  # 1 second at 60 FPS
        elif health_percent > 0.33:
            self.boss['phase'] = 2
            shoot_delay = 40  # Faster shooting
        else:
            self.boss['phase'] = 3
            shoot_delay = 25  # Very fast shooting
        
        # Boss shooting
        if self.boss['shoot_cooldown'] <= 0:
            self.shoot_fire_cheeseball()
            self.boss['shoot_cooldown'] = shoot_delay
        else:
            self.boss['shoot_cooldown'] -= 1
    
    def shoot_fire_cheeseball(self):
        # Calculate angle to player for tracking
        dx = self.player['x'] + self.player['size'] // 2 - (self.boss['x'] + self.boss['size'] // 2)
        dy = self.player['y'] + self.player['size'] // 2 - (self.boss['y'] + self.boss['size'] // 2)
        angle = math.atan2(dy, dx)
        
        # Add some randomness based on boss phase
        if self.boss['phase'] >= 2:
            angle += random.uniform(-0.3, 0.3)  # Less accurate in higher phases
        
        speed = 3 + self.boss['phase']  # Gets faster each phase
        
        cheeseball = {
            'x': self.boss['x'] + self.boss['size'] // 2,
            'y': self.boss['y'] + self.boss['size'],
            'vx': math.cos(angle) * speed,
            'vy': math.sin(angle) * speed,
            'size': 12,
            'trail': []  # For fire effect
        }
        
        self.fire_cheeseballs.append(cheeseball)
        
        # In phase 3, shoot multiple cheeseballs
        if self.boss['phase'] == 3 and random.random() < 0.4:
            for i in range(2):
                extra_angle = angle + random.uniform(-0.8, 0.8)
                extra_cheeseball = {
                    'x': self.boss['x'] + self.boss['size'] // 2,
                    'y': self.boss['y'] + self.boss['size'],
                    'vx': math.cos(extra_angle) * speed,
                    'vy': math.sin(extra_angle) * speed,
                    'size': 12,
                    'trail': []
                }
                self.fire_cheeseballs.append(extra_cheeseball)
    
    def update_projectiles(self):
        # Update fire cheeseballs
        for cheeseball in self.fire_cheeseballs[:]:
            # Add to trail
            cheeseball['trail'].append((cheeseball['x'], cheeseball['y']))
            if len(cheeseball['trail']) > 8:
                cheeseball['trail'].pop(0)
            
            cheeseball['x'] += cheeseball['vx']
            cheeseball['y'] += cheeseball['vy']
            
            # Remove if off screen
            if (cheeseball['x'] < -50 or cheeseball['x'] > self.WIDTH + 50 or
                cheeseball['y'] < -50 or cheeseball['y'] > self.HEIGHT + 50):
                self.fire_cheeseballs.remove(cheeseball)
        
        # Update player bullets
        for bullet in self.player_bullets[:]:
            bullet['y'] -= bullet['speed']
            if bullet['y'] < 0:
                self.player_bullets.remove(bullet)
    
    def check_collisions(self):
        if self.game_state != "playing":
            return
        
        # Player vs fire cheeseballs
        player_rect = pygame.Rect(self.player['x'], self.player['y'], 
                                self.player['size'], self.player['size'])
        
        for cheeseball in self.fire_cheeseballs:
            cheeseball_rect = pygame.Rect(cheeseball['x'] - cheeseball['size']//2,
                                        cheeseball['y'] - cheeseball['size']//2,
                                        cheeseball['size'], cheeseball['size'])
            if player_rect.colliderect(cheeseball_rect):
                self.game_state = "dead"
                return
        
        # Player bullets vs boss
        boss_rect = pygame.Rect(self.boss['x'], self.boss['y'], 
                              self.boss['size'], self.boss['size'])
        
        for bullet in self.player_bullets[:]:
            bullet_rect = pygame.Rect(bullet['x'] - bullet['size']//2,
                                    bullet['y'] - bullet['size']//2,
                                    bullet['size'], bullet['size'])
            if boss_rect.colliderect(bullet_rect):
                self.boss['health'] -= 5
                self.player_bullets.remove(bullet)
                
                if self.boss['health'] <= 0:
                    self.game_state = "victory"
                    return
    
    def draw(self):
        # Clear screen with gradient-like effect
        self.screen.fill((20, 10, 40))
        
        # Draw stars/particles in background
        for i in range(50):
            x = (i * 123) % self.WIDTH
            y = (i * 456) % self.HEIGHT
            pygame.draw.circle(self.screen, (100, 100, 150), (x, y), 1)
        
        if self.game_state == "playing":
            self.draw_game()
        elif self.game_state == "dead":
            self.draw_game_over()
        elif self.game_state == "victory":
            self.draw_victory()
        
        pygame.display.flip()
    
    def draw_game(self):
        # Draw player
        pygame.draw.rect(self.screen, self.BLUE, 
                        (self.player['x'], self.player['y'], 
                         self.player['size'], self.player['size']))
        pygame.draw.rect(self.screen, self.WHITE, 
                        (self.player['x'], self.player['y'], 
                         self.player['size'], self.player['size']), 2)
        
        # Draw boss (Mouse God)
        boss_color = self.GRAY
        if self.boss['phase'] == 2:
            boss_color = self.DARK_RED
        elif self.boss['phase'] == 3:
            boss_color = self.RED
        
        # Boss body
        pygame.draw.ellipse(self.screen, boss_color,
                          (self.boss['x'], self.boss['y'], 
                           self.boss['size'], self.boss['size']))
        
        # Boss eyes (glowing)
        eye_size = 8
        eye_y = self.boss['y'] + 15
        pygame.draw.circle(self.screen, self.RED, 
                         (int(self.boss['x'] + 15), int(eye_y)), eye_size)
        pygame.draw.circle(self.screen, self.RED, 
                         (int(self.boss['x'] + 45), int(eye_y)), eye_size)
        pygame.draw.circle(self.screen, self.YELLOW, 
                         (int(self.boss['x'] + 15), int(eye_y)), eye_size//2)
        pygame.draw.circle(self.screen, self.YELLOW, 
                         (int(self.boss['x'] + 45), int(eye_y)), eye_size//2)
        
        # Boss ears
        ear_points1 = [(self.boss['x'] + 10, self.boss['y']), 
                      (self.boss['x'] + 5, self.boss['y'] - 15),
                      (self.boss['x'] + 20, self.boss['y'] - 5)]
        ear_points2 = [(self.boss['x'] + 50, self.boss['y']), 
                      (self.boss['x'] + 55, self.boss['y'] - 15),
                      (self.boss['x'] + 40, self.boss['y'] - 5)]
        pygame.draw.polygon(self.screen, boss_color, ear_points1)
        pygame.draw.polygon(self.screen, boss_color, ear_points2)
        
        # Draw fire cheeseballs with trails
        for cheeseball in self.fire_cheeseballs:
            # Draw trail
            for i, (tx, ty) in enumerate(cheeseball['trail']):
                alpha = (i + 1) / len(cheeseball['trail'])
                trail_size = int(cheeseball['size'] * alpha * 0.5)
                if trail_size > 0:
                    pygame.draw.circle(self.screen, self.ORANGE, 
                                     (int(tx), int(ty)), trail_size)
            
            # Draw main cheeseball
            pygame.draw.circle(self.screen, self.YELLOW,
                             (int(cheeseball['x']), int(cheeseball['y'])), 
                             cheeseball['size'])
            pygame.draw.circle(self.screen, self.ORANGE,
                             (int(cheeseball['x']), int(cheeseball['y'])), 
                             cheeseball['size'] - 2)
            pygame.draw.circle(self.screen, self.RED,
                             (int(cheeseball['x']), int(cheeseball['y'])), 
                             cheeseball['size'] - 4)
        
        # Draw player bullets
        for bullet in self.player_bullets:
            pygame.draw.circle(self.screen, self.WHITE,
                             (int(bullet['x']), int(bullet['y'])), 
                             bullet['size'])
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        # Boss health bar
        bar_width = 300
        bar_height = 20
        bar_x = (self.WIDTH - bar_width) // 2
        bar_y = 20
        
        # Background
        pygame.draw.rect(self.screen, self.BLACK, 
                        (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(self.screen, self.RED, 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # Health fill
        health_percent = max(0, self.boss['health'] / self.boss['max_health'])
        fill_width = int(bar_width * health_percent)
        pygame.draw.rect(self.screen, self.ORANGE, 
                        (bar_x, bar_y, fill_width, bar_height))
        
        # Health text
        health_text = self.small_font.render(
            f"Mouse God Health: {self.boss['health']}/{self.boss['max_health']}", 
            True, self.WHITE)
        text_rect = health_text.get_rect(center=(self.WIDTH//2, bar_y - 15))
        self.screen.blit(health_text, text_rect)
        
        # Phase indicator
        phase_text = self.small_font.render(f"Phase {self.boss['phase']}", 
                                          True, self.RED)
        self.screen.blit(phase_text, (bar_x + bar_width + 10, bar_y))
        
        # Instructions
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
        
        # Game over text
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
        
        # Victory text
        victory_text = self.font.render("VICTORY!", True, self.YELLOW)
        text_rect = victory_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 - 50))
        self.screen.blit(victory_text, text_rect)
        
        subtitle = self.small_font.render("You have defeated the Mouse God!", True, self.WHITE)
        text_rect = subtitle.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
        self.screen.blit(subtitle, text_rect)
        
        restart_text = self.small_font.render("Press R to play again", True, self.WHITE)
        text_rect = restart_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 50))
        self.screen.blit(restart_text, text_rect)
    
    def restart_game(self):
        self.game_state = "playing"
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

# Run the game
if __name__ == "__main__":
    game = MouseGodBoss()
    game.run()
# """
# import pygame
# from player import PlayerMovement

# class Boss:
#     def __init__(self, x, y):
#         self.image = pygame.image.load("resources/boss.png").convert_alpha()
#         self.image = pygame.transform.scale(self.image, (64 * 3, 64 * 3))
#         self.rect = self.image.get_rect(topleft=(x, y))
#         self.health = 100  # Example health value
#         self.is_alive = True
#         self.attack_timer = 0
#         self.attack_delay = 60  # Frames between attacks
#         self.active_fireballs = []

#     def draw(self, surface, camera_offset):
#         if self.is_alive:
#             surface.blit(self.image, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))

#     def take_damage(self, amount):
#         self.health -= amount
#         if self.health <= 0:
#             self.is_alive = False

# class PlayerHealth:
#     def __init__(self, player, max_health=100):
#         self.player = player  # Store reference to player
#         self.max_health = max_health
#         self.current_health = max_health
#         print(f"PlayerHealth initialized with max health: {max_health}")

#     def take_damage(self, amount):
#         self.current_health -= amount
#         if self.current_health < 0:
#             self.current_health = 0

#     def is_alive(self):
#         return self.current_health > 0

#     def get_health_percentage(self):
#         return self.current_health / self.max_health
    
#     def draw_health_bar(self, surface):
#         health_percentage = self.get_health_percentage()
#         bar_width = 200
#         bar_height = 20
#         fill_width = int(bar_width * health_percentage)
        
#         # Draw health bar at fixed screen position
#         x = 20  # Fixed screen position
#         y = 20  # Fixed screen position
        
#         # Draw the background of the health bar
#         pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
#         # Draw the filled part of the health bar
#         pygame.draw.rect(surface, (0, 255, 0), (x, y, fill_width, bar_height))
        
#         # Draw health text
#         font = pygame.font.Font(None, 24)
#         health_text = f"Health: {self.current_health}/{self.max_health}"
#         text_surface = font.render(health_text, True, (255, 255, 255))
#         surface.blit(text_surface, (x + bar_width + 10, y))
    

# class Fireball:
#     def __init__(self, boss_x, boss_y, target_x, target_y):
#         self.image = pygame.image.load("resources/fireball.png").convert_alpha()
#         self.image = pygame.transform.scale(self.image, (32 * 3, 32 * 3))
#         self.rect = self.image.get_rect(center=(boss_x, boss_y))
#         self.speed = 5
        
#         # Calculate direction when fireball is created
#         direction_x = target_x - boss_x
#         direction_y = target_y - boss_y
#         distance = (direction_x**2 + direction_y**2)**0.5
        
#         if distance > 0:
#             self.direction_x = direction_x / distance
#             self.direction_y = direction_y / distance
#         else:
#             self.direction_x = 0
#             self.direction_y = 0

#     def update(self):
#         # Move fireball along its path
#         self.rect.x += self.direction_x * self.speed
#         self.rect.y += self.direction_y * self.speed
        
#     def hit_detection(self, player_rect):
#         return self.rect.colliderect(player_rect)
        
# class FireballQuest:
#     def __init__(self, player):
#         self.boss = Boss(800, 300)  # Position boss on right side
#         self.player = player
#         self.player_health = PlayerHealth(player)
#         self.active_fireballs = []
#         self.game_over = False
#         self.camera_offset = pygame.Vector2(0, 0)
        
#         # Load sound effects
#         try:
#             self.fireball_sound = pygame.mixer.Sound("resources/fireball.wav")
#             self.hit_sound = pygame.mixer.Sound("resources/hit.wav")
#         except:
#             print("Warning: Could not load sound effects")

#     def update(self):
#         if self.game_over:
#             return

#         # Update boss attack timer
#         if self.boss.is_alive:
#             self.boss.attack_timer += 1
#             if self.boss.attack_timer >= self.boss.attack_delay:
#                 self.boss.attack_timer = 0
#                 # Create new fireball aimed at player
#                 new_fireball = Fireball(
#                     self.boss.rect.centerx,
#                     self.boss.rect.centery,
#                     self.player.rect.centerx,
#                     self.player.rect.centery
#                 )
#                 self.active_fireballs.append(new_fireball)
#                 try:
#                     self.fireball_sound.play()
#                 except:
#                     pass

#         # Update all active fireballs
#         for fireball in self.active_fireballs[:]:  # Use slice to safely remove while iterating
#             fireball.update()
            
#             # Remove fireballs that are off screen
#             if (fireball.rect.right < 0 or fireball.rect.left > self.player.SCREEN_WIDTH or
#                 fireball.rect.bottom < 0 or fireball.rect.top > self.player.SCREEN_HEIGHT):
#                 self.active_fireballs.remove(fireball)
#                 continue

#             # Check collision with player
#             if fireball.hit_detection(self.player.rect):
#                 self.player_health.take_damage(10)
#                 self.active_fireballs.remove(fireball)
#                 try:
#                     self.hit_sound.play()
#                 except:
#                     pass
                
#                 if not self.player_health.is_alive():
#                     self.game_over = True

#     def draw(self, screen):
#         camera_offset = pygame.Vector2(0, 0)
#         if self.game_over:
#             # Draw game over screen
#             font = pygame.font.Font(None, 74)
#             text = font.render('Game Over', True, (255, 0, 0))
#             screen.blit(text, (screen.get_width()//2 - 140, screen.get_height()//2 - 30))
#             return

#         # Draw boss with camera offset
#         if self.boss.is_alive:
#             self.boss.draw(screen, camera_offset)

#         # Draw all active fireballs with camera offset
#         for fireball in self.active_fireballs:
#             screen.blit(fireball.image, 
#                 (fireball.rect.x - camera_offset.x, 
#                  fireball.rect.y - camera_offset.y))

#         # Draw health bar (no camera offset since it's UI)
#         self.player_health.draw_health_bar(screen)
        
