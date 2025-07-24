# #this is a placeholder for the quest 4 code
import pygame
from misc import *
from pygame import mixer
from pygame import font


# class Quest4:
#     def __init__(self):
#         self.quest_result = None
#         self.quest_completed = False
#         self.quest_failed = False

        
        
    
#     def fireball_shoot(self):
#         pass
    
#     def fireball_hit(self):
#         pass
        
#     def run(self):
#         pass
        
# class Fireball:
#     def __init__(self):
#         self.image = pygame.image.load("resources/fireball.png").convert_alpha()
#         self.image = pygame.transform.scale(self.image, (32 * 3, 32 * 3))
#         self.rect = self.image
#         self.origin = (0,0)
#         self.speed = 5
    
#     def set_target(self):
#         return (self.player_x, self.player_y)
    
#     def fire
pygame.font.init()

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
BACKGROUND = (0, 20, 50)
#pygame.transform.scale(pygame.image.load("resources/quest4_background.png").convert(), (SCREEN_WIDTH, SCREEN_HEIGHT))
 

run = True
quest_result = None
    
class Key():
    def __init__(self, x, y, colour1, colour2, key):
        self.x = x
        self.y = y
        self.colour1 = colour1
        self.colour2 = colour2
        self.key = key
        self.rect = pygame.Rect(x, y, 100, 40)
        
        # def update(self, elapsed_time, combo):
        #     if not self.hit:
keys = [
    Key(100, 520, (255, 0, 0), (200, 0, 0), pygame.K_a),
    Key(266, 520, (0, 255, 0), (0, 200, 0), pygame.K_s),
    Key(433, 520, (0, 0, 255), (0, 0, 200), pygame.K_d),
    Key(600, 520, (255, 255, 0), (200, 200, 0), pygame.K_f)
]

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
                
map_rects = load("resources/WienerDog")
                


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
        font = pygame.font.Font(None, 74)
        text = font.render("PAUSED", True, (255, 255, 255))
        win.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
        pygame.display.update()
        clock.tick(FPS)             
 
 

                   
        
    
    
while True:
    
    # font = pygame.font.Font(None, 74)
    # text = font.render("PRESS SPACE TO START", True, (255, 255, 255))
    # win.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - text.get_height() // 2))
    # pygame.display.update()
    
    win.fill((0,0,0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        
        
    

        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                pause()

    k = pygame.key.get_pressed()
    for key in keys:
        if k[key.key]:
            pygame.draw.rect(win, key.colour2, key.rect)
        else:
            pygame.draw.rect(win, key.colour1, key.rect)
    
    for rect in map_rects:
        pygame.draw.rect(win, (200, 0, 250), rect)
        rect.y += 7
        for key in keys:
            if rect.colliderect(key.rect) and k[key.key]:
                pygame.draw.rect(win, (255, 255, 255), key.rect)
                map_rects.remove(rect)
               
                    # Here you can add logic for what happens when a key is hit
                    # e.g., increase score, play sound, etc.
          
    pygame.display.update()
    clock.tick(FPS)
            
        
        


        
        
    