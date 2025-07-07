import pygame
import random
from misc import SCREEN_WIDTH as WIDTH, SCREEN_HEIGHT as HEIGHT, TILE_SIZE
import sys
from collections import deque
from tilemap import TileMap

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PLAYER_COLOR = (0, 0, 255)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)
CYAN = (50, 255, 255)
PURPLE = (180, 50, 255)


def play_first_quest():
    # Initialize Pygame and set up the window
    pygame.init()
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fall Without Hitting")

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

    # --- MAP ---
    maze = [
    "WWWWWWWWWWWW",
    "W..      ..W",
    "W.WW WW WW.W",
    "W.W  ..  W.W",
    "W.W WW W W W",
    "W.. W  W  .W",
    "WWWWWWWWWWWW"
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

    clock = pygame.time.Clock()
    run = True
    quest_result = None
    game_started = False


    def move(rect, dx, dy):
        new_rect = rect.move(dx * TILE_SIZE, dy * TILE_SIZE)
        if all(not new_rect.colliderect(w) for w in walls):
            rect.x += dx * TILE_SIZE
            rect.y += dy * TILE_SIZE

    def ghost_chase():
        start = ((ghost.x - draw_offset_x) // TILE_SIZE, (ghost.y - draw_offset_y) // TILE_SIZE)
        goal = ((player.x - draw_offset_x) // TILE_SIZE, (player.y - draw_offset_y) // TILE_SIZE)
        queue = deque([(start, [])])
        visited = set()

        while queue:
            (x, y), path = queue.popleft()
            if (x, y) == goal:
                if path:
                    dx, dy = path[0]
                    move(ghost, dx, dy)
                return
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < COLS and 0 <= ny < ROWS and maze[ny][nx] != 'W' and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append(((nx, ny), path+[(dx, dy)]))


    while run:
        clock.tick(5)
        win.fill(BLACK)

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
            ghost_chase()

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

        # Draw maze
        for wall in walls:
            pygame.draw.rect(win, BLUE, wall)
        for p in points:
            pygame.draw.rect(win, WHITE, p)

        pygame.draw.rect(win, YELLOW, player)
        pygame.draw.rect(win, RED, ghost)

        pygame.display.update()

    return quest_result


def play_third_quest():
    FPS = 60
    PLAYER_SPEED = TILE_SIZE // 8 
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cheese Heist!")
    clock = pygame.time.Clock()

    tmx_data = TileMap("resources/mazemap.tmx")

    # Assets
    player_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    player_img.fill(WHITE)
    npc_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    npc_img.fill(RED)
    cheese_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    cheese_img.fill(YELLOW)

    # Game objects
    walls = []
    exits = []
    npcs = []
    cheese = None
    player = None

    for group in tmx_data.tmx_data.objectgroups:
        for obj in group:
            rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
            if obj.type == "wall" and obj.properties.get("collidable", False):
                walls.append(rect)
            elif obj.type == "player_spawn":
                player = pygame.Rect(obj.x, obj.y, TILE_SIZE, TILE_SIZE)
            elif obj.type == "cheese":
                cheese = rect
            elif obj.type == "exit":
                exits.append(rect)
            elif obj.type == "npc_patrol":
                npcs.append({
                    "rect": pygame.Rect(obj.x, obj.y, TILE_SIZE, TILE_SIZE),
                    "start_y": obj.y,
                    "radius": obj.properties.get("radius", 2) * TILE_SIZE,
                    "direction": 1,
                    "timer": 0,
                    "flip_interval": 2000,  # ms between direction flip
                })

    got_cheese = False
    spotted = False
    quest_result = None
    run = True

    def move(rect, dx, dy):
        next_rect = rect.move(dx, dy)
        if all(not next_rect.colliderect(w) for w in walls):
            rect.x += dx
            rect.y += dy

    while run:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a]: dx = -PLAYER_SPEED
        if keys[pygame.K_d]: dx = PLAYER_SPEED
        if keys[pygame.K_w]: dy = -PLAYER_SPEED
        if keys[pygame.K_s]: dy = PLAYER_SPEED
        if dx or dy:
            move(player, dx, dy)

# ...existing code...
        # --- NPC Logic ---
        for npc in npcs:
            npc_rect = npc["rect"]
            npc["timer"] += dt
            if npc["timer"] >= npc["flip_interval"]:
                npc["direction"] *= -1
                npc["timer"] = 0

            # Patrol move (up/down)
            move(npc_rect, 0, npc["direction"])
            if abs(npc_rect.y - npc["start_y"]) > npc["radius"]:
                npc_rect.y = npc["start_y"]
                npc["direction"] *= -1

            # Line of sight (simplified vertical scan)
            if abs(npc_rect.centerx - player.centerx) < TILE_SIZE:
                vision_rect = pygame.Rect(
                    npc_rect.centerx,
                    npc_rect.centery,
                    1,
                    TILE_SIZE * 5 * npc["direction"]
                )
                vision_rect.normalize()
                blocked = any(w.colliderect(vision_rect) for w in walls)
                if vision_rect.colliderect(player) and not blocked:
                    print("You were spotted!")
                    quest_result = "lose"
                    run = False
                    break  # Immediately end the loop and quest

        # --- Game Logic ---
        if cheese and player.colliderect(cheese):
            got_cheese = True
            cheese = None

        if got_cheese and any(player.colliderect(exit_rect) for exit_rect in exits):
            print("You escaped undetected!")
            quest_result = "win"
            run = False

        # --- Drawing ---
        screen.fill(BLACK)

        for layer in tmx_data.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, surf in layer.tiles():
                    screen.blit(surf, (x * TILE_SIZE, y * TILE_SIZE))

        for wall in walls:
            pygame.draw.rect(screen, BLUE, wall)

        for exit_rect in exits:
            pygame.draw.rect(screen, GREEN, exit_rect)

        if cheese:
            screen.blit(cheese_img, cheese)

        screen.blit(player_img, player)

        for npc in npcs:
            screen.blit(npc_img, npc["rect"])
            # Draw patrol zone
            patrol_line = pygame.Rect(
                npc["rect"].x,
                npc["start_y"] - npc["radius"],
                TILE_SIZE,
                npc["radius"] * 2
            )
            pygame.draw.rect(screen, CYAN, patrol_line, 1)
            # Draw vision line
            vision = pygame.Rect(
                npc["rect"].centerx,
                npc["rect"].centery,
                1,
                TILE_SIZE * 5 * npc["direction"]
            )
            vision.normalize()
            pygame.draw.rect(screen, (150, 100, 255), vision, 1)

        pygame.display.update()

    return quest_result

play_third_quest()