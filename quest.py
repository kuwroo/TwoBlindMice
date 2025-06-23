import pygame
import random
from misc import SCREEN_WIDTH as WIDTH, SCREEN_HEIGHT as HEIGHT, TILE_SIZE
import sys
from collections import deque

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PLAYER_COLOR = (0, 0, 255)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)

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
    "W.W      W.W",
    "W.W WW W W.W",
    "W.. W  W ..W",
    "WWWWWWWWWWWW"
    ]

    ROWS = len(maze)
    COLS = len(maze[0])

    # Parse maze
    walls = []
    points = []
    for y, row in enumerate(maze):
        for x, char in enumerate(row):
            if char == 'W':
                walls.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            elif char == '.':
                points.append(pygame.Rect(x * TILE_SIZE + TILE_SIZE//4, y * TILE_SIZE + TILE_SIZE//4, TILE_SIZE//2, TILE_SIZE//2))

    # --- PLAYER ---
    player = pygame.Rect(TILE_SIZE, TILE_SIZE, TILE_SIZE, TILE_SIZE)

    # Ghost
    ghost = pygame.Rect((COLS - 2) * TILE_SIZE, (ROWS - 2) * TILE_SIZE, TILE_SIZE, TILE_SIZE)

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
        start = (ghost.x // TILE_SIZE, ghost.y // TILE_SIZE)
        goal = (player.x // TILE_SIZE, player.y // TILE_SIZE)
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



