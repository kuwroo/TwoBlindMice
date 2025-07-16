import pygame
import random
from misc import SCREEN_WIDTH as WIDTH, SCREEN_HEIGHT as HEIGHT, TILE_SIZE
from collections import deque
from tilemap import TileMap
from spritesheet_loader import SpriteSheet
from colours import *


def play_first_quest():
    # Initialize Pygame and set up the window
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Rabbit-hole!")

    # --- PLAYER ---
    player_size = 30
    player_x = WIDTH // 2
    player_y = HEIGHT // 2
    player = pygame.Rect(player_x, player_y, player_size, player_size)
    player_speed = 7
    scroll_speed = 8

    # --- STARTING PLATFORM ---
    platform_width = WIDTH
    platform_height = 20
    platform_x = player_x - platform_width // 2
    platform_y = player_y + player_size  # just below player
    platform = pygame.Rect(platform_x, platform_y, platform_width, platform_height)

    # Adjust player to stand directly on the platform
    player.bottom = platform.top

    # --- OBSTACLES ---
    obstacles = []
    obstacle_height = 20
    gap = 200
    start_offset = 750  # moved further down
    num_obstacles = 10

    for i in range(num_obstacles):
        obstacle_width = random.randint(70, 200)
        x = random.randint(0, WIDTH - obstacle_width)
        y = i * gap + start_offset
        obstacles.append(pygame.Rect(x, y, obstacle_width, obstacle_height))

    ground_height = 30
    ground_y = num_obstacles * gap + start_offset
    ground = pygame.Rect(0, ground_y, WIDTH, ground_height)

    # Game Loop variables
    camera_offset = 0
    clock = pygame.time.Clock()
    run = True
    quest_result = None
    on_ground = False
    falling = False  # player must press SPACE to start falling

    while run:
        clock.tick(60) # game timing
        win.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quest_result = "quit"

        # Input handling
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player.left > 0:
            player.x -= player_speed
        if keys[pygame.K_d] and player.right < WIDTH:
            player.x += player_speed

        if not falling and keys[pygame.K_SPACE]:
            falling = True  # start fall when SPACE is pressed 

        if falling and not on_ground:
            if ground.top - camera_offset <= player.bottom:
                on_ground = True
                print("You landed safely! Press E to return.")
            else:
                camera_offset += scroll_speed # game mechanics

        # --- DRAW OBSTACLES ---
        for obs in obstacles:
            draw_rect = obs.copy()
            draw_rect.y -= camera_offset
            pygame.draw.rect(win, RED, draw_rect)
            if player.colliderect(draw_rect):
                print("Game Over!")
                quest_result = "lose"
                run = False

        # --- DRAW GROUND ---
        draw_ground = ground.copy()
        draw_ground.y -= camera_offset
        pygame.draw.rect(win, GREEN, draw_ground)

        # --- DRAW STARTING PLATFORM ---
        draw_platform = platform.copy()
        draw_platform.y -= camera_offset
        pygame.draw.rect(win, BROWN, draw_platform)

        # --- INTERACT AFTER LANDING ---
        if on_ground and keys[pygame.K_e]:
            quest_result = "win"
            run = False

        # --- DRAW PLAYER ---
        pygame.draw.rect(win, PLAYER_COLOR, player)
        pygame.display.update()

    return quest_result

def play_second_quest():

    # Initialize Pygame and set up the window
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Mouse!")
    tile = SpriteSheet("resources\\ROUNDBRICKS.png")
    wall_image = tile.get_frame(0, 32, 32)
    tube = SpriteSheet("resources\\tube.jpg")
    tube_image = tube.get_frame(0, 32, 32)

    # --- MAP ---
    maze = [
        "WWWWWWWWWWWWWWWWWWW",
        "W..    WW      .  W",
        "W.WW W   WW WW W  W",
        "W.W   ..    WW W  W",
        "W.W WWW WWW   W W W",
        "W..  W   W W W    W",
        "W WWWWWWWWW WWWWW W",
        "W     W     W     W",
        "W WWW W WWW W WWW W",
        "W W      W      W W",
        "W WWWWWWW WWWWWWW W",
        "W   .  W   W     .W",
        "W WWW W WWW WWWWW W",
        "W   W   ..   W    W",
        "W..   WWWW    ..  W",
        "WWWWWWWWWWWWWWWWWWW"
        ]

    ROWS = len(maze)
    COLS = len(maze[0])
    maze_width = COLS * TILE_SIZE
    maze_height = ROWS * TILE_SIZE
    draw_offset_x = (WIDTH - maze_width) // 2
    draw_offset_y = (HEIGHT - maze_height) // 2 

    # Parse maze
    walls = []
    points = []
    for y, row in enumerate(maze):
        for x, char in enumerate(row):
            if char == 'W':
                walls.append(pygame.Rect(draw_offset_x + x * TILE_SIZE, draw_offset_y + y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif char == '.':
                points.append(pygame.Rect(
                    draw_offset_x + x * TILE_SIZE + TILE_SIZE // 4,
                    draw_offset_y + y * TILE_SIZE + TILE_SIZE // 4,
                    TILE_SIZE // 2, TILE_SIZE // 2))

    # --- PLAYER ---
    player = pygame.Rect(draw_offset_x + TILE_SIZE, draw_offset_y + TILE_SIZE, TILE_SIZE, TILE_SIZE)

    # Ghost
    ghost = pygame.Rect(draw_offset_x + (COLS - 2) * TILE_SIZE, draw_offset_y + (ROWS - 2) * TILE_SIZE, TILE_SIZE, TILE_SIZE)
    ghost2 = pygame.Rect(draw_offset_x + TILE_SIZE * (COLS - 3), draw_offset_y + TILE_SIZE, TILE_SIZE, TILE_SIZE)

    clock = pygame.time.Clock()
    run = True
    quest_result = None
    game_started = False


    def move(rect, dx, dy):
        new_rect = rect.move(dx * TILE_SIZE, dy * TILE_SIZE)
        if all(not new_rect.colliderect(w) for w in walls):
            rect.x += dx * TILE_SIZE
            rect.y += dy * TILE_SIZE

    def ghost_chase(ghost_rect):
        start = ((ghost_rect.x - draw_offset_x) // TILE_SIZE, (ghost_rect.y - draw_offset_y) // TILE_SIZE)
        goal = ((player.x - draw_offset_x) // TILE_SIZE, (player.y - draw_offset_y) // TILE_SIZE)
        queue = deque([(start, [])])
        visited = set()

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
        
                    
    while run:
        clock.tick(5)
        for y in range(0, HEIGHT, 32):
            for x in range(0, WIDTH, 32):
                win.blit(wall_image, (x, y))

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

            # Ghost moves
            ghost_chase(ghost)
            ghost_chase(ghost2)

            # Check collision with points
            points = [p for p in points if not player.colliderect(p)]

            # Win condition
            if not points:
                print("You Win!")
                quest_result = "win"
                run = False

            # Lose condition
            if player.colliderect(ghost):
                print("Caught by Ghost! You Lose.")
                quest_result = "lose"
                run = False
            
            if player.colliderect(ghost2):
                print("Caught by Second Ghost! You Lose.")
                quest_result = "lose"
                run = False

        # Draw maze
        for wall in walls:
            # pygame.draw.rect(win, BLUE, wall)
            win.blit(tube_image, wall.topleft)

        for p in points:
            pygame.draw.rect(win, WHITE, p)

        pygame.draw.rect(win, YELLOW, player)
        pygame.draw.rect(win, RED, ghost)
        pygame.draw.rect(win, (255, 105, 180), ghost2)  

        pygame.display.update()

    return quest_result


def play_third_quest():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    pygame.display.set_caption("Stealth Heist")
    FPS = 60

    tmx = TileMap("resources/mazemap.tmx")

    player = None
    exit_rects = []
    walls = []
    npcs = []

    for obj in tmx.interactables:
        if obj["type"].lower() == "wall":
            walls.append(obj["rect"])
        elif obj["type"].lower() == "spawn":
            PLAYER_SIZE = 32  # or any value you want
            player = pygame.Rect(obj["rect"].x, obj["rect"].y, PLAYER_SIZE, PLAYER_SIZE)
        elif obj["type"].lower() == "exit":
            exit_rects.append(obj["rect"])
        elif obj["type"].lower() == "npc":
            print("Raw NPC object:", obj)  # <-- Add this line
            props = {p["name"]: p["value"] for p in obj.get("properties", [])}
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

    print("Walls loaded:", walls)
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

    pygame.quit()
    return result

