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
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Cheese Heist!")
    clock = pygame.time.Clock()

    tmx_data = TileMap("resources/mazemap.tmx")
    FPS = 60
    PLAYER_SPEED = TILE_SIZE // 6

    # Assets
    player_img = pygame.Surface((TILE_SIZE, TILE_SIZE)); player_img.fill(WHITE)
    npc_img = pygame.Surface((TILE_SIZE, TILE_SIZE)); npc_img.fill(RED)
    cheese_img = pygame.Surface((TILE_SIZE, TILE_SIZE)); cheese_img.fill(YELLOW)

    # Game state
    walls, exits, npcs = [], [], []
    player, cheese = None, None
    got_cheese = False
    quest_result = None
    run = True

    # Load objects
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
                movement_type = obj.properties.get("movement_type", "vertical")  # Default to vertical
                npcs.append({
                    "rect": pygame.Rect(int(obj.x), int(obj.y), TILE_SIZE, TILE_SIZE),
                    "name": obj.name,
                    "movement": movement_type,
                    "start_x": obj.x,
                    "start_y": obj.y,
                    "radius": obj.properties.get("radius", 2) * TILE_SIZE,
                    "direction": 1,
                    "timer": 0,
                    "flip_interval": obj.properties.get("flip_interval", 2000),
                    "speed": obj.properties.get("speed", TILE_SIZE // 32)
                })


    # Abstracted functions
    def handle_events():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def move(rect, dx, dy):
        next_rect = rect.move(dx, dy)
        if all(not next_rect.colliderect(w) for w in walls):
            rect.x += dx
            rect.y += dy

    def update_player():
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a]: dx = -PLAYER_SPEED
        if keys[pygame.K_d]: dx = PLAYER_SPEED
        if keys[pygame.K_w]: dy = -PLAYER_SPEED
        if keys[pygame.K_s]: dy = PLAYER_SPEED
        if dx or dy:
            move(player, dx, dy)
    
    # helper functions for NPCs
    def is_wall_blocking_vision(npc_rect, player_rect, walls, axis):
        if axis == "x":
            min_x = min(npc_rect.centerx, player_rect.centerx)
            max_x = max(npc_rect.centerx, player_rect.centerx)
            scan_box = pygame.Rect(min_x, npc_rect.centery - 5, max_x - min_x, 10)
        else:
            min_y = min(npc_rect.centery, player_rect.centery)
            max_y = max(npc_rect.centery, player_rect.centery)
            scan_box = pygame.Rect(npc_rect.centerx - 5, min_y, 10, max_y - min_y)

        for wall in walls:
            if scan_box.colliderect(wall):
                return True
        return False

    def move_npc_horizontal(npc):
        rect = npc["rect"]
        speed = npc["speed"]
        start_x = npc["start_x"]
        radius = npc["radius"]

        rect.x += npc["direction"] * speed
        if abs(rect.x - start_x) > radius:
            npc["direction"] *= -1

    def move_npc_vertical(npc):
        rect = npc["rect"]
        speed = npc["speed"]
        start_y = npc["start_y"]
        radius = npc["radius"]

        rect.y += npc["direction"] * speed
        if abs(rect.y - start_y) > radius:
            npc["direction"] *= -1

    def update_npc_direction_timer(npc, dt):
        npc["timer"] += dt
        if npc["timer"] >= npc["flip_interval"]:
            npc["direction"] *= -1
            npc["timer"] = 0

    def npc_can_see_player(npc, player, walls):
        vision_rect = get_npc_vision_rect(npc)

        if not vision_rect.colliderect(player):
            return False  # Player not in vision cone

        axis = "x" if npc["movement"] == "horizontal" else "y"
        return not is_wall_blocking_vision(npc["rect"], player, walls, axis)
    
    def get_npc_vision_rect(npc):
        rect = npc["rect"]
        direction = npc["direction"]
        movement = npc["movement"]
        vision_length = TILE_SIZE * 5
        vision_width = TILE_SIZE * 2

        if movement == "horizontal":
            vision_rect = pygame.Rect(
                rect.centerx,
                rect.centery - vision_width // 2,
                vision_length * direction,
                vision_width
            )
        else:  # vertical
            vision_rect = pygame.Rect(
                rect.centerx - vision_width // 2,
                rect.centery,
                vision_width,
                vision_length * direction
            )

        vision_rect.normalize()
        return vision_rect

    def update_npcs(dt, npcs, player, walls):
        for npc in npcs:
            update_npc_direction_timer(npc, dt)

            if npc["movement"] == "horizontal":
                move_npc_horizontal(npc)
            else:
                move_npc_vertical(npc)

            if npc_can_see_player(npc, player, walls):
                print(f"{npc['name']} spotted the player!")
                return "lose"
        return None

    def check_game_conditions():
        nonlocal got_cheese, quest_result, run, cheese
        if cheese and player.colliderect(cheese):
            got_cheese = True
            cheese = None
        if got_cheese and any(player.colliderect(e) for e in exits):
            print("You escaped undetected!")
            quest_result = "win"
            return False
        return True

    def draw_game():
        screen.fill(BLACK)
        for layer in tmx_data.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, surf in layer.tiles():
                    screen.blit(surf, (x * TILE_SIZE, y * TILE_SIZE))
        for e in exits: pygame.draw.rect(screen, GREEN, e)
        if cheese: screen.blit(cheese_img, cheese)
        screen.blit(player_img, player)
        for npc in npcs:
            screen.blit(npc_img, npc["rect"])

            # draw path
            if npc["movement"] == "horizontal":
                patrol = pygame.Rect(
                    npc["start_x"] - npc["radius"],
                    npc["start_y"],
                    npc["radius"] + TILE_SIZE,
                    TILE_SIZE
                )
            else:  # vertical
                patrol = pygame.Rect(
                    npc["start_x"],
                    npc["start_y"] - npc["radius"],
                    TILE_SIZE,
                    npc["radius"] + TILE_SIZE
                )


            pygame.draw.rect(screen, CYAN, patrol, 1)

            vision = get_npc_vision_rect(npc)
            pygame.draw.rect(screen, (150, 100, 255), vision, 2)
        pygame.display.update()

    # --- Main Game Loop ---
    while run:
        dt = clock.tick(FPS)
        run = handle_events()
        update_player()

        npc_result = update_npcs(dt, npcs, player, walls)
        if npc_result == "lose":
            quest_result = "lose"
            break

        run = run and check_game_conditions()
        draw_game()
        
    return quest_result

play_third_quest()