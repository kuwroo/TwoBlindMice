import pygame
from misc import *
from pygame import mixer
from pygame import font
import math

def play_fourth_quest():
    pygame.font.init()
    pygame.init()

    clock = pygame.time.Clock()
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) 
    pygame.display.set_caption("RAT AND ROLL!") 
    print("RAT AND ROLL!") 

    # Game constants
    HIT_ZONE_Y = SCREEN_HEIGHT - 100
    HIT_ZONE_WIDTH = 25
    FPS = 60
    PROGRESS_BAR_WIDTH = SCREEN_WIDTH 
    PROGRESS_BAR_Y = SCREEN_HEIGHT - 50
    BACKGROUND = (0, 20, 50)

    # Game state variables
    run = True
    quest_result = None
    combo_count = 0
    max_combo = 0
    health = 100
    max_health = 100
    score = 0
    missed_notes = 0
    quest_failed = False
    music_started = True

    # Fonts
    font_path = "resources/Minecraft.ttf"
    font_large = pygame.font.Font(font_path, 42)
    font_medium = pygame.font.Font(font_path, 36)
    font_small = pygame.font.Font(font_path, 24)


    # Visual effects
    particles = []
    combo_display_timer = 0
    hit_effects = []

    class Particle:
        def __init__(self, x, y, color, velocity):
            self.x = x
            self.y = y
            self.color = color
            self.velocity = velocity
            self.life = 30
            self.max_life = 30
            
        def update(self):
            self.x += self.velocity[0]
            self.y += self.velocity[1]
            self.life -= 1
            
        def draw(self, surface):
            if self.life > 0:
                alpha = int(255 * (self.life / self.max_life))
                color_with_alpha = (*self.color[:3], alpha)
                size = int(4 * (self.life / self.max_life))
                if size > 0:
                    pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)

    class HitEffect:
        def __init__(self, x, y, hit_type="perfect"):
            self.x = x
            self.y = y
            self.timer = 30
            self.hit_type = hit_type
            self.scale = 1.0
            
        def update(self):
            self.timer -= 1
            self.scale += 0.1
            self.y -= 2
            
        def draw(self, surface):
            if self.timer > 0:
                alpha = int(255 * (self.timer / 30))
                if self.hit_type == "perfect":
                    color = (255, 255, 100)
                    text = "PERFECT!"
                elif self.hit_type == "good":
                    color = (100, 255, 100)
                    text = "GOOD"
                else:
                    color = (255, 100, 100)
                    text = "MISS"
                    
                font_obj = pygame.font.Font(font_path, int(36 * self.scale))
                text_surface = font_obj.render(text, True, color)
                surface.blit(text_surface, (self.x - text_surface.get_width()//2, self.y))

    class Key:
        def __init__(self, x, y, colour1, colour2, key):
            self.x = x
            self.y = y
            self.colour1 = colour1
            self.colour2 = colour2
            self.key = key
            self.rect = pygame.Rect(x, y, 100, 40)
            self.glow_intensity = 0
            self.hit_animation = 0
            
        def update(self):
            if self.glow_intensity > 0:
                self.glow_intensity -= 5
            if self.hit_animation > 0:
                self.hit_animation -= 1
                
        def draw(self, surface, pressed=False):
            # Draw glow effect
            if self.glow_intensity > 0:
                glow_rect = pygame.Rect(self.x - 5, self.y - 5, 110, 50)
                glow_color = (255, 255, 255, self.glow_intensity)
                pygame.draw.rect(surface, (255, 255, 255), glow_rect, 3)
            
            # Draw main key
            color = self.colour2 if pressed else self.colour1
            if self.hit_animation > 0:
                # Add white flash when hit
                flash_intensity = self.hit_animation / 10
                color = tuple(min(255, c + int(100 * flash_intensity)) for c in color)
                
            pygame.draw.rect(surface, color, self.rect)
            pygame.draw.rect(surface, (255, 255, 255), self.rect, 2)

    keys = [
        Key(100, 520, (255, 100, 100), (255, 50, 50), pygame.K_a),
        Key(266, 520, (100, 255, 100), (50, 255, 50), pygame.K_s),
        Key(433, 520, (100, 100, 255), (50, 50, 255), pygame.K_d),
        Key(600, 520, (255, 255, 100), (255, 255, 50), pygame.K_f)
    ]

    def create_particles(x, y, color, count=10):
        for _ in range(count):
            velocity = (
                (pygame.time.get_ticks() % 10 - 5) * 2,
                (pygame.time.get_ticks() % 10 - 5) * 2
            )
            particles.append(Particle(x, y, color, velocity))

    def load(filename):
        rects = []
        mixer.init()
        mixer.music.load(filename + ".mp3")
        mixer.music.play()
        f = open(filename + ".txt", "r")
        data = f.readlines()
        
        for y in range(len(data)):
            for x in range(len(data[y])):
                if data[y][x] == "0":
                    rects.append(pygame.Rect(keys[x].rect.x, y*-100, 100, 60))
        return rects

    def draw_health_bar():
        # Background
        health_bg = pygame.Rect(20, 20, 200, 20)
        pygame.draw.rect(win, (100, 0, 0), health_bg)
        
        # Health fill
        health_width = int(200 * (health / max_health))
        health_fill = pygame.Rect(20, 20, health_width, 20)
        
        # Color changes based on health
        if health > 70:
            health_color = (0, 255, 0)
        elif health > 30:
            health_color = (255, 255, 0)
        else:
            health_color = (255, 0, 0)
            
        pygame.draw.rect(win, health_color, health_fill)
        pygame.draw.rect(win, (255, 255, 255), health_bg, 2)
        
        # Health text
        font_obj = pygame.font.Font(font_path, 24)
        health_text = font_obj.render(f"HP: {health}/{max_health}", True, (255, 255, 255))
        win.blit(health_text, (23, 50))

    def draw_combo_display():
        global combo_display_timer
        
        # Combo counter
        font_obj = pygame.font.Font(font_path, 48)
        combo_text = font_obj.render(f"COMBO: {combo_count}", True, (255, 255, 100))
        win.blit(combo_text, (SCREEN_WIDTH - 250, 20))
        
        # Max combo
        font_small = pygame.font.Font(font_path, 24)
        max_combo_text = font_small.render(f"MAX: {max_combo}", True, (200, 200, 200))
        win.blit(max_combo_text, (SCREEN_WIDTH - 250, 70))
        
        # Score
        score_text = font_obj.render(f"SCORE: {score}", True, (255, 255, 255))
        win.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 20))
        
        # Combo multiplier effect
        if combo_count > 10:
            multiplier = min(combo_count // 10, 5)
            mult_text = font_small.render(f"x{multiplier} MULTIPLIER!", True, (255, 100, 255))
            win.blit(mult_text, (SCREEN_WIDTH - 250, 95))

    def draw_background():
        # Animated background
        time = pygame.time.get_ticks() / 1000
        for i in range(0, SCREEN_WIDTH, 50):
            color_shift = int(50 * math.sin(time + i * 0.01))
            color = (
                max(0, min(255, BACKGROUND[0] + color_shift)),
                max(0, min(255, BACKGROUND[1] + color_shift // 2)),
                max(0, min(255, BACKGROUND[2] + color_shift // 3))
            )
            pygame.draw.rect(win, color, (i, 0, 50, SCREEN_HEIGHT))

    try:
        map_rects = load("resources/WienerDog")
    except:
        print("Could not load song file, using empty map")
        map_rects = []

    def pause():
        paused = True
        pygame.mixer.music.pause()
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    quit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                        paused = False
                        pygame.mixer.music.unpause()
            
            win.fill((0, 0, 0))
            font_obj = pygame.font.Font(font_path, 74)
            text = font_obj.render("PAUSED", True, (255, 255, 255))
            win.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
            
            resume_text = pygame.font.Font(font_path, 36).render("Press SPACE or ESC to resume", True, (200, 200, 200))
            win.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            
            pygame.display.update()
            clock.tick(FPS)

    # Main game loop
    while run:
        draw_background()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    pause()

        k = pygame.key.get_pressed()
        
        # Update keys
        for key in keys:
            key.update()
            key.draw(win, k[key.key])
        
        # Update and draw notes
        notes_to_remove = []
        for rect in map_rects[:]:  # Create a copy to iterate over
            pygame.draw.rect(win, (200, 100, 255), rect)
            pygame.draw.rect(win, (255, 255, 255), rect, 2)
            rect.y += 7
            
            hit = False
            for key in keys:
                if rect.colliderect(key.rect) and k[key.key]:
                    # Perfect hit
                    combo_count += 1
                    max_combo = max(max_combo, combo_count)
                    multiplier = min(combo_count // 10 + 1, 5)
                    score += 100 * multiplier
                    
                    key.glow_intensity = 100
                    key.hit_animation = 10
                    
                    create_particles(rect.centerx, rect.centery, key.colour1, 15)
                    hit_effects.append(HitEffect(rect.centerx, rect.centery, "perfect"))
                    
                    map_rects.remove(rect)
                    hit = True
                    break
            
            # Check if note missed (went too far down)
            if rect.y > SCREEN_HEIGHT:
                combo_count = 0
                health -= 10
                missed_notes += 1
                hit_effects.append(HitEffect(rect.centerx, HIT_ZONE_Y, "miss"))
                map_rects.remove(rect)
                
                if health <= 0:
                    quest_failed = True
                    # Game over logic could go here
        
        # Update and draw particles
        particles = [p for p in particles if p.life > 0]
        for particle in particles:
            particle.update()
            particle.draw(win)
        
        # Update and draw hit effects
        hit_effects = [effect for effect in hit_effects if effect.timer > 0]
        for effect in hit_effects:
            effect.update()
            effect.draw(win)
        
        # Draw UI elements
        draw_health_bar()
        draw_combo_display()
        
        # Draw hit zone indicator
        for key in keys:
            hit_zone = pygame.Rect(key.x, HIT_ZONE_Y - 30, 100, 60)
            pygame.draw.rect(win, (*key.colour1, 50), hit_zone)
            pygame.draw.rect(win, key.colour1, hit_zone, 2)

        if k[pygame.K_r] and quest_failed:
            map_rects = load("resources/WienerDog")
            run = True
            quest_result = None
            combo_count = 0
            max_combo = 0
            health = 100
            max_health = 100
            score = 0
            missed_notes = 0
            quest_failed = False
            
                    
        if quest_failed:
            # Quest failed screen
            draw_background()
            pygame.mixer.music.pause()
            fail_text = font_large.render("QUEST FAILED!", True, (255, 50, 50))
            fail_rect = fail_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            win.blit(fail_text, fail_rect)
            
            reason_text = font_medium.render("Too many notes missed!", True, (255, 100, 100))
            reason_rect = reason_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            win.blit(reason_text, reason_rect)
            
            score_text = font_medium.render(f"Final Score: {score:,}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            win.blit(score_text, score_rect)
            
            retry_text = font_small.render("Press R to restart", True, (200, 200, 200))
            retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
            win.blit(retry_text, retry_rect)
            
            quest_result = 'lose'
        
        elif len(map_rects) == 0 and music_started:
            # Display final score
            draw_background()
            final_text = font_large.render("SONG COMPLETE!", True, (255, 255, 100))
            final_rect = final_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            win.blit(final_text, final_rect)
            
            score_text = font_medium.render(f"Final Score: {score:,}", True, (255, 255, 255))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            win.blit(score_text, score_rect)
            
            
            max_combo_text = font_medium.render(f"Max Combo: {max_combo}", True, (255, 255, 255))
            max_combo_rect = max_combo_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            win.blit(max_combo_text, max_combo_rect)
            
            quest_result = 'win'
            
        
        pygame.display.update()
        clock.tick(FPS)
    return quest_result

play_fourth_quest()