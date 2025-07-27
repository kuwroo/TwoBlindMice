import pygame
import math
import time
from pygame import mixer
from pygame import font
pygame.font.init()

# Constants (assuming these from your misc.py)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

clock = pygame.time.Clock()
win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("RAT AND ROLL!")
print("RAT AND ROLL!")

game_started = False
HIT_ZONE_Y = SCREEN_HEIGHT - 100
HIT_ZONE_WIDTH = 25
FPS = 60
PROGRESS_BAR_WIDTH = SCREEN_WIDTH
PROGRESS_BAR_Y = SCREEN_HEIGHT - 50

# Enhanced colors and graphics
BACKGROUND = (10, 15, 35)
NOTE_COLORS = [
    (255, 100, 100),  # Red
    (100, 255, 100),  # Green  
    (100, 100, 255),  # Blue
    (255, 255, 100)   # Yellow
]
NOTE_PRESSED_COLORS = [
    (255, 200, 200),  # Light Red
    (200, 255, 200),  # Light Green
    (200, 200, 255),  # Light Blue
    (255, 255, 200)   # Light Yellow
]

# Game state variables
combo = 0
max_combo = 0
score = 0
total_notes = 0
notes_hit = 0
notes_missed = 0
accuracy = 100.0
game_time = 0
music_started = False

# Health system
max_health = 100
current_health = max_health
health_loss_per_miss = 20  # Lose 20 health per missed note
quest_failed = False

# Fonts
font_large = pygame.font.Font(None, 48)
font_medium = pygame.font.Font(None, 36)
font_small = pygame.font.Font(None, 24)

# BPM settings for "Wiener Dog" song (adjust as needed)
BPM = 120  # Typical BPM, adjust based on actual song
BEAT_INTERVAL = 60.0 / BPM  # Seconds per beat
NOTE_SPEED = 3  # Reduced from 5 to make notes easier to see and hit

class Key:
    def __init__(self, x, y, colour1, colour2, key, letter):
        self.x = x
        self.y = y
        self.colour1 = colour1
        self.colour2 = colour2
        self.key = key
        self.letter = letter
        self.rect = pygame.Rect(x, y, 100, 40)
        self.pressed = False
        self.hit_effect_timer = 0
        self.hit_effect_alpha = 0
    
    def draw(self, surface, pressed):
        # Draw key background with gradient effect
        color = self.colour2 if pressed else self.colour1
        
        # Main key
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 3)
        
        # Letter on key
        text = font_medium.render(self.letter, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)
        
        # Hit effect
        if self.hit_effect_timer > 0:
            effect_rect = pygame.Rect(self.rect.x - 10, self.rect.y - 10, 
                                    self.rect.width + 20, self.rect.height + 20)
            pygame.draw.rect(surface, (*color, self.hit_effect_alpha), effect_rect, 5)
            self.hit_effect_timer -= 1
            self.hit_effect_alpha = max(0, self.hit_effect_alpha - 15)
    
    def trigger_hit_effect(self):
        self.hit_effect_timer = 10
        self.hit_effect_alpha = 255

class Note:
    def __init__(self, x, y, key_index):
        self.x = x
        self.y = y
        self.key_index = key_index
        self.rect = pygame.Rect(x, y, 100, 60)
        self.hit = False
        self.missed = False
        self.glow_effect = 0
    
    def update(self):
        self.y += NOTE_SPEED
        self.glow_effect = (self.glow_effect + 5) % 360  # Rotating glow
        
        # Check if note is missed (passed the hit zone)
        if self.y > SCREEN_HEIGHT and not self.hit:
            self.missed = True
            global current_health, notes_missed, quest_failed
            current_health -= health_loss_per_miss
            notes_missed += 1
            
            # Check if quest failed
            if current_health <= 0:
                quest_failed = True
                current_health = 0
            
            return True
        return False
    
    def draw(self, surface):
        
        if self.hit:
            return
        
        # Calculate glow intensity
        glow_intensity = (math.sin(math.radians(self.glow_effect)) + 1) / 2
        base_color = NOTE_COLORS[self.key_index]
        
        # Create glowing effect
        glow_color = [min(255, int(c + glow_intensity * 50)) for c in base_color]
        
        # Draw note with glow
        glow_rect = pygame.Rect(self.rect.x - 5, self.rect.y - 5, 
                               self.rect.width + 10, self.rect.height + 10)
        pygame.draw.rect(surface, glow_color, glow_rect, border_radius=10)
        pygame.draw.rect(surface, base_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, (255, 255, 255), self.rect, 2, border_radius=8)
        
        # Draw musical note symbol
        note_symbol = "♪"
        text = font_medium.render(note_symbol, True, (255, 255, 255))
        text_rect = text.get_rect(center=self.rect.center)
        surface.blit(text, text_rect)

# Initialize keys with letters
keys = [
    Key(100, 520, NOTE_COLORS[0], NOTE_PRESSED_COLORS[0], pygame.K_a, "A"),
    Key(266, 520, NOTE_COLORS[1], NOTE_PRESSED_COLORS[1], pygame.K_s, "S"),
    Key(433, 520, NOTE_COLORS[2], NOTE_PRESSED_COLORS[2], pygame.K_d, "D"),
    Key(600, 520, NOTE_COLORS[3], NOTE_PRESSED_COLORS[3], pygame.K_f, "F")
]

def load_song(filename):
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
                
map_notes = load_song("resources/WienerDog")
                
                    # Changed from 60 to 40 pixels apart
                    #note = Note(keys[x].rect.x, note_y, x)
                    #notes.append(note)
                    #total_notes += 1
         
def check_hit(note, key_pressed, key_index):
    global combo, score, notes_hit, accuracy
    
    if not key_pressed or note.key_index != key_index:
        return False
    
    # Check if note is in hit zone
    hit_zone_center = HIT_ZONE_Y + 20
    distance = abs(note.rect.centery - hit_zone_center)
    
    if distance <= 30:  # Hit zone tolerance
        note.hit = True
        combo += 1
        notes_hit += 1
        
        # Score based on accuracy and combo
        base_score = 100
        accuracy_bonus = max(0, 100 - distance * 3)  # Closer = more points
        combo_bonus = min(combo * 10, 500)  # Combo multiplier capped at 50x
        
        score += int(base_score + accuracy_bonus + combo_bonus)
        
        # Update accuracy
        accuracy = (notes_hit / max(1, notes_hit + notes_missed)) * 100
        
        # Trigger visual effect
        keys[key_index].trigger_hit_effect()
        
        return True
    return False

def reset_combo():
    global combo, max_combo
    max_combo = max(max_combo, combo)
    combo = 0

def draw_ui(surface):
    global combo, score, accuracy, max_combo, current_health, max_health
    
    # Background gradient
    for y in range(SCREEN_HEIGHT):
        color_intensity = int(20 + (y / SCREEN_HEIGHT) * 15)
        color = (color_intensity, color_intensity // 2, color_intensity * 2)
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))
    
    # Draw hit zone
    hit_zone_rect = pygame.Rect(50, HIT_ZONE_Y, SCREEN_WIDTH - 100, 60)
    pygame.draw.rect(surface, (100, 100, 100, 100), hit_zone_rect)
    pygame.draw.rect(surface, (255, 255, 255), hit_zone_rect, 2)
    
    # Draw lanes
    for i, key in enumerate(keys):
        lane_rect = pygame.Rect(key.x, 0, 100, HIT_ZONE_Y)
        pygame.draw.rect(surface, (30, 30, 50, 50), lane_rect)
        pygame.draw.rect(surface, (100, 100, 150), lane_rect, 1)
    
    # Health bar
    health_bar_width = 200
    health_bar_height = 20
    health_bar_x = SCREEN_WIDTH - health_bar_width - 20
    health_bar_y = 150
    
    # Health bar background
    pygame.draw.rect(surface, (100, 0, 0), 
                    (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    
    # Health bar fill
    health_percent = current_health / max_health
    health_fill_width = int(health_bar_width * health_percent)
    
    # Color based on health level
    if health_percent > 0.6:
        health_color = (0, 255, 0)  # Green
    elif health_percent > 0.3:
        health_color = (255, 255, 0)  # Yellow
    else:
        health_color = (255, 0, 0)  # Red
    
    pygame.draw.rect(surface, health_color, 
                    (health_bar_x, health_bar_y, health_fill_width, health_bar_height))
    
    # Health bar border
    pygame.draw.rect(surface, (255, 255, 255), 
                    (health_bar_x, health_bar_y, health_bar_width, health_bar_height), 2)
    
    # Health text
    health_text = font_small.render(f"Health: {current_health}/{max_health}", True, (255, 255, 255))
    surface.blit(health_text, (health_bar_x, health_bar_y - 25))
    
    # Combo counter
    if combo > 0:
        combo_text = font_large.render(f"COMBO: {combo}", True, (255, 255, 100))
        combo_shadow = font_large.render(f"COMBO: {combo}", True, (100, 100, 50))
        surface.blit(combo_shadow, (SCREEN_WIDTH - 252, 52))
        surface.blit(combo_text, (SCREEN_WIDTH - 250, 50))
        
        # Combo streak effect
        if combo > 10:
            streak_text = font_medium.render("STREAK!", True, (255, 100, 100))
            surface.blit(streak_text, (SCREEN_WIDTH - 200, 100))
    
    # Score
    score_text = font_medium.render(f"Score: {score:,}", True, (255, 255, 255))
    surface.blit(score_text, (20, 20))
    
    # Max combo
    max_combo_text = font_small.render(f"Max Combo: {max_combo}", True, (200, 200, 200))
    surface.blit(max_combo_text, (20, 60))
    
    # Accuracy
    accuracy_color = (100, 255, 100) if accuracy >= 90 else (255, 255, 100) if accuracy >= 70 else (255, 100, 100)
    accuracy_text = font_small.render(f"Accuracy: {accuracy:.1f}%", True, accuracy_color)
    surface.blit(accuracy_text, (20, 90))
    
    # Notes missed counter
    missed_text = font_small.render(f"Missed: {notes_missed}", True, (255, 100, 100))
    surface.blit(missed_text, (20, 120))
    
    # Progress bar
    if total_notes > 0:
        progress = max(0, 1 - len(map_notes) / total_notes)
        progress_width = int(PROGRESS_BAR_WIDTH * progress)
        
        pygame.draw.rect(surface, (50, 50, 50), 
                        (0, PROGRESS_BAR_Y, PROGRESS_BAR_WIDTH, 30))
        pygame.draw.rect(surface, (100, 255, 100), 
                        (0, PROGRESS_BAR_Y, progress_width, 30))
        pygame.draw.rect(surface, (255, 255, 255), 
                        (0, PROGRESS_BAR_Y, PROGRESS_BAR_WIDTH, 30), 2)
        
        progress_text = font_small.render(f"{progress * 100:.1f}%", True, (255, 255, 255))
        surface.blit(progress_text, (PROGRESS_BAR_WIDTH // 2 - 20, PROGRESS_BAR_Y + 5))

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
        
        # Draw pause screen
        win.fill((0, 0, 20))
        
        pause_text = font_large.render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        win.blit(pause_text, pause_rect)
        
        instruction_text = font_medium.render("Press ESC or SPACE to continue", True, (200, 200, 200))
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        win.blit(instruction_text, instruction_rect)
        
        pygame.display.update()
        clock.tick(FPS)

# Load the song and notes
print("Loading song...")
map_notes = load_song("resources/WienerDog")


for rect in map_notes:
        pygame.draw.rect(win, (200, 0, 250), rect)
        rect.y += 7
        for key in keys:
            if rect.colliderect(key.rect) and k[key.key]:
                pygame.draw.rect(win, (255, 255, 255), key.rect)
                map_notes.remove(rect)
try:
    mixer.music.play()
    music_started = True
    print("Music started playing")
except:
    print("Could not play music, but notes will still work")
    music_started = True  # Allow game to continue without music


# Game loop
run = True
quest_result = None

while run:
    game_time += clock.get_time() / 1000.0  # Convert to seconds
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                pause()
    
    # Get pressed keys
    k = pygame.key.get_pressed()
    
    # Clear screen and draw UI
    win.fill(BACKGROUND)
    draw_ui(win)
    
    # Draw and update keys
    for i, key in enumerate(keys):
        pressed = k[key.key]
        key.draw(win, pressed)
    
    # Update and draw notes
    notes_to_remove = []
    notes_visible = 0
    
    for note in map_notes[:]:  # Create a copy to iterate over
        # Count visible notes for debugging
        if note.y > -100 and note.y < SCREEN_HEIGHT:
            notes_visible += 1
            
        if note.update():  # Note missed
            reset_combo()
            notes_to_remove.append(note)
            continue
        
        for note in map_notes:
            pygame.draw.rect(win, (200, 0, 250), note.rect)

        
        # Check for hits
        for i, key in enumerate(keys):
            if k[key.key] and check_hit(note, True, i):
                notes_to_remove.append(note)
                break
    
    # Debug info - show next few notes
    if len(map_notes) > 0:
        next_notes_info = []
        for note in map_notes[:5]:  # Show info for next 5 notes
            key_name = ['A', 'S', 'D', 'F'][note.key_index]
            next_notes_info.append(f"{key_name}:{int(note.y)}")
        
        debug_text = font_small.render(f"Next notes: {', '.join(next_notes_info)}", True, (255, 255, 0))
        win.blit(debug_text, (20, 150))
        
        # Show when first note will be visible
        first_note = min(map_notes, key=lambda n: n.y)
        if first_note.y < 0:
            frames_until_visible = abs(first_note.y) // NOTE_SPEED
            seconds_until_visible = frames_until_visible / 60
            time_text = font_small.render(f"First note in {seconds_until_visible:.1f}s", True, (200, 200, 200))
            win.blit(time_text, (3, 175))
    
    # Remove processed notes
    for note in notes_to_remove:
        if note in map_notes:
            map_notes.remove(note)
    
    # Check if song is finished or quest failed
    if quest_failed:
        # Quest failed screen
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
        
        # Handle restart
        if k[pygame.K_r]:
            # Reset game state
            combo = 0
            max_combo = 0
            score = 0
            notes_hit = 0
            notes_missed = 0
            accuracy = 100.0
            current_health = max_health
            quest_failed = False
            map_notes = load_song("resources/WienerDog")
            if map_notes:
                mixer.music.play()
                music_started = True
        
    elif len(map_notes) == 0 and music_started:
        # Display final score
        final_text = font_large.render("SONG COMPLETE!", True, (255, 255, 100))
        final_rect = final_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        win.blit(final_text, final_rect)
        
        score_text = font_medium.render(f"Final Score: {score:,}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        win.blit(score_text, score_rect)
        
        accuracy_text = font_medium.render(f"Accuracy: {accuracy:.1f}%", True, (255, 255, 255))
        accuracy_rect = accuracy_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        win.blit(accuracy_text, accuracy_rect)
        
        max_combo_text = font_medium.render(f"Max Combo: {max_combo}", True, (255, 255, 255))
        max_combo_rect = max_combo_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        win.blit(max_combo_text, max_combo_rect)
        
        # Determine quest result based on performance
        if accuracy >= 80 and notes_missed <= 5:
            quest_result = "EXCELLENT"
            result_color = (100, 255, 100)
        elif accuracy >= 60 and notes_missed <= 15:
            quest_result = "GOOD"
            result_color = (255, 255, 100)
        else:
            quest_result = "PASSED"
            result_color = (255, 150, 100)
        
        result_text = font_medium.render(f"Grade: {quest_result}", True, result_color)
        result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
        win.blit(result_text, result_rect)
    
    pygame.display.update()
    clock.tick(FPS)

pygame.quit()