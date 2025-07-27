import pygame
import random
from misc import SCREEN_WIDTH as WIDTH, SCREEN_HEIGHT as HEIGHT, TILE_SIZE
import sys
from collections import deque
from tilemap import TileMap
from spritesheet_loader import SpriteSheet
from colours import *
from spritesheet_loader import *
import pytmx

def play_first_quest():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rabbit-hole!")
    FPS = 60

    # Load TMX map
    tmx = TileMap("resources/quest1map.tmx")

    # Setup variables
    obstacles = []
    floor_tiles = []
    player = None  # Default to None in case spawn isn't found

    # Find spawn point from object layer
    for obj in tmx.interactables:
        obj_type = obj["type"].lower()
        rect = obj["rect"]
        if obj_type == "spawn":
            PLAYER_SIZE = 32
            player = pygame.Rect(rect.x, rect.y, PLAYER_SIZE, PLAYER_SIZE)

    if player is None:
        raise ValueError("No 'spawn' object found in TMX map. Cannot start quest.")

    # === LOAD FLOOR AND OBSTACLE TILES FROM LAYERS ===
    tilewidth = tmx.tmx_data.tilewidth
    tileheight = tmx.tmx_data.tileheight

    # Get floor tiles (pick the lowest one for landing logic)
    # Get floor tiles (now store all of them)
    floor_layer = tmx.tmx_data.get_layer_by_name("floor")
    for x, y, gid in floor_layer:
        if gid:
            rect = pygame.Rect(x * tilewidth, y * tileheight, tilewidth, tileheight)
            floor_tiles.append(rect)

    # Get obstacle tiles (touch = lose)
    obs_layer = tmx.tmx_data.get_layer_by_name("obs")
    for x, y, gid in obs_layer:
        if gid:
            rect = pygame.Rect(x * tilewidth, y * tileheight, tilewidth, tileheight)
            obstacles.append(rect)

    # Game loop vars
    camera_offset = 0
    clock = pygame.time.Clock()
    run = True
    falling = False
    on_floor = False
    scroll_speed = 8
    player_speed = 7
    quest_result = None
    font = pygame.font.SysFont(None, 24)

    while run:
        clock.tick(FPS)
        win.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quest_result = "quit"

        # Movement logic — no walking through floor tile (not used currently but kept for consistency)
        def can_move(new_rect):
            for tile in floor_tiles:
                tile_shifted = tile.copy()
                tile_shifted.y -= camera_offset
                if new_rect.colliderect(tile_shifted):
                    return False
            return True

        # Input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            new_pos = player.move(-player_speed, 0)
            if can_move(new_pos):
                player = new_pos
        if keys[pygame.K_d]:
            new_pos = player.move(player_speed, 0)
            if can_move(new_pos):
                player = new_pos

        # Begin falling
        if not falling:
            # Check if no floor is under the player
            feet_rect = player.copy()
            feet_rect.y += 1  # One pixel below player
            on_platform = any(feet_rect.colliderect(tile) for tile in floor_tiles)
            if not on_platform:
                falling = True



        # Simulate falling by scrolling upward
        if falling and not on_floor:
            # Check collision with any floor tile
            player_feet = player.copy()
            player_feet.y += 1
            for tile in floor_tiles:
                if player_feet.colliderect(tile.move(0, -camera_offset)):
                    on_floor = True
                    print("You landed on the floor! Press E to leave.")
                    break
            else:
                camera_offset += scroll_speed


        # --- DRAW EVERYTHING ---
        tmx.draw(win, pygame.Vector2(0, camera_offset))
        tmx.draw_texts(win, pygame.Vector2(0, camera_offset))
        
        # Check collision with obstacles
        for obs in obstacles:
            obs_screen = obs.copy()
            obs_screen.y -= camera_offset
            if player.colliderect(obs_screen):
                print("You hit an obstacle. Game over!")
                quest_result = "lose"
                run = False

        # Draw player
        pygame.draw.rect(win, PLAYER_COLOR, player)

        # Win condition
        if on_floor and keys[pygame.K_e]:
            print("You completed the quest!")
            quest_result = "win"
            run = False

        pygame.display.update()

    return quest_result


def play_second_quest():
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Mouse!")

    WALL_COLOR = (0, 0, 255)
    DOT_COLOR = (255, 255, 255)
    PLAYER_COLOR = (255, 255, 0)
    GHOST1_COLOR = (255, 0, 0)
    GHOST2_COLOR = (255, 105, 180)

    maze = [
        "WWWWWWWWWWWWWWWWWWW",
        "W....            .W",
        "W.W     W   W     W",
        "W.WW W   WW WW    W",
        "W....     ....    W",
        "W.WW WW       W  WW",
        "W.       W        W",
        "W.WW      W       W",
        "W     ..     .    W",
        "W   W   WW WW .   W",
        "WWWWWWWWWWWWWWWWWWW"
    ]


    ROWS = len(maze)
    COLS = len(maze[0])
    maze_width = COLS * TILE_SIZE
    maze_height = ROWS * TILE_SIZE

    draw_offset_x = 97 # higher = more right
    draw_offset_y = 225 # higher = more down

    background = pygame.image.load("resources/quest2/quest2screen.png").convert()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    walls = []
    points = []
    ghosts = []

    for y, row in enumerate(maze):
        for x, char in enumerate(row):
            px = draw_offset_x + x * TILE_SIZE
            py = draw_offset_y + y * TILE_SIZE

            if char == 'W':
                walls.append(pygame.Rect(px, py, TILE_SIZE, TILE_SIZE))
            elif char == '.':
                points.append(pygame.Rect(px + TILE_SIZE // 4, py + TILE_SIZE // 4, TILE_SIZE // 2, TILE_SIZE // 2))
            elif char == 'G':
                ghosts.append(pygame.Rect(px, py, TILE_SIZE, TILE_SIZE))

    player = pygame.Rect(draw_offset_x + TILE_SIZE, draw_offset_y + TILE_SIZE, TILE_SIZE, TILE_SIZE)

    ghost = ghosts[0] if len(ghosts) > 0 else pygame.Rect(draw_offset_x + (COLS - 2) * TILE_SIZE, draw_offset_y + (ROWS - 2) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    ghost2 = ghosts[1] if len(ghosts) > 1 else pygame.Rect(draw_offset_x + TILE_SIZE * (COLS - 3), draw_offset_y + TILE_SIZE, TILE_SIZE, TILE_SIZE)

    clock = pygame.time.Clock()
    run = True
    quest_result = None
    game_started = False
    ghost_move_timer = 0
    ghost_move_interval = 2

    def can_move(rect, ignore_ghost=None):
        # Check walls and screen bounds as before
        if rect.left < draw_offset_x or rect.right > draw_offset_x + maze_width:
            return False
        if rect.top < draw_offset_y or rect.bottom > draw_offset_y + maze_height:
            return False
        if any(rect.colliderect(w) for w in walls):
            return False
        # Prevent collision with the other ghost
        if ignore_ghost != ghost and rect.colliderect(ghost):
            return False
        if ignore_ghost != ghost2 and rect.colliderect(ghost2):
            return False
        return True

    def move(rect, dx, dy, ignore_ghost=None):
        new_rect = rect.move(dx * TILE_SIZE, dy * TILE_SIZE)
        if can_move(new_rect, ignore_ghost):
            rect.x = new_rect.x
            rect.y = new_rect.y


    def ghost_chase(ghost_rect, ignore_ghost=None):
        start = ((ghost_rect.x - draw_offset_x) // TILE_SIZE, (ghost_rect.y - draw_offset_y) // TILE_SIZE)
        goal = ((player.x - draw_offset_x) // TILE_SIZE, (player.y - draw_offset_y) // TILE_SIZE)
        queue = deque([(start, [])])
        visited = set()

        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == goal:
                if path:
                    dx, dy = path[0]
                    move(ghost_rect, dx, dy, ignore_ghost)
                return
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 'W' and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path+[(dx, dy)]))


            while queue:
                (x, y), path = queue.popleft()
                if (x, y) == goal:
                    if path:
                        dx, dy = path[0]
                        move(ghost_rect, dx, dy)
                    return
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 'W' and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(((nx, ny), path+[(dx, dy)]))

            # If no path found, ghost does not move this turn (safe fallback)

    while run:
        clock.tick(8)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quest_result = "quit"

        keys = pygame.key.get_pressed()
        if not game_started and keys[pygame.K_SPACE]:
            game_started = True

        if game_started:
            if keys[pygame.K_a]:
                move(player, -1, 0)
            if keys[pygame.K_d]:
                move(player, 1, 0)
            if keys[pygame.K_w]:
                move(player, 0, -1)
            if keys[pygame.K_s]:
                move(player, 0, 1)

            ghost_move_timer += 1
            if ghost_move_timer >= ghost_move_interval:
                ghost_chase(ghost, ignore_ghost=ghost)
                ghost_chase(ghost2, ignore_ghost=ghost2)

                ghost_move_timer = 0

            points = [p for p in points if not player.colliderect(p)]

            if not points:
                print("You Win!")
                quest_result = "win"
                run = False

            if player.colliderect(ghost):
                print("Caught by Ghost! You Lose.")
                quest_result = "lose"
                run = False

            if player.colliderect(ghost2):
                print("Caught by Second Ghost! You Lose.")
                quest_result = "lose"
                run = False

        win.blit(background, (0, 0))

        for wall in walls:
            pygame.draw.rect(win, WALL_COLOR, wall)
        for p in points:
            pygame.draw.rect(win, DOT_COLOR, p)

        pygame.draw.rect(win, PLAYER_COLOR, player)
        pygame.draw.rect(win, GHOST1_COLOR, ghost)
        pygame.draw.rect(win, GHOST2_COLOR, ghost2)

        pygame.display.update()

    return quest_result

def play_third_quest():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Stealth Heist")
    FPS = 60

    tmx = TileMap("resources/mazemap2.tmx")

    player = None
    exit_rects = []
    npcs = []
    walls = tmx.floor_rects 

    for obj in tmx.interactables:
        if obj["type"].lower() == "spawn":
            PLAYER_SIZE = 32  # or any value you want
            player = pygame.Rect(obj["rect"].x, obj["rect"].y, PLAYER_SIZE, PLAYER_SIZE)
        elif obj["type"].lower() == "exit":
            exit_rects.append(obj["rect"])
        elif obj["type"].lower() == "npc":
            print("Raw NPC object:", obj)  # <-- Add this line
            props = obj.get("properties", {})
            patrol_tiles = int(props.get("patrol_length", props.get("patrol length", 1)))
            direction = props.get("direction", "horizontal").lower()
            start_dir = props.get("start_direction", "right").lower()

            print(f"NPC {obj.get('name', f'npc{len(npcs)+1}')}: direction={direction}, patrol_range={patrol_tiles}, start_direction={start_dir}")

            npc = {
                "name": obj.get("name", f"npc{len(npcs)+1}"),
                "rect": pygame.Rect(obj["rect"].x, obj["rect"].y, TILE_SIZE, TILE_SIZE),
                "origin": (obj["rect"].x, obj["rect"].y),
                "axis": direction,
                "direction": 1 if start_dir in ("right", "down") else -1,
                "patrol_range": patrol_tiles * TILE_SIZE,
                "speed": 1,
                "start_direction": start_dir
            }
            npcs.append(npc)

    print("Player spawn:", player)
    print("Exits loaded:", exit_rects)
    print("NPCs loaded:", npcs)

    for i, npc in enumerate(npcs):
        print(f"{npc['name']}: pos={npc['rect'].topleft}, axis={npc['axis']}, patrol_range={npc['patrol_range']}, direction={npc['direction']}")

    def move_player(rect, dx, dy):
        next_rect = rect.move(dx, dy)
        if not any(next_rect.colliderect(w) for w in walls):
            rect.x += dx
            rect.y += dy

    def update_player():
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a]: dx = -TILE_SIZE // 6
        if keys[pygame.K_d]: dx = TILE_SIZE // 6
        if keys[pygame.K_w]: dy = -TILE_SIZE // 6
        if keys[pygame.K_s]: dy = TILE_SIZE // 6
        if dx or dy:
            move_player(player, dx, dy)

    def is_wall_blocking(npc_rect, player_rect, axis):
        # Use center points for raycast
        start = npc_rect.center
        end = player_rect.center

        # Number of steps for the ray (higher = more accurate)
        steps = int(max(abs(end[0] - start[0]), abs(end[1] - start[1])) // 4)
        if steps == 0:
            return False  # Same position

        for i in range(steps + 1):
            t = i / steps
            x = int(start[0] + (end[0] - start[0]) * t)
            y = int(start[1] + (end[1] - start[1]) * t)
            point_rect = pygame.Rect(x, y, 4, 4)  # Small box for collision
            if any(point_rect.colliderect(w) for w in walls):
                return True  # Wall blocks vision
        return False  # No wall blocks vision

    def npc_vision_rect(npc):
        rect = npc["rect"]
        direction = npc["direction"]
        length = TILE_SIZE * 5  # Vision length (how far the NPC can see)
        width = TILE_SIZE       # Vision width (same as NPC width)
        if npc["axis"] == "horizontal":
            x = rect.right if direction > 0 else rect.left - length
            return pygame.Rect(x, rect.centery - width // 2, length, width)
        else:
            y = rect.bottom if direction > 0 else rect.top - length
            return pygame.Rect(rect.centerx - width // 2, y, width, length)

    def update_npcs():
        for npc in npcs:
            rect = npc["rect"]
            axis = npc["axis"]
            speed = npc["speed"]
            dir = npc["direction"]
            ox, oy = npc["origin"]

            if axis == "horizontal":
                rect.x += dir * speed
                if abs(rect.x - ox) >= npc["patrol_range"]:
                    npc["direction"] *= -1
            else:
                rect.y += dir * speed
                if abs(rect.y - oy) >= npc["patrol_range"]:
                    npc["direction"] *= -1

            vis = npc_vision_rect(npc)
            if vis.colliderect(player) and not is_wall_blocking(rect, player, "x" if axis == "horizontal" else "y"):
                print(f"{npc['rect']} spotted the player!")
                return "lose"
        return None

    def draw():
        screen.fill(BLACK)
        # Draw all tile layers from the map
        tmx.draw(screen, pygame.Vector2(0, 0))

        # Draw player
        pygame.draw.rect(screen, WHITE, player)

        # Draw NPCs and their vision
        for npc in npcs:
            pygame.draw.rect(screen, RED, npc["rect"])
            pygame.draw.rect(screen, MAGENTA, npc_vision_rect(npc), 2)

        # Draw any map texts
        tmx.draw_texts(screen, pygame.Vector2(0, 0))
        pygame.display.flip()

    # Game loop
    result = None
    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        update_player()
        npc_result = update_npcs()
        if npc_result == "lose":
            result = "lose"
            break
        if any(player.colliderect(exit_rect) for exit_rect in exit_rects):
            result = "win"
            break
        draw()

    return result

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
            max_combo_rect = max_combo_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 65))
            win.blit(max_combo_text, max_combo_rect)
            
            quit_text = font_medium.render(f"Press E to return", True, (255, 255, 255))
            quit_rect = max_combo_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
            win.blit(quit_text, quit_rect)
            
            quest_result = 'win'
            
            if k[pygame.K_e]:
                run = False
            
        
        pygame.display.update()
        clock.tick(FPS)
    return quest_result
