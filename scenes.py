import pygame
from misc import SCREEN_WIDTH, SCREEN_HEIGHT
from tilemap import TileMap
from player import PlayerMovement
from cursor import Cursor
from visibility import FogOfWar
from quest import *
from button import Button
from camera import Camera
import pytmx
import pickle
import os
import math
import random

SAVE_FILE = "savegame.sav"

class Scene:
    """Base class for all game scenes with common functionality."""
    
    def __init__(self, screen, tilemap_path):
        self.screen = screen
        self.tile_map = TileMap(tilemap_path)
        # Player movement based on map width
        self.player = PlayerMovement(SCREEN_WIDTH, SCREEN_HEIGHT, self.tile_map.width)
        self.cursor = Cursor()
        self.fog = FogOfWar()
        # Initialize camera with tilemap dimensions
        self.camera = Camera(self.player, self.tile_map.width, self.tile_map.height)
        self.camera_offset = self.camera.offset  # Initialize camera_offset with camera's offset
        self.font = pygame.font.Font(None, 36)  # Initialize font here since multiple scenes use it
        
    def handle_input_and_gravity(self, keys):
        """Common input handling and gravity application."""
        self.player.handle_input(keys)
        self.player.apply_gravity()
        
    def update_player_position(self, keys):
        """Common player position update logic."""
        # Use the pre-loaded rectangles from TileMap
        self.player.update_position(self.tile_map.floor_rects, self.tile_map.ladder_rects)
        self.player.update_animation(keys)
        
    def center_camera_on_player(self):
        """Update camera position."""
        self.camera_offset = self.camera.scroll()
        
    def draw_prompt(self, screen):
        """Draw interaction prompt if it exists."""
        prompt_text = self.tile_map.get_interaction_prompt(self.player.rect)
        if prompt_text:
            font = pygame.font.Font(None, 36)
            text = font.render(prompt_text, True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(text, text_rect)

class TitleScene(Scene):
    def __init__(self, screen):
        super().__init__(screen, "resources/entry.tmx")
        #print("Loaded tilemap, interactables:", self.tile_map.interactables)  # Debug print
        self.is_mouse = True
        self.cursor = Cursor()
        
        
        # Create buttons
        button_width = 200
        button_height = 50
        # Center the start button
        start_x = (SCREEN_WIDTH - button_width) // 2
        start_y = (SCREEN_HEIGHT - button_height) // 2
        self.start_button = Button(start_x, start_y, button_width, button_height, "Start Mouse")
        
        # Position the game button below the start button
        game_y = start_y + button_height + 20  # 20 pixels padding
        self.game_button = Button(start_x, game_y, button_width, button_height, "Enter Game")
        
        self.npcs = self.tile_map.load_npcs()
        self.NPC_interacted = False

  
    def handle_event(self, event):
        if self.is_mouse:
            # Handle start button click to switch to player mouse
            if self.start_button.handle_event(event):
                print("Start button clicked - switching to mouse control")
                self.cursor.is_mouse = False
                # Set player position to screen center
                self.player.player_x = SCREEN_WIDTH // 2
                self.player.player_y = SCREEN_HEIGHT // 2
                self.player.rect.topleft = (self.player.player_x, self.player.player_y)
                self.is_mouse = False
                return None
        else:  
            self.cursor.is_mouse = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                    for npc in self.npcs:
                        if npc.showing_dialogue:
                            result = npc.dialogue.handle_input(event.key)
                            if result == "CLOSE":
                                npc.showing_dialogue = False
                                self.player.can_move = True
                                # Check if dialogue is completely finished
                                if npc.name == "SusMouse":  # example NPC name, adapt as needed
                                    result = "SWITCH_TO_GAME"
                                # Otherwise continue the dialogue
                                return result
                            # Handle other dialogue results if needed
                       
                
                # Check for NPC interaction if no dialogue is active (only if no NPC is showing dialogue)
                if not any(npc.showing_dialogue for npc in self.npcs):
                    if event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):
                        for npc in self.npcs:
                            if npc.is_near_player(self.player.rect):
                                npc.interact()
                                return "NPC_INTERACTED"

        return None
    
    def update(self):
        keys = pygame.key.get_pressed()
        if self.is_mouse:
            self.cursor.update()
            self.start_button.update_position(self.camera_offset)
        else:
            # Use common update logic from superclass
            # Use common update logic from superclass
            if any(npc.showing_dialogue for npc in self.npcs):
                self.player.can_move = False
            self.handle_input_and_gravity(keys)
            self.update_player_position(keys)
            self.center_camera_on_player()
        return None
        
        
    def draw(self, screen):
        screen.fill((30, 30, 30))
        self.tile_map.draw(screen, self.camera_offset)
        
        # Update and draw fog of war
        self.fog.visibility_radius = 0  # No fog in title scene
        self.fog.update((self.player.rect.centerx, self.player.rect.centery), self.camera_offset)
        self.fog.draw(screen)
        # Load image
        my_image = pygame.image.load("resources/title.png").convert_alpha()

        # World coordinates of image (e.g., a piece of cheese)
        cheese_pos = pygame.Vector2(300, 200)

        # Camera position (moves as player moves)
        camera_x = self.player.rect.centerx - SCREEN_WIDTH // 2
        camera_y = self.player.rect.centery - SCREEN_HEIGHT // 2
        camera_offset = pygame.Vector2(camera_x, camera_y)

        # Convert world to screen position
        screen_pos = cheese_pos - camera_offset

        # Draw
        screen.blit(my_image, screen_pos)

        if self.is_mouse:
            self.start_button.draw(screen)
            self.cursor.draw()
        else:
            
            
            
            self.player.draw(screen, pygame.key.get_pressed(), self.camera_offset)
        
        
        # Draw interaction prompt if it exists
        self.draw_prompt(screen)
        # Let each NPC handle its own update and draw
        current_time = pygame.time.get_ticks()
        for npc in self.npcs:
            npc.update(current_time)
            npc.draw(screen, self.camera_offset)
            
         
        
        
              
            
class GameScene(Scene):
    
    def __init__(self, screen):
        super().__init__(screen, "resources/sewermap.tmx")
        # Set initial spawn position higher
        self.player.player_y = SCREEN_HEIGHT // 4
        self.player.rect.topleft = (self.player.player_x, self.player.player_y)
        self.fog = FogOfWar()
        self.boss_entry_zone = None

        #sprites and NPCS
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.npcs = self.tile_map.load_npcs()
        self.cheese_count = 1
        # to edit!!
        self.cheese_sprite = pygame.image.load("resources/cheese.png")
        self.cheese_sprite = pygame.transform.scale(self.cheese_sprite, (24, 24))
        self.quest1_completed = False
        self.quest2_completed = False
        self.quest3_completed = False
        self.quest4_completed = False
        self.player_start_tile = (0, 0)  # Default value
        self.load_game()  # ✅ Auto-load on creation
        # After self.tile_map is initialized
        for obj in self.tile_map.tmx_data.objects:
            if obj.name == "boss_entry_zone":
                self.boss_entry_zone = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
    
    def save_game(self):
        data = {
            'player_position': self.player.rect.topleft,
            'cheese_count': self.cheese_count,
            'quest1_completed': self.quest1_completed,
            'quest2_completed': self.quest2_completed,
            'quest3_completed': self.quest3_completed,
            'quest4_completed': self.quest4_completed
        }
        with open(SAVE_FILE, 'wb') as f:
            pickle.dump(data, f)
        print("Game saved.")

    def load_game(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'rb') as f:
                data = pickle.load(f)
                self.player.rect.topleft = data['player_position']
                self.player.player_x, self.player.player_y = data['player_position']
                self.cheese_count = data['cheese_count']
                self.quest1_completed = data['quest1_completed']
                self.quest2_completed = data['quest2_completed']
                self.quest3_completed = data['quest3_completed']
                self.quest4_completed = data['quest4_completed']
                print("Game loaded.")
        else:
            print("No save file found.")
  
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # 1. Handle dialogue input (if any NPC is showing dialogue)
            if event.key in (pygame.K_e, pygame.K_SPACE, pygame.K_RETURN):  # Added K_RETURN here
                for npc in self.npcs:
                    if npc.showing_dialogue:
                        result = npc.dialogue.handle_input(event.key)
                        if result == "CLOSE":
                            npc.showing_dialogue = False
                            self.player.can_move = True
                            return result
                        elif result == "PLAY_QUEST":
                            npc.showing_dialogue = False
                            self.player.can_move = True
                            # Start the quest related to this NPC
                            if npc.name == "Frog":  # example NPC name, adapt as needed
                                print("Starting Pac-mouse...")
                                result = play_second_quest()
                                if result == "win" and not self.quest2_completed:
                                    self.cheese_count += 1
                                    self.quest2_completed = True
                                    self.save_game()
                                    
                            elif npc.name == "Rabbit":  # example NPC name, adapt as needed
                                print("Starting Rabbit-hole...")
                                result = play_first_quest()
                                if result == "win" and not self.quest1_completed:
                                    self.cheese_count += 1
                                    self.quest1_completed = True
                                    self.save_game()

                            elif npc.name == "Rat":  # example NPC name, adapt as needed
                                print("Starting Mouse-Heist...")
                                result = play_third_quest()
                                if result == "win" and not self.quest3_completed:
                                    self.cheese_count += 1
                                    self.quest3_completed = True
                                    self.save_game()

                            elif npc.name == "Wiener":  # example NPC name, adapt as needed
                                print("Starting Wiener Mouse...")
                                result = play_fourth_quest()
                                if result == "win" and not self.quest4_completed:
                                    self.cheese_count += 1
                                    self.quest4_completed = True
                                    self.save_game()

                            return "QUEST_STARTED"
                        return result

                # Check for NPC interaction if no dialogue is active
                for npc in self.npcs:
                    if npc.is_near_player(self.player.rect):
                        npc.interact()
                        return "NPC_INTERACTED"
            # After checking NPC interaction...
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                if self.boss_entry_zone and self.boss_entry_zone.colliderect(self.player.rect):
                    if self.cheese_count >= 5:
                        return "ENTER_BOSS"

        return None

   
    def update(self):
        keys = pygame.key.get_pressed()
        
        # Use common update logic from superclass
        if any(npc.showing_dialogue for npc in self.npcs):
            self.player.can_move = False
        self.handle_input_and_gravity(keys)
        self.update_player_position(keys)
        self.center_camera_on_player()
        
        return None

    def draw(self, screen):
        screen.fill((30, 30, 30))
        self.tile_map.draw(screen, self.camera_offset)
        self.player.draw(screen, pygame.key.get_pressed(), self.camera_offset)
        if self.boss_entry_zone and self.boss_entry_zone.colliderect(self.player.rect) and self.cheese_count >= 5:
            font = pygame.font.Font(None, 24)
            prompt = font.render("Press [E] to challenge the Mouse God", True, (255, 255, 0))
            screen.blit(prompt, (self.player.rect.x - 30, self.player.rect.y - 40))

        # Dynamically update fog radius based on cheese count
        self.fog.visibility_radius = 150 + (self.cheese_count - 1) * 40
        
        # Update and draw fog of war
        self.fog.update((self.player.rect.centerx, self.player.rect.centery), self.camera_offset)
        self.fog.draw(screen)
        
        # Draw interaction prompt if it exists
        self.draw_prompt(screen)
        # Let each NPC handle its own update and draw
        current_time = pygame.time.get_ticks()
        for npc in self.npcs:
            npc.update(current_time)
            npc.draw(screen, self.camera_offset)
        
        
        # Draw cheese count
        cheese_x = 10
        cheese_y = 10
        screen.blit(self.cheese_sprite, (cheese_x, cheese_y))
        cheese_text = self.font.render(f"x {self.cheese_count}", True, (255, 255, 255))
        screen.blit(cheese_text, (cheese_x + 30, cheese_y))

class Quest1:
    pass

class Entry(Scene):
    def __init__(self, screen):
        super().__init__(screen, "resources/entry.tmx")
        self.fog = FogOfWar()
        self.fog.visibility_radius = 0 # Set initial visibility radius idk why this doesnt work
        self.player.player_y = SCREEN_HEIGHT // 4
        self.fog = FogOfWar()
        self.all_sprites = pygame.sprite.Group()
        self.all_sprites.add(self.player)
        self.npcs = self.tile_map.load_npcs()

        
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            for npc in self.npcs:
                if npc.is_near_player(self.player.rect):
                    npc.interact()
                    return "NPC_INTERACTED"
                # Implement NPC interaction logic here
        return None
    
    def update(self):
        keys = pygame.key.get_pressed()
        # Use common update logic from superclass
        if any(npc.showing_dialogue for npc in self.npcs):
            self.player.can_move = False
        self.handle_input_and_gravity(keys)
        self.update_player_position(keys)
        self.center_camera_on_player()



        return None
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_e, pygame.K_SPACE):
                for npc in self.npcs:
                    if npc.is_near_player(self.player.rect):
                        npc.interact()
                    if npc.showing_dialogue:
                        result = npc.dialogue.handle_input(event.key)
                        if result == "CLOSE":
                            npc.showing_dialogue = False
                            self.player.can_move = True
                        return result

           
        return None


    def draw(self, screen):
        screen.fill((0, 0, 0))
        self.tile_map.draw(screen, self.camera_offset)
        self.player.draw(screen, pygame.key.get_pressed(), self.camera_offset)
        
        # Update and draw fog of war
        self.fog.update((self.player.rect.centerx, self.player.rect.centery), self.camera_offset)
        self.fog.draw(screen)
        # Draw interaction prompt if it exists
        self.draw_prompt(screen)
        # Let each NPC handle its own update and draw
        current_time = pygame.time.get_ticks()
        for npc in self.npcs:
            npc.update(current_time)
            npc.draw(screen, self.camera_offset)

from player import PlayerMovement
from misc import SCREEN_HEIGHT, SCREEN_WIDTH
import math


# class MouseGodBoss(Scene):
#     WIDTH = SCREEN_WIDTH
#     HEIGHT = SCREEN_HEIGHT
#     def __init__(self, screen):
#         super().__init__(screen, None)  # No TMX map needed
#         self.screen = screen
#         pygame.display.set_caption("Mouse God Boss Battle")
#         self.clock = pygame.time.Clock()
        
#         # Colors
#         self.BLACK = (0, 0, 0)
#         self.WHITE = (255, 255, 255)
#         self.RED = (255, 50, 50)
#         self.ORANGE = (255, 165, 0)
#         self.YELLOW = (255, 255, 0)
#         self.BLUE = (100, 150, 255)
#         self.PURPLE = (150, 50, 200)
#         self.GRAY = (128, 128, 128)
#         self.DARK_RED = (150, 0, 0)
        
#         # Game state
#         self.game_state = "playing"  # "playing", "dead", "victory"
#         self.font = pygame.font.Font(None, 36)
#         self.small_font = pygame.font.Font(None, 24)
#         self.end_state_timer = 0  # counts frames when dead or victory

#         self.boss_frames = self.load_spritesheet('resources/boss.png', 2, 200, 150)
#         self.boss_frames = [pygame.transform.scale(frame, (800, 600)) for frame in self.boss_frames]
        
#         self.attack_frames = self.load_spritesheet('resources/attack.png', 7, 32, 32)
#         self.attack_frames = [pygame.transform.scale(frame, (32*4, 32*4)) for frame in self.attack_frames]
        
#         self.death_frames = self.load_spritesheet('resources/death.png', 7, 32, 32)
#         self.deahth_frames = [pygame.transform.scale(frame, (32*4, 32*4)) for frame in self.death_frames]

#         # Animation state variables
#         self.boss_current_frame = 0
        
#         self.is_attacking = False
#         self.frame_timer = 0
#         self.frame_delay = 6 # Delay for boss animation frames
#         self.death_anim_index = 0
#         self.death_anim_timer = 0
#         self.is_boss_dead = False
        
        
#         self.init_game()
    
#     def init_game(self):
#         # Player
#         self.player = PlayerMovement(self.WIDTH, self.HEIGHT, self.WIDTH)
        
    
#         self.player.PLAYER_SPEED = 7
#         self.player.PLAYER_JUMP_POWER = 1
#         self.player.player_x = self.WIDTH // 2
#         self.player.player_y = 400
#         self.player.rect.topleft = (self.player.player_x, self.player.player_y)
#         self.player_attack_cooldown = 0
#         self.player_attacking = False
#         self.player.allow_attack = True
        
        
      
#         # Mouse God Boss
#         self.boss = {
#             'x': self.WIDTH // 2 - 150,
#             'y': 200,
#             'width': 700,
#             'height':500,
#             'health': 100,
#             'max_health': 100,
#             'shoot_cooldown': 0,
#             'move_timer': 0,
#             'move_direction': 1,
#             'phase': 1 
#         # Gets harder as health decreases
#         }
#         self.boss['x'] = (self.WIDTH - self.boss_frames[0].get_width()) // 2
#         self.boss['y'] = 0
#         self.boss_rect = pygame.Rect(self.boss['x'], self.boss['y'], self.boss['width'], self.boss['height'])
#         self.boss_rect.topleft = (self.boss['x'], self.boss['y'])
        
#         # Projectiles
#         self.fire_cheeseballs = []
        
#     def load_spritesheet(self, image_path, frame_count, frame_width, frame_height):
#         spritesheet = pygame.image.load(image_path)
#         frames = []
#         for i in range(frame_count):
#             frame = spritesheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height))
#             frames.append(frame)
#         return frames    
    

#     # def handle_input(self):
#     #     keys = pygame.key.get_pressed()
#     #     self.player.handle_input(keys)
#     #     for event in pygame.event.get():
#     #         if event.type == pygame.QUIT:
#     #             return False
#     #         elif event.type == pygame.KEYDOWN:
#     #             if event.key == pygame.K_r and self.game_state != "playing":
#     #                 self.restart_game()
#     #             if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT and self.game_state == "playing":
#     #                 self.try_player_attack()
#     #     return True
#     def handle_input(self, event):
#         if event.type == pygame.QUIT:
#             return False  # or handle quit as needed
#         elif event.type == pygame.KEYDOWN:
#             if event.key == pygame.K_r and self.game_state != "playing":
#                 self.restart_game()
#             if self.game_state == "playing":
#                 if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
#                     self.try_player_attack()
#         return True

#     def try_player_attack(self):
#         # Only allow attack if cooldown is 0 and player is near boss
#         if self.player_attack_cooldown == 0:
#             player_rect = self.player.rect
#             # Base size of sword
#             sword_width = 10
#             sword_height = 32

#             # Position: top-right corner of player
#             sword_x = player_rect.right
#             sword_y = player_rect.top

#             # Create sword hitbox
#             sword_hitbox = pygame.Rect(sword_x, sword_y, sword_width, sword_height)

#             # Inflate the hitbox (expand in all directions)
#             sword_hitbox = sword_hitbox.inflate(64 * 3, 64 * 3)

#             boss_rect = self.boss_rect
#             # Check if player is close enough to boss (simple collision or range check)
#             attack_range = 60
#             if sword_hitbox.colliderect(boss_rect.inflate(attack_range, attack_range)):
#                 self.player_attacking = True
#                 self.boss['health'] -= 5
#                 self.player_attack_cooldown = 30  # Cooldown frames
#                 if self.boss['health'] <= 0:
#                     self.game_state = "victory"

#     # def update_player(self):
#     #     if self.game_state != "playing":
#     #         return
#     #     keys = pygame.key.get_pressed()
#     #     self.player.handle_input(keys)
#     #     floor_rects = [pygame.Rect(0, 500, self.WIDTH, 100)]  # Ground at y=500
#     #     ladder_rects = []
#     #     # keys = pygame.key.get_pressed()
#     #     self.player.update_position(floor_rects, ladder_rects)
#     #     self.player.update_animation(keys)
#     #     self.player.apply_gravity()
#     #     if self.player_attack_cooldown > 0:
#     #         self.player_attack_cooldown -= 1
#     #     else:
#     #         self.player_attacking = False
#     def update_player(self):
#         if self.game_state != "playing":
#             return
#         keys = pygame.key.get_pressed()
#         self.player.handle_input(keys)
#         floor_rects = [pygame.Rect(0, 500, self.WIDTH, 100)]  # Ground at y=500
#         ladder_rects = []
#         self.player.update_position(floor_rects, ladder_rects)
#         self.player.update_animation(keys)
#         self.player.apply_gravity()
#         if self.player_attack_cooldown > 0:
#             self.player_attack_cooldown -= 1
#         else:
#             self.player_attacking = False

#     def update_boss(self):
#         if self.game_state != "playing":
#             return
#         # Boss movement (side to side)
#         self.boss['move_timer'] += 1
#         if self.boss['move_timer'] % 120 == 0:
#             self.boss['move_direction'] *= -1
#         self.boss['x'] += self.boss['move_direction'] * 2
#         if self.boss['x'] <= 0 or self.boss['x'] >= self.WIDTH - self.boss['width']:
#             self.boss['move_direction'] *= -1
#         self.boss_rect.topleft = (self.boss['x'], self.boss['y'])
#         # Determine boss phase based on health
#         health_percent = self.boss['health'] / self.boss['max_health']
#         if health_percent > 0.66:
#             self.boss['phase'] = 1
#             shoot_delay = 60
#         elif health_percent > 0.33:
#             self.boss['phase'] = 2
#             shoot_delay = 40
#         else:
#             self.boss['phase'] = 3
#             shoot_delay = 30
#         # Boss shooting
#         if self.boss['shoot_cooldown'] <= 0:
#             self.shoot_fire_cheeseball()
#             self.boss['shoot_cooldown'] = shoot_delay
#         else:
#             self.boss['shoot_cooldown'] -= 1
#     def update(self):
#         if self.game_state == "playing":
#             self.update_player()
#             self.update_boss()
#             self.update_projectiles()
#             self.check_collisions()
#         elif self.game_state in ("dead", "victory"):
#             self.end_state_timer += 1
#             if self.end_state_timer > 120:  # 2 seconds at 60fps
#                 return "POP_SCENE"

#     def shoot_fire_cheeseball(self):
#         # Fireball spawns from boss mouth (center top of boss sprite)
#         mouth_x = self.boss['x'] + 400  # 800 / 2
#         mouth_y = self.boss['y'] + 170 
#         dx = self.player.player_x + self.player.PLAYER_WIDTH // 2 - mouth_x
#         dy = self.player.player_y + self.player.PLAYER_HEIGHT // 2 - mouth_y
#         angle = math.atan2(dy, dx)
#         if self.boss['phase'] >= 2:
#             angle += random.uniform(-0.3, 0.3)
#         speed = 3 + self.boss['phase']
#         cheeseball = {
#             'x': mouth_x,
#             'y': mouth_y,
#             'vx': math.cos(angle) * speed,
#             'vy': math.sin(angle) * speed,
#             'size': 35,  # Larger fireballs
#             'trail': []
#         }
#         self.fire_cheeseballs.append(cheeseball)
#         if self.boss['phase'] == 3 and random.random() < 0.4:
#             for i in range(2):
#                 extra_angle = angle + random.uniform(-0.8, 0.8)
#                 extra_cheeseball = {
#                     'x': mouth_x,
#                     'y': mouth_y,
#                     'vx': math.cos(extra_angle) * speed,
#                     'vy': math.sin(extra_angle) * speed,
#                     'size': 48,
#                     'trail': []
#                 }
#                 self.fire_cheeseballs.append(extra_cheeseball)

#     def update_projectiles(self):
#         for cheeseball in self.fire_cheeseballs[:]:
#             cheeseball['trail'].append((cheeseball['x'], cheeseball['y']))
#             if len(cheeseball['trail']) > 8:
#                 cheeseball['trail'].pop(0)
#             cheeseball['x'] += cheeseball['vx']
#             cheeseball['y'] += cheeseball['vy']
#             if (cheeseball['x'] < -100 or cheeseball['x'] > self.WIDTH + 100 or
#                 cheeseball['y'] < -100 or cheeseball['y'] > self.HEIGHT + 100):
#                 self.fire_cheeseballs.remove(cheeseball)
                
#     def check_collisions(self):
#         if self.game_state != "playing":
#             return
#         def get_shrunk_hitbox(rect, shrink=0.6):
#             w = int(rect.width * shrink)
#             h = int(rect.height * shrink)
#             return pygame.Rect(
#                 rect.centerx - w // 2,
#                 rect.centery - h // 2,
#                 w, h
#             )
#         player_rect = get_shrunk_hitbox(self.player.rect, shrink=0.6)

#         for cheeseball in self.fire_cheeseballs:
#             cheeseball_rect = pygame.Rect(cheeseball['x'] - cheeseball['size']//2,
#                                         cheeseball['y'] - cheeseball['size']//2,
#                                         cheeseball['size']*0.4, cheeseball['size']*0.4)
#             if player_rect.colliderect(cheeseball_rect):
#                 self.game_state = "dead"
#                 return

#     def draw(self, screen):
#         self.screen = screen
#         self.screen.fill((20, 10, 40))
#         for i in range(50):
#             x = (i * 123) % self.WIDTH
#             y = (i * 456) % self.HEIGHT
#             pygame.draw.circle(self.screen, (100, 100, 150), (x, y), 1)
#         if self.game_state == "playing":
#             self.draw_game()
#         elif self.game_state == "dead":
            
#             self.draw_game_over()
#         elif self.game_state == "victory":
#             self.draw_victory()
#         pygame.display.flip()

#     def draw_game(self):
#         # Draw ground
#         pygame.draw.rect(self.screen, (60, 40, 20), (0, 500, self.WIDTH, 100))
#         # Draw player (mouse avatar)
        
#         # Boss death animation
#         if self.boss['health'] <= 0:
#             self.is_boss_dead = True
#         self.frame_timer += 1
#         if self.frame_timer >= self.frame_delay:
#             self.frame_timer = 0
#             if not self.is_boss_dead:
#                 self.boss_current_frame += 1

#         frame_index = self.boss_current_frame % len(self.boss_frames)
#         frame = self.boss_frames[frame_index]
#         self.screen.blit(frame, (self.boss['x'], self.boss['y']))
#         # Draw fire cheeseballs with trails
#         for cheeseball in self.fire_cheeseballs:
#             for i, (tx, ty) in enumerate(cheeseball['trail']):
#                 alpha = (i + 1) / len(cheeseball['trail'])
#                 trail_size = int(cheeseball['size'] * alpha * 0.5)
#                 if trail_size > 0:
#                     pygame.draw.circle(self.screen, self.ORANGE, (int(tx), int(ty)), trail_size)
#             pygame.draw.circle(self.screen, self.YELLOW,
#                              (int(cheeseball['x']), int(cheeseball['y'])), 
#                              cheeseball['size'])
#             pygame.draw.circle(self.screen, self.ORANGE,
#                              (int(cheeseball['x']), int(cheeseball['y'])), 
#                              cheeseball['size'] - 8)
#             pygame.draw.circle(self.screen, self.RED,
#                              (int(cheeseball['x']), int(cheeseball['y'])), 
#                              cheeseball['size'] - 16)
#         self.player.draw(self.screen, pygame.key.get_pressed(), pygame.Vector2(0, 0))
#         # Player attack animation
#         self.draw_ui()

#     def draw_ui(self):
#         bar_width = 300
#         bar_height = 20
#         bar_x = (self.WIDTH - bar_width) // 2
#         bar_y = 20
#         pygame.draw.rect(self.screen, self.BLACK, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
#         pygame.draw.rect(self.screen, self.RED, (bar_x, bar_y, bar_width, bar_height))
#         health_percent = max(0, self.boss['health'] / self.boss['max_health'])
#         fill_width = int(bar_width * health_percent)
#         pygame.draw.rect(self.screen, self.ORANGE, (bar_x, bar_y, fill_width, bar_height))
#         health_text = self.small_font.render(
#             f"Mouse God Health: {self.boss['health']}/{self.boss['max_health']}", 
#             True, self.WHITE)
#         text_rect = health_text.get_rect(center=(self.WIDTH//2, bar_y - 15))
#         self.screen.blit(health_text, text_rect)
#         phase_text = self.small_font.render(f"Phase {self.boss['phase']}", True, self.RED)
#         self.screen.blit(phase_text, (bar_x + bar_width + 10, bar_y))
#         instructions = [
#             "WASD/Arrow Keys: Move",
#             "Space: Attack",
#             "Avoid the fire-cheeseballs!"
#         ]
#         for i, instruction in enumerate(instructions):
#             text = self.small_font.render(instruction, True, self.WHITE)
#             self.screen.blit(text, (10, self.HEIGHT - 80 + i * 25))

#     def draw_game_over(self):
#         self.screen.fill((40, 0, 0))
#         game_over_text = self.font.render("YOU HAVE BEEN CHEESED!", True, self.RED)
#         text_rect = game_over_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 - 50))
#         self.screen.blit(game_over_text, text_rect)
#         subtitle = self.small_font.render("The Mouse God's fire-cheeseballs were too much!", 
#                                         True, self.WHITE)
#         text_rect = subtitle.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
#         self.screen.blit(subtitle, text_rect)
#         restart_text = self.small_font.render("Press R to try again", True, self.WHITE)
#         text_rect = restart_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 50))
#         self.screen.blit(restart_text, text_rect)

#     def draw_victory(self):
#         self.screen.fill((0, 40, 0))
#         victory_text = self.font.render("VICTORY!", True, self.YELLOW)
#         text_rect = victory_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 - 50))
#         self.screen.blit(victory_text, text_rect)
#         subtitle = self.small_font.render("You have defeated the Mouse God!", True, self.WHITE)
#         text_rect = subtitle.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
#         self.screen.blit(subtitle, text_rect)
#         restart_text = self.small_font.render("Press R to play again", True, self.WHITE)
#         text_rect = restart_text.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 50))
#         self.screen.blit(restart_text, text_rect)

#     def restart_game(self):
#         self.game_state = "playing"
#         self.init_game()



import pygame
import math
import random
import sys
from player import PlayerMovement
from misc import SCREEN_HEIGHT, SCREEN_WIDTH


class MouseGodBoss(Scene):
    def __init__(self, screen):
        # Initialize pygame if not already done
        if not pygame.get_init():
            pygame.init()
        
        self.screen = screen
        self.WIDTH = SCREEN_WIDTH
        self.HEIGHT = SCREEN_HEIGHT
        
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
        
        # Load spritesheets
        self.boss_frames = self.load_spritesheet('resources/boss.png', 2, 200, 150)
        self.boss_frames = [pygame.transform.scale(frame, (800, 600)) for frame in self.boss_frames]
        
        self.attack_frames = self.load_spritesheet('resources/attack.png', 7, 32, 32)
        self.attack_frames = [pygame.transform.scale(frame, (32*4, 32*4)) for frame in self.attack_frames]
        
        self.death_frames = self.load_spritesheet('resources/death.png', 7, 32, 32)
        self.death_frames = [pygame.transform.scale(frame, (32*4, 32*4)) for frame in self.death_frames]

        # Animation state variables
        self.boss_current_frame = 0
        self.is_attacking = False
        self.frame_timer = 0
        self.frame_delay = 6  # Delay for boss animation frames
        self.death_anim_index = 0
        self.death_anim_timer = 0
        self.is_boss_dead = False
        self.end_state_timer = 0
        
        self.init_game()
    
    def init_game(self):
        # Player
        self.player = PlayerMovement(self.WIDTH, self.HEIGHT, self.WIDTH)
        self.player.PLAYER_SPEED = 7
        self.player.JUMP_POWER = 10
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
            'height': 500,
            'health': 100,
            'max_health': 100,
            'shoot_cooldown': 0,
            'move_timer': 0,
            'move_direction': 1,
            'phase': 1
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
    
    def handle_event(self, event):
        """Handle events for the boss fight scene"""
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
            elif event.key == pygame.K_q and self.game_state == "paused":
                return "POP_SCENE"  # Return to previous scene
            elif event.key == pygame.K_r and self.game_state != "playing":
                self.restart_game()
            elif self.game_state == "playing":
                if event.key == pygame.K_LSHIFT or event.key == pygame.K_RSHIFT:
                    self.try_player_attack()
        return None

    def try_player_attack(self):
        """Handle player attack logic"""
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
            # Check if player is close enough to boss
            attack_range = 60
            if sword_hitbox.colliderect(boss_rect.inflate(attack_range, attack_range)):
                self.player_attacking = True
                self.boss['health'] -= 5
                self.player_attack_cooldown = 30  # Cooldown frames
                if self.boss['health'] <= 0:
                    self.game_state = "victory"

    def update(self):
        """Update the boss fight scene"""
        
        if self.game_state == "playing":
            self.update_player()
            self.update_boss()
            self.update_projectiles()
            self.check_collisions()
        elif self.game_state == "victory":
            self.end_state_timer += 1
            if self.end_state_timer > 120:  # 2 seconds at 60fps
                return "POP_SCENE"
        return None

    def update_player(self):
        """Update player movement and physics"""
        if self.game_state != "playing":
            return
        floor_rects = [pygame.Rect(0, 500, self.WIDTH, 100)]  # Ground at y=500
        ladder_rects = []
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.update_position(floor_rects, ladder_rects)
        self.player.update_animation(keys)
        self.player.apply_gravity()
        if self.player_attack_cooldown > 0:
            self.player_attack_cooldown -= 1
        else:
            self.player_attacking = False

    def update_boss(self):
        """Update boss movement and behavior"""
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
        """Create fireballs from boss"""
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
            'size': 48,  # Larger fireballs
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
        """Update fireball positions and trails"""
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
        """Check collisions between player and fireballs"""
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

    def draw(self, screen):
        """Draw the boss fight scene"""
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

    def draw_game(self):
        """Draw the main game elements"""
        # Draw ground
        pygame.draw.rect(self.screen, (60, 40, 20), (0, 500, self.WIDTH, 100))
        
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
        self.draw_ui()

    def draw_ui(self):
        """Draw the user interface"""
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
            "WASD/Space: Move",
            "R/LSHIFT: Attack",
            "ESC: Pause",
            "Avoid the fire-cheeseballs!"
        ]
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, self.WHITE)
            self.screen.blit(text, (10, self.HEIGHT - 100 + i * 25))

    def draw_game_over(self):
        """Draw game over screen"""
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
        """Draw victory screen"""
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
        """Draw the pause menu"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.WIDTH, self.HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Menu background
        menu_width = 400
        menu_height = 350
        menu_x = (self.WIDTH - menu_width) // 2
        menu_y = (self.HEIGHT - menu_height) // 2
        
        pygame.draw.rect(self.screen, (50, 50, 50), (menu_x, menu_y, menu_width, menu_height))
        pygame.draw.rect(self.screen, (100, 100, 100), (menu_x, menu_y, menu_width, menu_height), 3)
        
        # Menu title
        title_text = self.settings_font.render("PAUSED", True, self.WHITE)
        title_rect = title_text.get_rect(center=(self.WIDTH//2, menu_y + 50))
        self.screen.blit(title_text, title_rect)
        
        # Menu options
        
        # Menu options
        options = [
            "Press ESC to Resume",
            "Press R to Restart Game",
            "Press Q to Quit"
        ]
        
        for i, option in enumerate(options):
            option_text = self.settings_small_font.render(option, True, self.WHITE)
            option_rect = option_text.get_rect(center=(self.WIDTH//2, menu_y + 120 + i * 40))
            self.screen.blit(option_text, option_rect)

    def restart_game(self):
        """Restart the boss fight"""
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
        self.end_state_timer = 0
        self.init_game()
        

        
        

        
       
        