#fireball quest (final bossfight)

"""
- healthbar
- attack animation
- fireball graphics
- big boss graphics and animations
- fireball hit detection
- all sound effects
- fireball hit effect
- fireball hit damage
- fireball hit quest completion
- fireball hit quest failure
- fireball hit quest progress
- fireball hit quest restart

- death animation
- death sound
"""
import pygame
from player import PlayerMovement

class Boss:
    def __init__(self, x, y):
        self.image = pygame.image.load("resources/boss.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (64 * 3, 64 * 3))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.health = 100  # Example health value
        self.is_alive = True
        self.attack_timer = 0
        self.attack_delay = 60  # Frames between attacks
        self.active_fireballs = []

    def draw(self, surface, camera_offset):
        if self.is_alive:
            surface.blit(self.image, (self.rect.x - camera_offset.x, self.rect.y - camera_offset.y))

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.is_alive = False

class PlayerHealth:
    def __init__(self, player, max_health=100):
        self.player = player  # Store reference to player
        self.max_health = max_health
        self.current_health = max_health
        print(f"PlayerHealth initialized with max health: {max_health}")

    def take_damage(self, amount):
        self.current_health -= amount
        if self.current_health < 0:
            self.current_health = 0

    def is_alive(self):
        return self.current_health > 0

    def get_health_percentage(self):
        return self.current_health / self.max_health
    
    def draw_health_bar(self, surface):
        health_percentage = self.get_health_percentage()
        bar_width = 200
        bar_height = 20
        fill_width = int(bar_width * health_percentage)
        
        # Draw health bar at fixed screen position
        x = 20  # Fixed screen position
        y = 20  # Fixed screen position
        
        # Draw the background of the health bar
        pygame.draw.rect(surface, (255, 0, 0), (x, y, bar_width, bar_height))
        # Draw the filled part of the health bar
        pygame.draw.rect(surface, (0, 255, 0), (x, y, fill_width, bar_height))
        
        # Draw health text
        font = pygame.font.Font(None, 24)
        health_text = f"Health: {self.current_health}/{self.max_health}"
        text_surface = font.render(health_text, True, (255, 255, 255))
        surface.blit(text_surface, (x + bar_width + 10, y))
    

class Fireball:
    def __init__(self, boss_x, boss_y, target_x, target_y):
        self.image = pygame.image.load("resources/fireball.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (32 * 3, 32 * 3))
        self.rect = self.image.get_rect(center=(boss_x, boss_y))
        self.speed = 5
        
        # Calculate direction when fireball is created
        direction_x = target_x - boss_x
        direction_y = target_y - boss_y
        distance = (direction_x**2 + direction_y**2)**0.5
        
        if distance > 0:
            self.direction_x = direction_x / distance
            self.direction_y = direction_y / distance
        else:
            self.direction_x = 0
            self.direction_y = 0

    def update(self):
        # Move fireball along its path
        self.rect.x += self.direction_x * self.speed
        self.rect.y += self.direction_y * self.speed
        
    def hit_detection(self, player_rect):
        return self.rect.colliderect(player_rect)
        
class FireballQuest:
    def __init__(self, player):
        self.boss = Boss(800, 300)  # Position boss on right side
        self.player = player
        self.player_health = PlayerHealth(player)
        self.active_fireballs = []
        self.game_over = False
        self.camera_offset = pygame.Vector2(0, 0)
        
        # Load sound effects
        try:
            self.fireball_sound = pygame.mixer.Sound("resources/fireball.wav")
            self.hit_sound = pygame.mixer.Sound("resources/hit.wav")
        except:
            print("Warning: Could not load sound effects")

    def update(self):
        if self.game_over:
            return

        # Update boss attack timer
        if self.boss.is_alive:
            self.boss.attack_timer += 1
            if self.boss.attack_timer >= self.boss.attack_delay:
                self.boss.attack_timer = 0
                # Create new fireball aimed at player
                new_fireball = Fireball(
                    self.boss.rect.centerx,
                    self.boss.rect.centery,
                    self.player.rect.centerx,
                    self.player.rect.centery
                )
                self.active_fireballs.append(new_fireball)
                try:
                    self.fireball_sound.play()
                except:
                    pass

        # Update all active fireballs
        for fireball in self.active_fireballs[:]:  # Use slice to safely remove while iterating
            fireball.update()
            
            # Remove fireballs that are off screen
            if (fireball.rect.right < 0 or fireball.rect.left > self.player.SCREEN_WIDTH or
                fireball.rect.bottom < 0 or fireball.rect.top > self.player.SCREEN_HEIGHT):
                self.active_fireballs.remove(fireball)
                continue

            # Check collision with player
            if fireball.hit_detection(self.player.rect):
                self.player_health.take_damage(10)
                self.active_fireballs.remove(fireball)
                try:
                    self.hit_sound.play()
                except:
                    pass
                
                if not self.player_health.is_alive():
                    self.game_over = True

    def draw(self, screen):
        camera_offset = pygame.Vector2(0, 0)
        if self.game_over:
            # Draw game over screen
            font = pygame.font.Font(None, 74)
            text = font.render('Game Over', True, (255, 0, 0))
            screen.blit(text, (screen.get_width()//2 - 140, screen.get_height()//2 - 30))
            return

        # Draw boss with camera offset
        if self.boss.is_alive:
            self.boss.draw(screen, camera_offset)

        # Draw all active fireballs with camera offset
        for fireball in self.active_fireballs:
            screen.blit(fireball.image, 
                (fireball.rect.x - camera_offset.x, 
                 fireball.rect.y - camera_offset.y))

        # Draw health bar (no camera offset since it's UI)
        self.player_health.draw_health_bar(screen)
        
